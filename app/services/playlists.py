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

    # @staticmethod
    # async def create_playlist(
    #     db: Session, name: str, owner_id: int
    # ) -> PlaylistStatusResponse:
    #     """Verifica se a playlist já existe ou cria uma nova."""

    #     existing_playlist = (
    #         db.query(Playlist)
    #         .filter(
    #             Playlist.name == name,
    #             Playlist.owner_id == owner_id,
    #             ~Playlist.system_deleted,
    #         )
    #         .first()
    #     )

    #     if existing_playlist:
    #         count = (
    #             db.query(func.count(PlaylistItem.id))
    #             .filter(PlaylistItem.playlist_id == existing_playlist.id)
    #             .scalar()
    #         )

    #         rprint(
    #             f"[bold yellow]Playlist Recovered:[/bold yellow] {existing_playlist.name}"
    #         )
    #         return PlaylistStatusResponse(
    #             id=existing_playlist.id,
    #             name=existing_playlist.name,
    #             owner_id=existing_playlist.owner_id,
    #             music_count=count or 0,
    #             status="success",
    #             message="Playlist existente recuperada.",
    #         )

    #     try:
    #         db_playlist = Playlist(name=name, owner_id=owner_id)
    #         db.add(db_playlist)
    #         db.commit()
    #         db.refresh(db_playlist)

    #         rprint(f"[bold green]Playlist Created:[/bold green] {db_playlist.name}")
    #         return PlaylistStatusResponse(
    #             id=db_playlist.id,
    #             name=db_playlist.name,
    #             owner_id=db_playlist.owner_id,
    #             music_count=0,
    #             status="success",
    #             message="Nova playlist criada com sucesso.",
    #         )
    #     except Exception as e:
    #         db.rollback()
    #         return PlaylistStatusResponse(status="error", message=str(e))

    # @staticmethod
    # async def get_all_playlists(
    #     db: Session, owner_id: int, skip: int = 0, limit: int = 20
    # ) -> List[PlaylistResponse]:
    #     """Retorna todas as playlists do usuário com paginação"""
    #     playlists = (
    #         db.query(Playlist)
    #         .filter(Playlist.owner_id == owner_id, ~Playlist.system_deleted)
    #         .offset(skip)
    #         .limit(limit)
    #         .all()
    #     )

    #     results = []
    #     for p in playlists:
    #         count = (
    #             db.query(func.count(PlaylistItem.id))
    #             .filter(PlaylistItem.playlist_id == p.id)
    #             .scalar()
    #         )
    #         items = (
    #             db.query(PlaylistItem)
    #             .filter(PlaylistItem.playlist_id == p.id)
    #             .limit(10)
    #             .all()
    #         )
    #         results.append(
    #             PlaylistResponse(
    #                 id=p.id,
    #                 name=p.name,
    #                 owner_id=p.owner_id,
    #                 music_count=count or 0,
    #                 items=items,
    #             )
    #         )
    #     return results

    # @staticmethod
    # async def get_playlist(db: Session, playlist_id: int) -> PlaylistResponse | None:
    #     """Retorna uma playlist específica"""
    #     playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    #     if not playlist:
    #         return None

    #     count = (
    #         db.query(func.count(PlaylistItem.id))
    #         .filter(PlaylistItem.playlist_id == playlist_id)
    #         .scalar()
    #     )
    #     items = (
    #         db.query(PlaylistItem).filter(PlaylistItem.playlist_id == playlist_id).all()
    #     )

    #     return PlaylistResponse(
    #         id=playlist.id,
    #         name=playlist.name,
    #         owner_id=playlist.owner_id,
    #         music_count=count or 0,
    #         items=items,
    #     )

    # @staticmethod
    # async def add_tracks_batch(
    #     db: Session, playlist_name: str, track_names: List[str], owner_id: int
    # ) -> int | None:
    #     """Adiciona múltiplas faixas a uma playlist"""
    #     playlist = (
    #         db.query(Playlist)
    #         .filter(Playlist.name == playlist_name)
    #         .filter(Playlist.owner_id == owner_id)
    #         .first()
    #     )
    #     if not playlist:
    #         return None

    #     added_count = 0
    #     for t_name in track_names:
    #         track = db.query(Track).filter(Track.name == t_name).first()
    #         if not track:
    #             continue
    #         exists = (
    #             db.query(PlaylistItem)
    #             .filter_by(playlist_id=playlist.id, track_id=track.id)
    #             .first()
    #         )
    #         if not exists:
    #             db.add(PlaylistItem(playlist_id=playlist.id, track_id=track.id))
    #             added_count += 1

    #     db.commit()
    #     return added_count

    # @staticmethod
    # async def delete_playlist(
    #     db: Session, name: str, owner_id: int
    # ) -> PlaylistStatusResponse:
    #     """Deleta permanentemente uma playlist do banco de dados pelo nome."""

    #     playlist = (
    #         db.query(Playlist)
    #         .filter(Playlist.name == name, Playlist.owner_id == owner_id)
    #         .first()
    #     )

    #     if not playlist:
    #         return PlaylistStatusResponse(
    #             status="error", message=f"Playlist '{name}' não encontrada."
    #         )

    #     try:
    #         db.delete(playlist)
    #         db.commit()

    #         rprint(f"[bold red]Playlist Deleted:[/bold red] {name}")
    #         return PlaylistStatusResponse(
    #             status="success",
    #             message=f"Playlist '{name}' foi excluída permanentemente.",
    #         )
    #     except Exception as e:
    #         db.rollback()
    #         return PlaylistStatusResponse(
    #             status="error", message=f"Erro ao excluir a playlist: {str(e)}"
    #         )

    # @staticmethod
    # async def get_playlist_tracks(
    #     db: Session, playlist_id: int, skip: int = 0, limit: int = 20
    # ) -> List[Track] | None:
    #     """Retorna as faixas de uma playlist com paginação"""
    #     playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    #     if not playlist:
    #         return None

    #     tracks = (
    #         db.query(Track)
    #         .join(PlaylistItem, Track.id == PlaylistItem.track_id)
    #         .filter(PlaylistItem.playlist_id == playlist_id)
    #         .offset(skip)
    #         .limit(limit)
    #         .all()
    #     )

    #     return tracks

    # @staticmethod
    # async def get_playlist_tracks_by_name(
    #     db: Session, playlist_name: str, owner_id: int
    # ) -> PlaylistTracksResponse:
    #     """Recupera as faixas de uma playlist específica pelo nome"""
    #     playlist = (
    #         db.query(Playlist)
    #         .filter(
    #             Playlist.name == playlist_name,
    #             Playlist.owner_id == owner_id,
    #             ~Playlist.system_deleted,
    #         )
    #         .first()
    #     )
    #     if not playlist:
    #         return PlaylistTracksResponse(
    #             status="error", message="Playlist não encontrada."
    #         )

    #     tracks = (
    #         db.query(Track)
    #         .join(PlaylistItem, Track.id == PlaylistItem.track_id)
    #         .filter(PlaylistItem.playlist_id == playlist.id)
    #         .all()
    #     )

    #     track_list = [
    #         TrackResponse(
    #             id=track.id,
    #             name=track.name,
    #             artist=track.artists,
    #             spotify_id=track.spotify_id,
    #         )
    #         for track in tracks
    #     ]

    #     return PlaylistTracksResponse(status="success", tracks=track_list)

    # @staticmethod
    # async def remove_track_from_playlist(
    #     db: Session, playlist_id: int, track_id: int
    # ) -> bool:
    #     """Remove uma faixa de uma playlist"""
    #     item = (
    #         db.query(PlaylistItem)
    #         .filter(
    #             PlaylistItem.playlist_id == playlist_id,
    #             PlaylistItem.track_id == track_id,
    #         )
    #         .first()
    #     )

    #     if not item:
    #         return False

    #     db.delete(item)
    #     db.commit()
    #     return True
