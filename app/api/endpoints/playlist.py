from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.core.database import get_db
from app.models.playlist import Playlist, PlaylistItem
from app.models.track import Track
from app.schemas.playlist import (
    PlaylistCreate, PlaylistResponse, PlaylistItemResponse
)
from app.schemas.track import TrackResponse

router = APIRouter()

@router.post("/", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
def create_playlist(
    playlist_in: PlaylistCreate,
    db: Session = Depends(get_db)
):
    db_playlist = Playlist(name=playlist_in.name, owner_id=playlist_in.owner_id)
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return {**db_playlist.__dict__, "music_count": 0, "items": []}

@router.get("/", response_model=List[PlaylistResponse])
def get_all_playlists(
    owner_id: int = Query(...), 
    db: Session = Depends(get_db)
):
    playlists = db.query(Playlist).filter(Playlist.owner_id == owner_id, Playlist.system_deleted == False).all()
    
    results = []
    for p in playlists:
        count = db.query(func.count(PlaylistItem.id)).filter(PlaylistItem.playlist_id == p.id).scalar()
        items = db.query(PlaylistItem).filter(PlaylistItem.playlist_id == p.id).limit(10).all()
        results.append({
            "id": p.id,
            "name": p.name,
            "owner_id": p.owner_id,
            "music_count": count,
            "items": items
        })
    return results

@router.get("/{playlist_id}", response_model=PlaylistResponse)
def get_playlist(
    playlist_id: int,
    db: Session = Depends(get_db)
):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    
    count = db.query(func.count(PlaylistItem.id)).filter(PlaylistItem.playlist_id == playlist_id).scalar()
    items = db.query(PlaylistItem).filter(PlaylistItem.playlist_id == playlist_id).all()
    
    return {
        "id": playlist.id,
        "name": playlist.name,
        "owner_id": playlist.owner_id,
        "music_count": count,
        "items": items
    }

@router.post("/tracks", status_code=status.HTTP_201_CREATED)
def add_tracks_batch(
    playlist_id: int,
    track_ids: List[int],
    db: Session = Depends(get_db)
):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")

    added_count = 0
    for t_id in track_ids:
        if not db.query(Track).filter(Track.id == t_id).first():
            continue
        exists = db.query(PlaylistItem).filter_by(playlist_id=playlist_id, track_id=t_id).first()
        if not exists:
            db.add(PlaylistItem(playlist_id=playlist_id, track_id=t_id))
            added_count += 1
    
    db.commit()
    return {"message": f"{added_count} músicas adicionadas"}

@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    
    playlist.system_deleted = True
    db.commit()
    return None

@router.get("/{playlist_id}/tracks", response_model=List[TrackResponse])
def get_playlist_tracks(
    playlist_id: int,
    skip: int = Query(0, ge=0, description="Número de itens para pular"),
    limit: int = Query(20, ge=1, le=100, description="Quantidade de itens para retornar"),
    db: Session = Depends(get_db)
):
    """
    Busca as músicas de uma playlist específica com suporte a paginação.
    """
    # Verifica se a playlist existe
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")

    # Realiza o Join entre Track e PlaylistItem para filtrar pela playlist_id
    tracks = db.query(Track)\
        .join(PlaylistItem, Track.id == PlaylistItem.track_id)\
        .filter(PlaylistItem.playlist_id == playlist_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return tracks

@router.delete("/{playlist_id}/tracks/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_track_from_playlist(
    playlist_id: int,
    track_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove uma música específica de uma playlist.
    """
    # Busca o item na tabela de associação
    item = db.query(PlaylistItem).filter(
        PlaylistItem.playlist_id == playlist_id,
        PlaylistItem.track_id == track_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404, 
            detail="A música não foi encontrada nesta playlist"
        )

    db.delete(item)
    db.commit()
    return None