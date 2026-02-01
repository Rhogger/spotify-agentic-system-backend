from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.playlists import (
    PlaylistsMCPResponse,
    PlaylistMCPDetailResponse,
)
from app.services.playlists import PlaylistsService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.logger import logger

router = APIRouter()


@router.get("/", response_model=PlaylistsMCPResponse)
async def get_my_playlists_mcp(
    limit: int = 50,
    offset: int = 0,
    json: bool = True,
    md: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Busca playlists via MCP Tool 'getMyPlaylists'.
    """
    try:
        logger.info("Buscando playlists do usuário via MCP")
        return await PlaylistsService.get_my_playlists_mcp(
            current_user, db, limit, offset, json, md
        )
    except Exception as e:
        logger.error(f"Erro ao buscar playlists via MCP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{playlist_id}", response_model=PlaylistMCPDetailResponse)
async def get_playlist_details_mcp(
    playlist_id: str,
    calculate_duration: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Busca detalhes de uma playlist específica via MCP Tool 'getPlaylist'.
    """
    try:
        logger.info(f"Buscando detalhes da playlist {playlist_id} via MCP")
        return await PlaylistsService.get_playlist_details_mcp(
            current_user, db, playlist_id, calculate_duration
        )
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes da playlist {playlist_id} via MCP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
# async def create_playlist(playlist_in: PlaylistCreate, db: Session = Depends(get_db)):
#     result = await PlaylistsService.create_playlist(
#         db, playlist_in.name, playlist_in.owner_id
#     )
#     return result


# @router.post("/tracks", status_code=status.HTTP_201_CREATED)
# async def add_tracks_batch(
#     playlist_id: int, track_ids: List[int], db: Session = Depends(get_db)
# ):
#     added_count = await PlaylistsService.add_tracks_batch(db, playlist_id, track_ids)
#     if added_count is None:
#         raise HTTPException(status_code=404, detail="Playlist não encontrada")
#     return {"message": f"{added_count} músicas adicionadas"}


# @router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_playlist(playlist_id: int, db: Session = Depends(get_db)):
#     deleted = await PlaylistsService.delete_playlist(db, playlist_id)
#     if not deleted:
#         raise HTTPException(status_code=404, detail="Playlist não encontrada")
#     return None


# @router.get("/{playlist_id}/tracks", response_model=List[TrackResponse])
# async def get_playlist_tracks(
#     playlist_id: int,
#     skip: int = Query(0, ge=0, description="Número de itens para pular"),
#     limit: int = Query(
#         20, ge=1, le=100, description="Quantidade de itens para retornar"
#     ),
#     db: Session = Depends(get_db),
# ):
#     """
#     Busca as músicas de uma playlist específica com suporte a paginação.
#     """
#     tracks = await PlaylistsService.get_playlist_tracks(db, playlist_id, skip, limit)
#     if tracks is None:
#         raise HTTPException(status_code=404, detail="Playlist não encontrada")
#     return tracks


# @router.delete(
#     "/{playlist_id}/tracks/{track_id}", status_code=status.HTTP_204_NO_CONTENT
# )
# async def remove_track_from_playlist(
#     playlist_id: int, track_id: int, db: Session = Depends(get_db)
# ):
#     """
#     Remove uma música específica de uma playlist.
#     """
#     deleted = await PlaylistsService.remove_track_from_playlist(
#         db, playlist_id, track_id
#     )
#     if not deleted:
#         raise HTTPException(
#             status_code=404, detail="A música não foi encontrada nesta playlist"
#         )
#     return None
