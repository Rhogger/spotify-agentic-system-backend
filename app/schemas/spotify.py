from pydantic import BaseModel
from typing import List, Optional


class SpotifyImage(BaseModel):
    height: Optional[int] = None
    url: str
    width: Optional[int] = None


class SpotifyExternalUrls(BaseModel):
    spotify: str


class SpotifyOwner(BaseModel):
    display_name: Optional[str] = None
    external_urls: SpotifyExternalUrls
    href: str
    id: str
    type: str
    uri: str


class SpotifyTracksRef(BaseModel):
    href: str
    total: int


class SpotifyPlaylist(BaseModel):
    collaborative: bool
    description: Optional[str] = None
    external_urls: SpotifyExternalUrls
    href: str
    id: str
    images: Optional[List[SpotifyImage]] = None
    name: str
    owner: SpotifyOwner
    primary_color: Optional[str] = None
    public: Optional[bool] = None
    snapshot_id: str
    tracks: SpotifyTracksRef
    type: str
    uri: str


class SpotifyPlaylistsResponse(BaseModel):
    href: str
    limit: int
    next: Optional[str] = None
    offset: int
    previous: Optional[str] = None
    total: int
    items: List[SpotifyPlaylist]


class SpotifyArtist(BaseModel):
    external_urls: SpotifyExternalUrls
    href: str
    id: str
    name: str
    type: str
    uri: str


class SpotifyAlbum(BaseModel):
    album_type: str
    artists: List[SpotifyArtist]
    external_urls: SpotifyExternalUrls
    href: str
    id: str
    images: List[SpotifyImage]
    name: str
    release_date: str
    release_date_precision: str
    total_tracks: int
    type: str
    uri: str


class SpotifyTrack(BaseModel):
    album: SpotifyAlbum
    artists: List[SpotifyArtist]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: Optional[dict] = None
    external_urls: SpotifyExternalUrls
    href: str
    id: str
    is_local: bool
    is_playable: Optional[bool] = None
    name: str
    popularity: int
    preview_url: Optional[str] = None
    track_number: int
    type: str
    uri: str


class SpotifyPlaylistItem(BaseModel):
    added_at: str
    added_by: SpotifyOwner
    is_local: bool
    primary_color: Optional[str] = None
    track: Optional[SpotifyTrack] = None
    video_thumbnail: Optional[dict] = None


class SpotifyPlaylistTracksResponse(BaseModel):
    href: str
    limit: int
    next: Optional[str] = None
    offset: int
    previous: Optional[str] = None
    total: int
    items: List[SpotifyPlaylistItem]
