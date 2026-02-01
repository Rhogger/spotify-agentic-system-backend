from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.recommendation import AudioFeaturesInput, RecommendationResponse
from app.services.recommender import RecommenderService

from app.core.logger import logger

router = APIRouter()


@router.post(
    "/",
    response_model=RecommendationResponse,
    summary="Recomenda músicas baseadas em características de áudio",
    description="Retorna uma lista de tracks usando o modelo KNN e filtros de década/popularidade.",
)
async def get_recommendations(
    features: AudioFeaturesInput, db: Session = Depends(deps.get_db)
):
    try:
        logger.info("Solicitação de recomendação recebida", data=features.model_dump())
        results = await RecommenderService.recommend_by_audio_features(db, features)
        if not results:
            logger.warning("Nenhuma recomendação encontrada para estes parâmetros")
            raise HTTPException(
                status_code=404,
                detail="Nenhuma recomendação encontrada para estes parâmetros.",
            )
        return {"recommendations": results}
    except ValueError as e:
        logger.error(f"Erro de validação nas recomendações: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro interno no motor de recomendação: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro interno no motor de recomendação: {str(e)}"
        )
