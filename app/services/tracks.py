from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.track import Track
from app.schemas.tracks import TrackFeaturesInput


class TracksService:
    @staticmethod
    async def get_by_id(db: Session, track_id: int):
        """Busca uma música pelo ID interno."""
        return db.query(Track).filter(Track.id == track_id).first()

    @staticmethod
    async def search_tracks_fuzzy(
        db: Session, query: str, limit: int = 5, offset: int = 0
    ):
        """
        Realiza busca fuzzy (aproximada) por nome da música ou artista.
        Requer a extensão pg_trgm habilitada no PostgreSQL.
        """
        search_target = Track.name + " " + Track.artists

        return (
            db.query(Track)
            .filter(
                text("(tracks.name || ' ' || tracks.artists) % :q").bindparams(q=query)
            )
            .order_by(func.similarity(search_target, query).desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    @staticmethod
    async def filter_tracks_exact(
        db: Session, filters: TrackFeaturesInput, limit: int = 5
    ):
        """
        Filtra músicas combinando múltiplos critérios exatos de features.
        """
        query = db.query(Track)

        filter_data = filters.model_dump(exclude_unset=True)
        for field, value in filter_data.items():
            query = query.filter(getattr(Track, field) == value)

        return query.limit(limit).all()
