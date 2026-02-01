from pydantic import BaseModel
from typing import Dict, Any


class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any] = {}
