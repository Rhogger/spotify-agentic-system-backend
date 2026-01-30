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
from app.schemas.mcp import PlaylistsMCPResponse, PlaylistTracksMCPResponse


class SpotifyMCPService:
    @staticmethod
    @asynccontextmanager
    async def connect():
        """
        Conecta ao servidor MCP via HTTP (SSE).
        """
        try:
            async with sse_client(settings.MCP_SERVER_URL) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    yield session
        except Exception as e:
            print(f"❌ Erro ao conectar no MCP: {e}")
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

                    for c in result.content:
                        if not hasattr(c, "text"):
                            continue

                        text_content = c.text
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

                    return response_data

                return {"md": "Sem resposta da ferramenta.", "json": None}

            except Exception as e:
                print(f"Erro na execução da tool {tool_name}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao executar ação no Spotify: {str(e)}",
                )

    @staticmethod
    async def get_my_playlists(
        user: User,
        db: Session,
        limit: int = 50,
        json_output: bool = True,
        md_output: bool = True,
    ) -> PlaylistsMCPResponse:
        """
        Helper específico para buscar playlists via MCP.
        """
        result_dict = await SpotifyMCPService.call_tool(
            "getMyPlaylists",
            user,
            db,
            {"limit": limit, "json": json_output, "md": md_output},
        )
        return PlaylistsMCPResponse(**result_dict)

    @staticmethod
    async def get_playlist_tracks(
        user: User,
        db: Session,
        playlist_id: str,
        limit: int = 50,
        offset: int = 0,
        json_output: bool = True,
        md_output: bool = True,
    ) -> PlaylistTracksMCPResponse:
        """
        Helper específico para buscar faixas de uma playlist via MCP.
        """
        result_dict = await SpotifyMCPService.call_tool(
            "getPlaylistTracks",
            user,
            db,
            {
                "playlistId": playlist_id,
                "limit": limit,
                "offset": offset,
                "json": json_output,
                "md": md_output,
            },
        )
        return PlaylistTracksMCPResponse(**result_dict)
