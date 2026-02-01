from fastapi import APIRouter
from app.core.logger import logger

router = APIRouter()


@router.get(
    "/",
    summary="Verificação de Saúde",
    description="Verifica se a API está online e respondendo.",
)
async def health_check():
    logger.debug("Verificação de saúde (Health Check) solicitada")
    return {"status": "ok"}
