from fastapi import APIRouter
from app.core.logger import logger

router = APIRouter()


@router.get("/")
async def health_check():
    logger.debug("Verificação de saúde (Health Check) solicitada")
    return {"status": "ok"}
