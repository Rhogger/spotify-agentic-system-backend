from pydantic import BaseModel
from typing import Dict, Any, Optional
from .spotify import SpotifyPlaylistsResponse, SpotifyPlaylistTracksResponse


class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any] = {}


class MCPToolResponse(BaseModel):
    md: Optional[str] = None
    json: Optional[Any] = None


class PlaylistsMCPResponse(BaseModel):
    md: Optional[str] = None
    json: Optional[SpotifyPlaylistsResponse] = None


class PlaylistTracksMCPResponse(BaseModel):
    md: Optional[str] = None
    json: Optional[SpotifyPlaylistTracksResponse] = None
