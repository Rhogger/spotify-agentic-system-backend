from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import asc
from app.models.track import Track
from app.models.user import User
from app.schemas.recommendation import AudioFeaturesInput
from app.schemas.tracks import TrackResponse
import app.services.model_loader as loader
from app.services.tracks import TracksService
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
    async def recommend_by_audio_features(
        db: Session, features: AudioFeaturesInput, user: Optional[User] = None
    ) -> list[TrackResponse]:
        """
        Gera recomendações baseadas em audio features usando o modelo KNN.

        Args:
            db: Sessão do banco de dados
            features: Características de áudio para busca
            user: Usuário autenticado (opcional, necessário para buscar imagens)

        Returns:
            Lista de TrackResponse com image_url preenchido (se user fornecido)
        """
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
        distances, indices = model.kneighbors(input_final, n_neighbors=20)

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

        images_map: dict[str, Optional[str]] = {}
        if user and recommended_ids:
            try:
                images_response = await TracksService.get_track_images_mcp(
                    user=user,
                    db=db,
                    track_ids=recommended_ids,
                )
                if images_response.json:
                    images_map = images_response.json.images
                    logger.success(
                        f"Imagens obtidas para {images_response.json.count} tracks"
                    )
            except Exception as e:
                logger.warning(
                    f"Não foi possível buscar imagens das tracks: {e}"
                )

        track_responses = []
        for track in results:
            track_response = TrackResponse.model_validate(track)
            track_response.image_url = images_map.get(track.spotify_id)
            track_responses.append(track_response)

        return track_responses
