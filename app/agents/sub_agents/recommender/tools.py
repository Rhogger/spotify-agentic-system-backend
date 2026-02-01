from google.adk.tools import ToolContext
from app.services.recommender import RecommenderService
from app.schemas.recommendation import AudioFeaturesInput


async def recommend_by_features(tool_context: ToolContext, features: dict) -> list:
    """
    Gera recomendações de músicas similares com base em características técnicas (audio features).
    
    Esta ferramenta é ideal para quando você já tem os dados de uma 'seed_track' (obtidos pelo librarian_agent)
    e deseja encontrar outras faixas que mantenham a mesma vibe (energia, dançabilidade, valência, etc.).

    Args:
        features: Um dicionário contendo as características da música base.
                  Campos esperados: "energy", "danceability", "valence", "acousticness", 
                  "instrumentalness", "speechiness".
                  Opcionais: "is_popular" (bool), "explicit" (bool), "decade" (str).

    Returns:
        Uma lista de dicionários contendo os detalhes das músicas recomendadas, incluindo capas.
    """
    from app.agents.sub_agents.dj.tools import _get_user_from_context
    user, db = _get_user_from_context(tool_context)
    try:
        input_data = AudioFeaturesInput(**(features | {"top_k": 5}))

        results = await RecommenderService.recommend_by_audio_features(db, input_data, user=user)

        tracks_dict = [t.model_dump() for t in results]
        
        tool_context.state["metadata:tracks"] = tracks_dict

        return tracks_dict
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()
