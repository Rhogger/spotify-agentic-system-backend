from fastapi import APIRouter, HTTPException, Depends
from app.core.logger import logger
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.spotify_mcp import SpotifyMCPService
from app.schemas.mcp import ToolCallRequest

router = APIRouter()

mcp_client = SpotifyMCPService()


@router.get("/tools")
async def get_available_tools():
    """Lista ferramentas disponíveis."""
    logger.info("Solicitação para listar ferramentas do MCP recebida")
    try:
        return await mcp_client.list_tools()
    except Exception as e:
        logger.error(f"Erro ao listar ferramentas MCP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/call")
async def call_mcp_tool(
    payload: ToolCallRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Chama uma ferramenta."""
    logger.info(f"Chamada de ferramenta MCP: {payload.name} iniciada")
    try:
        return await mcp_client.call_tool(
            payload.name, current_user, db, payload.arguments
        )
    except Exception as e:
        logger.error(f"Erro na execução da ferramenta MCP {payload.name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
