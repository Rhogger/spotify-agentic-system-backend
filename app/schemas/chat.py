from typing import List, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    tracks: Optional[List[dict]] = None
    playlists: Optional[List[dict]] = None
