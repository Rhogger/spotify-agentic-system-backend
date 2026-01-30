from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class PlaylistItemCreate(BaseModel):
    track_id: int


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
