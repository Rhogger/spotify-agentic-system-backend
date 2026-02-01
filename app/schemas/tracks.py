from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.spotify import SpotifyPlaylistTracksResponse


class PlaylistTracksMCPResponse(BaseModel):
    md: Optional[str] = None
    json: Optional[SpotifyPlaylistTracksResponse] = None


class TrackImagesResponse(BaseModel):
    """Resposta JSON da tool getTrackImages do MCP."""

    images: dict[str, Optional[str]]
    count: int


class TrackImagesMCPResponse(BaseModel):
    """Wrapper da resposta MCP para imagens de tracks."""

    md: Optional[str] = None
    json: Optional[TrackImagesResponse] = None


class TrackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    spotify_id: str
    name: str
    artists: str
    duration_ms: int
    energy: float
    danceability: float
    valence: float
    acousticness: float
    instrumentalness: float
    speechiness: float
    explicit: bool
    image_url: Optional[str] = None


class TrackSearchInput(BaseModel):
    q: str
    limit: int = 10
    offset: int = 0


class TrackFeaturesInput(BaseModel):
    energy: Optional[float] = None
    danceability: Optional[float] = None
    valence: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    speechiness: Optional[float] = None
