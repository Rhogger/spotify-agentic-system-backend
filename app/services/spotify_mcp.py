import httpx
import json
from contextlib import asynccontextmanager
from typing import Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from mcp import ClientSession
from mcp.client.sse import sse_client

from app.core.config import settings
from app.models.user import User
from app.core.logger import logger


class SpotifyMCPService:
    @staticmethod
    @asynccontextmanager
    async def connect():
        last_error = None
        for attempt in range(3):
            try:
                async with sse_client(settings.MCP_SERVER_URL, timeout=120.0) as (
                    read,
                    write,
                ):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        yield session
                        return
            except Exception as e:
                logger.warning(
                    f"Tentativa {attempt + 1}/3 de conectar ao MCP falhou", data=str(e)
                )
                last_error = e
                import asyncio

                await asyncio.sleep(1 * (attempt + 1))

        logger.error("Erro ao conectar no MCP após 3 tentativas", error=last_error)
        raise HTTPException(
            status_code=503, detail="Serviço de Agente Spotify indisponível"
        )

    @staticmethod
    async def _refresh_spotify_token(user: User, db: Session) -> str:
        """
        Renova o Access Token usando o Refresh Token salvo no banco.
        """
        if not user.spotify_refresh_token:
            raise HTTPException(
                status_code=401,
                detail="Usuário não conectado ao Spotify (sem refresh token)",
            )

        token_url = "https://accounts.spotify.com/api/token"

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    token_url,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": user.spotify_refresh_token,
                        "client_id": settings.SPOTIFY_CLIENT_ID,
                        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                if resp.status_code != 200:
                    logger.error(f"Erro Spotify Refresh: {resp.text}")
                    raise HTTPException(
                        status_code=401,
                        detail="Sessão do Spotify expirada. Faça login novamente.",
                    )

                data = resp.json()
                new_access_token = data["access_token"]

                user.spotify_access_token = new_access_token

                if "refresh_token" in data:
                    user.spotify_refresh_token = data["refresh_token"]

                db.add(user)
                db.commit()
                db.refresh(user)

                return new_access_token

            except httpx.RequestError as e:
                logger.error("Erro de conexão no refresh", error=e)
                raise HTTPException(
                    status_code=502,
                    detail="Falha ao conectar com Spotify para renovar token",
                )

    @staticmethod
    async def list_tools():
        """Lista todas as ferramentas disponíveis (sem autenticação)"""
        async with SpotifyMCPService.connect() as session:
            result = await session.list_tools()
            return result.tools

    @staticmethod
    async def call_tool(
        tool_name: str, user: User, db: Session, arguments: dict = None
    ) -> Any:
        """
        Chama uma ferramenta específica injetando o token do usuário.
        """
        if arguments is None:
            arguments = {}

        token = user.spotify_access_token

        if not token:
            token = await SpotifyMCPService._refresh_spotify_token(user, db)

        arguments["_accessToken"] = token

        async with SpotifyMCPService.connect() as session:
            try:
                result = await session.call_tool(tool_name, arguments)

                if result.content and len(result.content) > 0:
                    response_data = {"md": None, "json": None}
                    error_message = None

                    for c in result.content:
                        if not hasattr(c, "text"):
                            continue

                        text_content = c.text
                        text_stripped = text_content.strip()

                        error_patterns = (
                            "Error:",
                            "Error ",
                            "Failed to",
                            "Unable to",
                            "Cannot ",
                            "Could not",
                        )
                        if text_stripped.startswith(error_patterns):
                            error_message = text_stripped
                            logger.error(
                                f"Erro retornado pela ferramenta {tool_name}",
                                error=error_message,
                            )

                        if text_content.strip().startswith(
                            "{"
                        ) and text_content.strip().endswith("}"):
                            try:
                                response_data["json"] = json.loads(text_content)
                            except json.JSONDecodeError:
                                response_data["json"] = text_content
                        elif text_content.strip().startswith(
                            "["
                        ) and text_content.strip().endswith("]"):
                            try:
                                response_data["json"] = json.loads(text_content)
                            except json.JSONDecodeError:
                                response_data["json"] = text_content
                        else:
                            response_data["md"] = text_content

                    if error_message:
                        raise HTTPException(
                            status_code=400,
                            detail=error_message,
                        )

                    logger.success(
                        f"Resultado da Ferramenta ({tool_name})", data=result.content
                    )

                    return response_data

                return {"md": "Sem resposta da ferramenta.", "json": None}

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Erro na execução da ferramenta {tool_name}", error=e)
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao executar ação no Spotify: {str(e)}",
                )
