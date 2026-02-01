from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.track import Track

from app.schemas.tracks import PlaylistTracksMCPResponse
from app.services.spotify_mcp import SpotifyMCPService
from app.models.user import User
from app.core.logger import logger


class TracksService:
    @staticmethod
    async def get_playlist_tracks_mcp(
        user: User,
        db: Session,
        playlist_id: str,
        limit: int = 10,
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

    # @staticmethod
    # async def get_by_id(db: Session, track_id: int):
    #     """Busca uma música pelo ID interno."""
    #     return db.query(Track).filter(Track.id == track_id).first()

    @staticmethod
    async def search_tracks_fuzzy(
        db: Session, query: str, limit: int = 5, offset: int = 0
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
        return results

    # @staticmethod
    # async def filter_tracks_exact(
    #     db: Session, filters: TrackFeaturesInput, limit: int = 5
    # ):
    #     """
    #     Filtra músicas combinando múltiplos critérios exatos de features.
    #     """
    #     query = db.query(Track)

    #     filter_data = filters.model_dump(exclude_unset=True)
    #     for field, value in filter_data.items():
    #         query = query.filter(getattr(Track, field) == value)

    #     return query.limit(limit).all()
