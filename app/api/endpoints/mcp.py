from fastapi import APIRouter, HTTPException
from app.services.spotify_mcp import SpotifyMCPService
from app.schemas.mcp import ToolCallRequest

router = APIRouter()

mcp_client = SpotifyMCPService()


@router.get("/tools")
async def get_available_tools():
    """Lista ferramentas disponíveis."""
    try:
        return await mcp_client.list_tools()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/call")
async def call_mcp_tool(payload: ToolCallRequest):
    """Chama uma ferramenta."""
    try:
        return await mcp_client.call_tool(payload.name, payload.arguments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
