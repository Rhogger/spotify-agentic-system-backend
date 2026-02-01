from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.track import Track

from app.schemas.tracks import PlaylistTracksMCPResponse, TrackImagesMCPResponse
from app.services.spotify_mcp import SpotifyMCPService
from app.models.user import User
from app.core.logger import logger


class TracksService:
    @staticmethod
    async def get_track_images_mcp(
        user: User,
        db: Session,
        track_ids: list[str],
    ) -> TrackImagesMCPResponse:
        """
        Busca as imagens de capa das tracks via MCP tool getTrackImages.

        Args:
            user: Usuário autenticado com token Spotify
            db: Sessão do banco de dados
            track_ids: Lista de IDs Spotify das tracks

        Returns:
            TrackImagesMCPResponse com o dicionário de imagens
        """
        result_dict = await SpotifyMCPService.call_tool(
            "getTrackImages",
            user,
            db,
            {
                "trackIds": track_ids,
            },
        )
        logger.success("Resposta MCP Track Images", data=result_dict)
        return TrackImagesMCPResponse(**result_dict)

    @staticmethod
    async def get_playlist_tracks_mcp(
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
        logger.success("Resposta MCP Tracks", data=result_dict)
        return PlaylistTracksMCPResponse(**result_dict)

    @staticmethod
    async def search_tracks_fuzzy(
        user: User, db: Session, query: str, limit: int = 5, offset: int = 0
    ):
        """
        Realiza busca fuzzy (aproximada) por nome da música ou artista.
        Requer a extensão pg_trgm habilitada no PostgreSQL.
        """
        search_target = Track.name + " " + Track.artists

        results = (
            db.query(Track)
            .filter(
                text("(tracks.name || ' ' || tracks.artists) % :q").bindparams(q=query)
            )
            .order_by(func.similarity(search_target, query).desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        logger.info(f"Busca fuzzy por '{query}' retornou {len(results)} faixas.")

        if not results:
            return []

        track_ids = [t.spotify_id for t in results]
        try:
            images_resp = await TracksService.get_track_images_mcp(user, db, track_ids)
            images_dict = images_resp.json.images if images_resp.json else {}

            for track in results:
                track.image_url = images_dict.get(track.spotify_id)
        except Exception as e:
            logger.error(f"Erro ao buscar imagens via MCP no fuzzy search: {e}")

        return results
