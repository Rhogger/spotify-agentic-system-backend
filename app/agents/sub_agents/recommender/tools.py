from app.core.database import SessionLocal
from app.schemas.tracks import TrackResponse
from app.services.tracks import TracksService
from app.services.recommender import RecommenderService

async def recommend_by_features(features: dict) -> list:
    """
    Recomenda músicas com base em características de audio de uma música alvo.
    Esta ferramenta reutiliza a lógica do TracksService.

    Args:
        features: Um dicionário contendo as características técnicas desejadas (
          "energy", "danceability", "valence", "acousticness", "is_popular", "explicit", "decade").

    Returns:
        Uma lista de dicionários contendo os detalhes das músicas recomendadas.
    """
    db = SessionLocal()
    try:
        results = await RecommenderService.recommend_by_audio_features(db, features | {"top_k": 5})

        return [TrackResponse.model_validate(t).model_dump() for t in results]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()