from app.api.endpoints import auth, mcp, health, tracks, playlists, track_actions
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["System"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["MCP Spotify"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(tracks.router, prefix="/tracks", tags=["tracks"])
api_router.include_router(playlists.router, prefix="/playlists", tags=["playlists"])
api_router.include_router(
    track_actions.router, prefix="/tracks", tags=["track actions"]
)
