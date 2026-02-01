from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.schemas.tracks import (
    TrackResponse,
    PlaylistTracksMCPResponse,
)
from app.services.tracks import TracksService
from app.models.user import User

from app.core.logger import logger

router = APIRouter()


@router.get("/playlist/{playlist_id}", response_model=PlaylistTracksMCPResponse)
async def get_playlist_tracks_mcp(
    playlist_id: str,
    limit: int = 10,
    offset: int = 0,
    json: bool = True,
    md: bool = True,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Busca faixas de uma playlist via MCP Tool 'getPlaylistTracks'.
    """
    try:
        logger.info(f"Buscando faixas da playlist {playlist_id} via MCP")
        return await TracksService.get_playlist_tracks_mcp(
            current_user, db, playlist_id, limit, offset, json, md
        )
    except Exception as e:
        logger.error(f"Erro ao buscar faixas via MCP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[TrackResponse])
async def search_tracks(
    q: str = Query(..., min_length=1),
    limit: int = 5,
    offset: int = 0,
    db: Session = Depends(deps.get_db),
):
    logger.info(f"Recebendo busca de faixas: '{q}'")
    return await TracksService.search_tracks_fuzzy(db, q, limit, offset)


# @router.post("/filter", response_model=List[TrackResponse])
# async def filter_tracks(
#     filters: TrackFeaturesInput, limit: int = 20, db: Session = Depends(deps.get_db)
# ):
#     return await TracksService.filter_tracks_exact(db, filters, limit)


# @router.get("/{track_id}", response_model=TrackResponse)
# async def get_track(track_id: int, db: Session = Depends(deps.get_db)):
#     track = await TracksService.get_by_id(db, track_id)
#     if not track:
#         raise HTTPException(status_code=404, detail="Música não encontrada")
#     return track
