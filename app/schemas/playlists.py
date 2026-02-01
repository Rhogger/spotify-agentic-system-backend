from app.schemas.spotify import SpotifyPlaylistsResponse
from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class PlaylistItemCreate(BaseModel):
    track_id: int


class PlaylistsMCPResponse(BaseModel):
    md: Optional[str] = None
    json: Optional[SpotifyPlaylistsResponse] = None


class PlaylistCreate(BaseModel):
    name: str
    owner_id: int


class PlaylistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    track_id: int


class PlaylistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    owner_id: int
    music_count: int
    items: List[PlaylistItemResponse]


class PlaylistStatusResponse(BaseModel):
    status: str
    message: str
    id: Optional[int] = None
    name: Optional[str] = None
    owner_id: Optional[int] = None
    music_count: Optional[int] = None


class TrackResponse(BaseModel):
    id: int
    name: str
    artist: str
    spotify_id: str


class PlaylistTracksResponse(BaseModel):
    status: str
    message: Optional[str] = None
    tracks: Optional[List[TrackResponse]] = None


class PlaylistRawSchema(BaseModel):
    id: str
    name: str
    description: str
    owner: str
    followers: int
    total_tracks: int
    total_duration_ms: Optional[int] = None
    formatted_duration: str
    image: str
    privacy: str
    snapshot_id: str
    primary_color: Optional[str] = None


class PlaylistMCPDetailResponse(BaseModel):
    md: Optional[str] = None
    json: Optional[PlaylistRawSchema] = None


# --- Schemas para operações de playlist via MCP ---


class CreatePlaylistInput(BaseModel):
    """Input para criar uma nova playlist no Spotify."""

    name: str
    description: Optional[str] = None
    public: bool = False


class UpdatePlaylistInput(BaseModel):
    """Input para atualizar uma playlist existente."""

    name: Optional[str] = None
    description: Optional[str] = None
    public: Optional[bool] = None


class AddTracksInput(BaseModel):
    """Input para adicionar tracks a uma playlist."""

    track_ids: List[str]
    position: Optional[int] = None


class RemoveTracksInput(BaseModel):
    """Input para remover tracks de uma playlist."""

    track_ids: List[str]
    snapshot_id: Optional[str] = None
    positions: Optional[List[int]] = None


class PlaylistOperationResponse(BaseModel):
    """Resposta padrão para operações de playlist."""

    success: bool
    message: str
    playlist_id: Optional[str] = None
    playlist_url: Optional[str] = None
