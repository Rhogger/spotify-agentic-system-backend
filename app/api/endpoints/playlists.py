from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.playlists import PlaylistCreate, PlaylistResponse
from app.schemas.tracks import TrackResponse
from app.services.playlists import PlaylistsService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
async def create_playlist(playlist_in: PlaylistCreate, db: Session = Depends(get_db)):
    result = await PlaylistsService.create_playlist(
        db, playlist_in.name, playlist_in.owner_id
    )
    return result


@router.get("/", response_model=List[PlaylistResponse])
async def get_all_playlists(
    skip: int = Query(0, ge=0, description="Items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = await PlaylistsService.get_all_playlists(db, current_user.id, skip, limit)
    return results


@router.get("/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = await PlaylistsService.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    return playlist


@router.post("/tracks", status_code=status.HTTP_201_CREATED)
async def add_tracks_batch(
    playlist_id: int, track_ids: List[int], db: Session = Depends(get_db)
):
    added_count = await PlaylistsService.add_tracks_batch(db, playlist_id, track_ids)
    if added_count is None:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    return {"message": f"{added_count} músicas adicionadas"}


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(playlist_id: int, db: Session = Depends(get_db)):
    deleted = await PlaylistsService.delete_playlist(db, playlist_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    return None


@router.get("/{playlist_id}/tracks", response_model=List[TrackResponse])
async def get_playlist_tracks(
    playlist_id: int,
    skip: int = Query(0, ge=0, description="Número de itens para pular"),
    limit: int = Query(
        20, ge=1, le=100, description="Quantidade de itens para retornar"
    ),
    db: Session = Depends(get_db),
):
    """
    Busca as músicas de uma playlist específica com suporte a paginação.
    """
    tracks = await PlaylistsService.get_playlist_tracks(db, playlist_id, skip, limit)
    if tracks is None:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    return tracks


@router.delete(
    "/{playlist_id}/tracks/{track_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_track_from_playlist(
    playlist_id: int, track_id: int, db: Session = Depends(get_db)
):
    """
    Remove uma música específica de uma playlist.
    """
    deleted = await PlaylistsService.remove_track_from_playlist(
        db, playlist_id, track_id
    )
    if not deleted:
        raise HTTPException(
            status_code=404, detail="A música não foi encontrada nesta playlist"
        )
    return None
