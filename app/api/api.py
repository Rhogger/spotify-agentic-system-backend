from fastapi import APIRouter
from app.api.endpoints import mcp, health

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["System"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["MCP Spotify"])
