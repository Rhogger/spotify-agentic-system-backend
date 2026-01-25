from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.schemas.tracks import TrackResponse, TrackFeaturesInput
from app.services.tracks import TracksService

router = APIRouter()


@router.get("/search", response_model=List[TrackResponse])
async def search_tracks(
    q: str = Query(..., min_length=1),
    limit: int = 5,
    offset: int = 0,
    db: Session = Depends(deps.get_db),
):
    return await TracksService.search_tracks_fuzzy(db, q, limit, offset)


@router.post("/filter", response_model=List[TrackResponse])
async def filter_tracks(
    filters: TrackFeaturesInput, limit: int = 20, db: Session = Depends(deps.get_db)
):
    return await TracksService.filter_tracks_exact(db, filters, limit)


@router.get("/{track_id}", response_model=TrackResponse)
async def get_track(track_id: int, db: Session = Depends(deps.get_db)):
    track = await TracksService.get_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Música não encontrada")
    return track
