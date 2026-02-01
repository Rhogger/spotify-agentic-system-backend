import asyncio
from io import BytesIO

import colorgram
import httpx
from PIL import Image

from app.models.user import User
from app.schemas.playlists import (
    PlaylistsMCPResponse,
    PlaylistMCPDetailResponse,
)
from app.services.spotify_mcp import SpotifyMCPService
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class PlaylistsService:
    @staticmethod
    async def get_my_playlists_mcp(
        user: User,
        db: Session,
        limit: int = 50,
        offset: int = 0,
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
            {"limit": limit, "offset": offset, "json": json_output, "md": md_output},
        )
        logger.info(
            f"Busca de playlists via MCP concluída. User: {user.email}, Offset: {offset}"
        )

        return PlaylistsMCPResponse(**result_dict)

    @staticmethod
    async def get_playlist_details_mcp(
        user: User,
        db: Session,
        playlist_id: str,
        calculate_duration: bool = False,
    ) -> PlaylistMCPDetailResponse:
        """
        Busca detalhes de uma playlist via MCP, opcionalmente calculando a duração total.
        """
        result_dict = await SpotifyMCPService.call_tool(
            "getPlaylist",
            user,
            db,
            {"playlistId": playlist_id, "calculateTotalDuration": calculate_duration},
        )
        logger.info(f"Detalhes da playlist {playlist_id} via MCP recuperados.")
        if result_dict.get("json") and result_dict["json"].get("image"):
            image_url = result_dict["json"]["image"]
            if image_url and image_url != "No image":
                color = await PlaylistsService.get_dominant_color(image_url)
                if color:
                    result_dict["json"]["primary_color"] = color

        return PlaylistMCPDetailResponse(**result_dict)

    @staticmethod
    async def get_dominant_color(image_url: str) -> str | None:
        """
        Downloads image, resizes it, and extracts dominant color.
        optimized to minimize bandwidth and CPU usage.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=5.0)
                if response.status_code != 200:
                    return None

                content = response.content

            logger.info(f"Extracting dominant color for image: {image_url}")

            def _extract_cpu(img_bytes):
                try:
                    img = Image.open(BytesIO(img_bytes))
                    img.thumbnail((100, 100))

                    if img.mode != "RGB":
                        img = img.convert("RGB")

                    buf = BytesIO()
                    img.save(buf, format="JPEG")
                    buf.seek(0)

                    colors = colorgram.extract(buf, 1)
                    if colors:
                        c = colors[0].rgb
                        return f"#{c.r:02x}{c.g:02x}{c.b:02x}"
                except Exception:
                    return None
                return None

            return await asyncio.to_thread(_extract_cpu, content)
        except Exception:
            return None

    @staticmethod
    async def create_playlist_mcp(
        user: User,
        db: Session,
        name: str,
        description: str | None = None,
        public: bool = False,
    ) -> dict:
        """
        Cria uma nova playlist no Spotify via MCP.
        """
        result_dict = await SpotifyMCPService.call_tool(
            "createPlaylist",
            user,
            db,
            {"name": name, "description": description, "public": public},
        )
        logger.info(f"Playlist '{name}' criada via MCP para user: {user.email}")

        md_response = result_dict.get("md", "")
        playlist_id = None
        playlist_url = None

        if "Playlist ID:" in md_response:
            try:
                playlist_id = md_response.split("Playlist ID:")[1].split("\n")[0].strip()
            except Exception:
                pass

        if "Playlist URL:" in md_response:
            try:
                playlist_url = md_response.split("Playlist URL:")[1].split("\n")[0].strip()
            except Exception:
                pass

        return {
            "success": True,
            "message": f"Playlist '{name}' criada com sucesso.",
            "playlist_id": playlist_id,
            "playlist_url": playlist_url,
        }

    @staticmethod
    async def update_playlist_mcp(
        user: User,
        db: Session,
        playlist_id: str,
        name: str | None = None,
        description: str | None = None,
        public: bool | None = None,
    ) -> dict:
        """
        Atualiza os detalhes de uma playlist no Spotify via MCP.
        """
        args = {"playlistId": playlist_id}
        if name is not None:
            args["name"] = name
        if description is not None:
            args["description"] = description
        if public is not None:
            args["public"] = public

        await SpotifyMCPService.call_tool("updatePlaylistDetails", user, db, args)
        logger.info(f"Playlist {playlist_id} atualizada via MCP para user: {user.email}")

        return {
            "success": True,
            "message": f"Playlist {playlist_id} atualizada com sucesso.",
            "playlist_id": playlist_id,
        }

    @staticmethod
    async def unfollow_playlist_mcp(
        user: User,
        db: Session,
        playlist_id: str,
    ) -> dict:
        """
        Remove uma playlist da biblioteca do usuário via MCP (unfollow).
        Nota: A API do Spotify não permite deletar playlists permanentemente.
        """
        await SpotifyMCPService.call_tool(
            "unfollowPlaylist", user, db, {"playlistId": playlist_id}
        )
        logger.info(
            f"Playlist {playlist_id} removida da biblioteca via MCP para user: {user.email}"
        )

        return {
            "success": True,
            "message": f"Playlist {playlist_id} removida da sua biblioteca.",
            "playlist_id": playlist_id,
        }

    @staticmethod
    async def add_tracks_to_playlist_mcp(
        user: User,
        db: Session,
        playlist_id: str,
        track_ids: list[str],
        position: int | None = None,
    ) -> dict:
        """
        Adiciona tracks a uma playlist via MCP.
        """
        args = {"playlistId": playlist_id, "trackIds": track_ids}
        if position is not None:
            args["position"] = position

        await SpotifyMCPService.call_tool("addTracksToPlaylist", user, db, args)
        logger.info(
            f"{len(track_ids)} tracks adicionadas à playlist {playlist_id} via MCP"
        )

        return {
            "success": True,
            "message": f"{len(track_ids)} track(s) adicionada(s) à playlist.",
            "playlist_id": playlist_id,
        }

    @staticmethod
    async def remove_tracks_from_playlist_mcp(
        user: User,
        db: Session,
        playlist_id: str,
        track_ids: list[str],
        snapshot_id: str | None = None,
    ) -> dict:
        """
        Remove tracks de uma playlist via MCP.
        """
        args = {"playlistId": playlist_id, "trackIds": track_ids}
        if snapshot_id:
            args["snapshotId"] = snapshot_id

        await SpotifyMCPService.call_tool("removeTracksFromPlaylist", user, db, args)
        logger.info(
            f"{len(track_ids)} tracks removidas da playlist {playlist_id} via MCP"
        )

        return {
            "success": True,
            "message": f"{len(track_ids)} track(s) removida(s) da playlist.",
            "playlist_id": playlist_id,
        }