from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.spotify_mcp import SpotifyMCPService
from app.schemas.mcp import (
    ToolCallRequest,
    PlaylistsMCPResponse,
    PlaylistTracksMCPResponse,
)

router = APIRouter()

mcp_client = SpotifyMCPService()


@router.get("/tools")
async def get_available_tools():
    """Lista ferramentas disponíveis."""
    try:
        return await mcp_client.list_tools()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/call")
async def call_mcp_tool(
    payload: ToolCallRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Chama uma ferramenta."""
    try:
        return await mcp_client.call_tool(
            payload.name, current_user, db, payload.arguments
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/playlists", response_model=PlaylistsMCPResponse)
async def get_my_playlists_mcp(
    limit: int = 50,
    json: bool = True,
    md: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint específico para buscar playlists via MCP Tool 'getMyPlaylists'.
    Retorna o MD e o JSON raw.
    """
    try:
        return await mcp_client.get_my_playlists(current_user, db, limit, json, md)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/playlists/{playlist_id}/tracks", response_model=PlaylistTracksMCPResponse)
async def get_playlist_tracks_mcp(
    playlist_id: str,
    limit: int = 50,
    offset: int = 0,
    json: bool = True,
    md: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint específico para buscar faixas de uma playlist via MCP Tool 'getPlaylistTracks'.
    """
    try:
        return await mcp_client.get_playlist_tracks(
            current_user, db, playlist_id, limit, offset, json, md
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
