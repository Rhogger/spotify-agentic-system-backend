from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    id: int
    email: str
    display_name: str | None = None
    spotify_id: str
    spotify_access_token: str

    model_config = ConfigDict(from_attributes=True)
