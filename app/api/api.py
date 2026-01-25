from app.api.endpoints import (
    auth,
    health,
    mcp,
    playlists,
    recommendations,
    track_actions,
    tracks,
)
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["System"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["MCP Spotify"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(tracks.router, prefix="/tracks", tags=["Tracks"])
api_router.include_router(playlists.router, prefix="/playlists", tags=["Playlists"])
api_router.include_router(
    track_actions.router, prefix="/tracks", tags=["Track actions"]
)
api_router.include_router(
    recommendations.router, prefix="/recommendations", tags=["Recommendations"]
)
