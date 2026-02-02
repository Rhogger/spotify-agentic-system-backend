from typing import List, Optional

from app.schemas.tracks import TrackResponse
from pydantic import BaseModel, Field


class AudioFeaturesInput(BaseModel):
    energy: float = Field(...)
    danceability: float = Field(...)
    valence: float = Field(...)
    acousticness: float = Field(...)
    is_popular: bool = False
    explicit: bool = False
    decade: Optional[str] = Field(
        None, pattern="^(1920|1930|1940|1950|1960|1970|1980|1990|2000|2010|2020)$"
    )


class RecommendationResponse(BaseModel):
    recommendations: List[TrackResponse]
