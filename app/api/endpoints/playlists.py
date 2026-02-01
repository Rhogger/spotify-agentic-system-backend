from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.playlists import (
    PlaylistsMCPResponse,
    PlaylistMCPDetailResponse,
    CreatePlaylistInput,
    UpdatePlaylistInput,
    AddTracksInput,
    RemoveTracksInput,
    PlaylistOperationResponse,
)
from app.services.playlists import PlaylistsService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import logger

router = APIRouter()


@router.get(
    "/",
    response_model=PlaylistsMCPResponse,
    summary="Lista playlists do usuário",
    description="Retorna as playlists do usuário autenticado via integração MCP com Spotify. Suporta paginação e formatos de saída JSON/Markdown.",
)
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


@router.post(
    "/",
    response_model=PlaylistOperationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova playlist",
    description="Cria uma nova playlist no Spotify via MCP.",
)
async def create_playlist_mcp(
    playlist_in: CreatePlaylistInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cria uma nova playlist via MCP Tool 'createPlaylist'.
    """
    try:
        logger.info(f"Criando playlist '{playlist_in.name}' via MCP")
        result = await PlaylistsService.create_playlist_mcp(
            current_user,
            db,
            playlist_in.name,
            playlist_in.description,
            playlist_in.public,
        )
        return PlaylistOperationResponse(**result)
    except Exception as e:
        logger.error(f"Erro ao criar playlist via MCP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{playlist_id}",
    response_model=PlaylistMCPDetailResponse,
    summary="Detalhes de uma playlist",
    description="Retorna informações detalhadas de uma playlist específica do Spotify, incluindo metadados e opcionalmente a duração total.",
)
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


@router.patch(
    "/{playlist_id}",
    response_model=PlaylistOperationResponse,
    summary="Atualiza uma playlist",
    description="Atualiza o nome, descrição ou visibilidade de uma playlist via MCP.",
)
async def update_playlist_mcp(
    playlist_id: str,
    playlist_in: UpdatePlaylistInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Atualiza uma playlist via MCP Tool 'updatePlaylistDetails'.
    """
    try:
        logger.info(f"Atualizando playlist {playlist_id} via MCP")
        result = await PlaylistsService.update_playlist_mcp(
            current_user,
            db,
            playlist_id,
            playlist_in.name,
            playlist_in.description,
            playlist_in.public,
        )
        return PlaylistOperationResponse(**result)
    except Exception as e:
        logger.error(f"Erro ao atualizar playlist {playlist_id} via MCP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{playlist_id}",
    response_model=PlaylistOperationResponse,
    summary="Remove playlist da biblioteca",
    description="Remove (unfollow) uma playlist da biblioteca do usuário. Nota: O Spotify não permite deletar playlists permanentemente.",
)
async def unfollow_playlist_mcp(
    playlist_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove uma playlist da biblioteca via MCP Tool 'unfollowPlaylist'.
    """
    try:
        logger.info(f"Removendo playlist {playlist_id} da biblioteca via MCP")
        result = await PlaylistsService.unfollow_playlist_mcp(
            current_user, db, playlist_id
        )
        return PlaylistOperationResponse(**result)
    except Exception as e:
        logger.error(f"Erro ao remover playlist {playlist_id} via MCP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{playlist_id}/tracks",
    response_model=PlaylistOperationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adiciona tracks a uma playlist",
    description="Adiciona uma ou mais tracks a uma playlist via MCP.",
)
async def add_tracks_to_playlist_mcp(
    playlist_id: str,
    tracks_in: AddTracksInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Adiciona tracks a uma playlist via MCP Tool 'addTracksToPlaylist'.
    """
    try:
        logger.info(f"Adicionando {len(tracks_in.track_ids)} tracks à playlist {playlist_id} via MCP")
        result = await PlaylistsService.add_tracks_to_playlist_mcp(
            current_user,
            db,
            playlist_id,
            tracks_in.track_ids,
            tracks_in.position,
        )
        return PlaylistOperationResponse(**result)
    except Exception as e:
        logger.error(f"Erro ao adicionar tracks à playlist {playlist_id} via MCP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{playlist_id}/tracks",
    response_model=PlaylistOperationResponse,
    summary="Remove tracks de uma playlist",
    description="Remove uma ou mais tracks de uma playlist via MCP.",
)
async def remove_tracks_from_playlist_mcp(
    playlist_id: str,
    tracks_in: RemoveTracksInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove tracks de uma playlist via MCP Tool 'removeTracksFromPlaylist'.
    """
    try:
        logger.info(f"Removendo {len(tracks_in.track_ids)} tracks da playlist {playlist_id} via MCP")
        result = await PlaylistsService.remove_tracks_from_playlist_mcp(
            current_user,
            db,
            playlist_id,
            tracks_in.track_ids,
            tracks_in.snapshot_id,
        )
        return PlaylistOperationResponse(**result)
    except Exception as e:
        logger.error(f"Erro ao remover tracks da playlist {playlist_id} via MCP: {e}")
        raise HTTPException(status_code=500, detail=str(e))
