from app.api.endpoints import (
    agent,
    auth,
    health,
    mcp,
    playlists,
    recommendations,
    track_actions,
    tracks,
    users,
    player,
)
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["System"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/auth", tags=["Users"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["MCP Spotify"])
api_router.include_router(agent.router, prefix="/agent", tags=["Chat"])
api_router.include_router(tracks.router, prefix="/tracks", tags=["Tracks"])
api_router.include_router(playlists.router, prefix="/playlists", tags=["Playlists"])
api_router.include_router(
    track_actions.router, prefix="/tracks", tags=["Track actions"]
)
api_router.include_router(
    recommendations.router, prefix="/recommendations", tags=["Recommendations"]
)
api_router.include_router(player.router, prefix="/player", tags=["Player"])
