from pydantic import BaseModel, Field
from typing import List, Optional

class PlayRequest(BaseModel):
    uri: Optional[str] = None
    uris: Optional[List[str]] = None
    context_uri: Optional[str] = None
    offset: Optional[dict] = None
    device_id: Optional[str] = None

class VolumeRequest(BaseModel):
    volume_percent: int = Field(..., ge=0, le=100)
    device_id: Optional[str] = None

class ShuffleRequest(BaseModel):
    state: bool
    device_id: Optional[str] = None

class RepeatRequest(BaseModel):
    state: str # track, context, off
    device_id: Optional[str] = None

class TransferRequest(BaseModel):
    device_id: str
    play: bool = False
