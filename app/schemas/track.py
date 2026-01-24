from pydantic import BaseModel, ConfigDict
from typing import Optional, List

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