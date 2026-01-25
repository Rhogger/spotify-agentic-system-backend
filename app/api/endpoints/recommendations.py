from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.recommendation import AudioFeaturesInput, RecommendationResponse
from app.services.recommender import RecommenderService

router = APIRouter()

@router.post("/by-features", 
             response_model=RecommendationResponse,
             summary="Recomenda músicas baseadas em características de áudio",
             description="Retorna uma lista de tracks usando o modelo KNN e filtros de década/popularidade.")
async def get_recommendations(
    features: AudioFeaturesInput,
    db: Session = Depends(deps.get_db)
):
    try:
        results = await RecommenderService.recommend_by_audio_features(db, features)
        if not results:
            raise HTTPException(status_code=404, detail="Nenhuma recomendação encontrada para estes parâmetros.")
        return {"recommendations": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Erro de inferência ou carregamento
        raise HTTPException(status_code=500, detail=f"Erro interno no motor de recomendação: {str(e)}")