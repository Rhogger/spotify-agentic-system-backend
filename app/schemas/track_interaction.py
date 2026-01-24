from pydantic import BaseModel
from enum import Enum

class InteractionTypeEnum(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    SKIP = "skip"
    BACK = "back"
    VIEW = "view"

class InteractionResponse(BaseModel):
    message: str
    track_id: int
    type: InteractionTypeEnum