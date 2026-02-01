import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import asc
from app.models.track import Track
from app.schemas.recommendation import AudioFeaturesInput
import app.services.model_loader as loader
from app.core.logger import logger


class RecommenderService:
    _id_map_cache = None

    @classmethod
    def get_id_map(cls, db: Session):
        """
        Cria um mapeamento de índice -> spotify_id baseado na ordem do banco.
        Isso substitui a necessidade do pre_processing.csv.
        """
        if cls._id_map_cache is None:
            tracks_ids = db.query(Track.spotify_id).order_by(asc(Track.id)).all()
            cls._id_map_cache = [t.spotify_id for t in tracks_ids]
            logger.info(
                f"Cache de ID inicializado com {len(cls._id_map_cache)} faixas."
            )
        return cls._id_map_cache

    @staticmethod
    async def recommend_by_audio_features(db: Session, features: AudioFeaturesInput):
        model = loader.get_model()
        scaler = loader.get_preprocessor()
        model_features = loader.get_features()

        input_dict = {
            "acousticness": features.acousticness,
            "danceability": features.danceability,
            "energy": features.energy,
            "valence": features.valence,
        }

        input_df = pd.DataFrame([input_dict])
        scaled_data = scaler.transform(input_df)
        full_df = pd.DataFrame(scaled_data, columns=input_dict.keys())

        full_df["is_popular"] = 1 if features.is_popular else 0
        full_df["explicit"] = 1 if features.explicit else 0

        decades = [f"d_{d}s" for d in range(1920, 2030, 10)]
        for d_col in decades:
            model_dec_col = d_col.replace("d_", "")
            full_df[model_dec_col] = (
                1 if (features.decade and features.decade in d_col) else 0
            )

        input_final = full_df[model_features].values
        distances, indices = model.kneighbors(input_final, n_neighbors=features.top_k)

        id_map = RecommenderService.get_id_map(db)

        recommended_ids = []
        for idx in indices[0]:
            if idx < len(id_map):
                recommended_ids.append(id_map[idx])

        results = db.query(Track).filter(Track.spotify_id.in_(recommended_ids)).all()
        logger.info(f"Geradas {len(results)} recomendações para audio features.")
        logger.success(
            "Recomendações Encontradas",
            data=[t.name for t in results[:5]],
        )

        return results
