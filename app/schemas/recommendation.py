from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from app.schemas.track import TrackResponse

class AudioFeaturesInput(BaseModel):
    energy: float = Field(..., ge=0.0, le=1.0)
    danceability: float = Field(..., ge=0.0, le=1.0)
    valence: float = Field(..., ge=0.0, le=1.0)
    acousticness: float = Field(..., ge=0.0, le=1.0)
    # Adicionais baseados no modelo anterior
    is_popular: bool = False
    explicit: bool = False
    decade: Optional[str] = Field(None, pattern="^(1920|1930|1940|1950|1960|1970|1980|1990|2000|2010|2020)$")
    top_k: int = Field(20, ge=1, le=50)

class RecommendationResponse(BaseModel):
    recommendations: List[TrackResponse]