from typing import List
from app.core.database import SessionLocal
from app.schemas.tracks import TrackResponse, TrackFeaturesInput
from app.services.tracks import TracksService


async def filter_tracks_exact(filters: TrackFeaturesInput) -> List[dict]:
    """
    Filtra músicas usando critérios técnicos exatos (features de áudio).
    Requer lógica de range query que é implementada diretamente aqui.

    Args:
        query: O termo de busca (nome da música ou artista).

    Returns:
        Lista de músicas filtradas serializadas via TrackResponse.
    """
    db = SessionLocal()
    try:
        results = await TracksService.filter_tracks_exact(db, filters)

        return [TrackResponse.model_validate(t).model_dump() for t in results]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()


async def search_tracks_fuzzy(query: str) -> List[dict]:
    """
    Busca músicas no banco de dados local por nome ou artista usando busca aproximada (fuzzy search).
    Esta ferramenta reutiliza a lógica do TracksService.

    Args:
        query: O termo de busca (nome da música ou artista).

    Returns:
        Uma lista de dicionários contendo os detalhes das músicas encontradas.
    """
    db = SessionLocal()
    try:
        results = await TracksService.search_tracks_fuzzy(db, query)

        return [TrackResponse.model_validate(t).model_dump() for t in results]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()
