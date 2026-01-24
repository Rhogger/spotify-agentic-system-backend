from app.api.endpoints import auth, mcp, health, track, playlist
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["System"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["MCP Spotify"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(track.router, prefix="/tracks", tags=["tracks"])
api_router.include_router(playlist.router, prefix="/playlists", tags=["playlists"])