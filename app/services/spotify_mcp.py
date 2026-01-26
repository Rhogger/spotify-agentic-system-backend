import httpx
from contextlib import asynccontextmanager
from typing import Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from mcp import ClientSession
from mcp.client.sse import sse_client

from app.core.config import settings
from app.models.user import User


class SpotifyMCPService:
    def __init__(self):
        self.server_url = settings.MCP_SERVER_URL

    @asynccontextmanager
    async def connect(self):
        """
        Conecta ao servidor MCP via HTTP (SSE).
        """
        try:
            async with sse_client(self.server_url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    yield session
        except Exception as e:
            print(f"❌ Erro ao conectar no MCP: {e}")
            raise HTTPException(
                status_code=503, detail="Serviço de Agente Spotify indisponível"
            )

    async def _refresh_spotify_token(self, user: User, db: Session) -> str:
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
                    print(f"Erro Spotify Refresh: {resp.text}")
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
                print(f"Erro de conexão no refresh: {e}")
                raise HTTPException(
                    status_code=502,
                    detail="Falha ao conectar com Spotify para renovar token",
                )

    async def list_tools(self):
        """Lista todas as ferramentas disponíveis (sem autenticação)"""
        async with self.connect() as session:
            result = await session.list_tools()
            return result.tools

    async def call_tool(
        self, tool_name: str, user: User, db: Session, arguments: dict = None
    ) -> Any:
        """
        Chama uma ferramenta específica injetando o token do usuário.
        """
        if arguments is None:
            arguments = {}

        token = user.spotify_access_token

        if not token:
            token = await self._refresh_spotify_token(user, db)

        arguments["_accessToken"] = token

        async with self.connect() as session:
            try:
                result = await session.call_tool(tool_name, arguments)

                if result.content and len(result.content) > 0:
                    return result.content[0].text
                return "Sem resposta da ferramenta."

            except Exception as e:
                print(f"Erro na execução da tool {tool_name}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao executar ação no Spotify: {str(e)}",
                )


spotify_mcp = SpotifyMCPService()
