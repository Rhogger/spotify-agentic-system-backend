from pydantic import BaseModel, ConfigDict
from typing import List


class SpotifyImage(BaseModel):
    url: str
    height: int | None = None
    width: int | None = None


class SpotifyFollowers(BaseModel):
    href: str | None = None
    total: int


class SpotifyExternalUrls(BaseModel):
    spotify: str


class SpotifyExplicitContent(BaseModel):
    filter_enabled: bool
    filter_locked: bool


class SpotifyProfile(BaseModel):
    id: str
    display_name: str | None = None
    email: str
    country: str | None = None
    product: str | None = None
    images: List[SpotifyImage] = []
    followers: SpotifyFollowers | None = None
    external_urls: SpotifyExternalUrls | None = None
    href: str | None = None
    uri: str | None = None
    explicit_content: SpotifyExplicitContent | None = None


class UserRead(BaseModel):
    id: int
    email: str
    display_name: str | None = None
    spotify_id: str
    spotify_access_token: str | None = None
    spotify_profile: SpotifyProfile | None = None

    model_config = ConfigDict(from_attributes=True)
