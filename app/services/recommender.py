import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import asc
from app.models.track import Track
from app.schemas.recommendation import AudioFeaturesInput
import app.services.model_loader as loader

class RecommenderService:
    # Cache na memória para não bater no banco toda hora buscando a lista de IDs
    _id_map_cache = None

    @classmethod
    def get_id_map(cls, db: Session):
        """
        Cria um mapeamento de índice -> spotify_id baseado na ordem do banco.
        Isso substitui a necessidade do pre_processing.csv.
        """
        if cls._id_map_cache is None:
            # IMPORTANTE: A ordem aqui deve ser a mesma ordem das linhas do CSV 
            # usado no treinamento do modelo. Geralmente é a ordem do 'id' primário.
            tracks_ids = db.query(Track.spotify_id).order_by(asc(Track.id)).all()
            cls._id_map_cache = [t.spotify_id for t in tracks_ids]
        return cls._id_map_cache

    @staticmethod
    async def recommend_by_audio_features(db: Session, features: AudioFeaturesInput):
        model = loader.get_model()
        scaler = loader.get_preprocessor()
        model_features = loader.get_features()
        
        # 1. Preparar o input para o modelo
        input_dict = {
            "acousticness": features.acousticness,
            "danceability": features.danceability,
            "energy": features.energy,
            "valence": features.valence
        }
        
        # Normalização
        input_df = pd.DataFrame([input_dict])
        scaled_data = scaler.transform(input_df)
        full_df = pd.DataFrame(scaled_data, columns=input_dict.keys())
        
        # Flags de categoria
        full_df["is_popular"] = 1 if features.is_popular else 0
        full_df["explicit"] = 1 if features.explicit else 0
        
        # Flags de Décadas (conforme o modelo espera)
        decades = [f"d_{d}s" for d in range(1920, 2030, 10)] # Ajustado para bater com seu Model Track (d_1920s)
        for d_col in decades:
            # O modelo provavelmente espera '1920s' sem o 'd_', mas seu banco usa 'd_1920s'.
            # Ajustamos aqui para a coluna que o MODELO espera (ex: '1920s')
            model_dec_col = d_col.replace("d_", "") 
            full_df[model_dec_col] = 1 if (features.decade and features.decade in d_col) else 0

        # 2. Inferência
        input_final = full_df[model_features].values
        distances, indices = model.kneighbors(input_final, n_neighbors=features.top_k)

        # 3. Mapear índices para Spotify IDs usando o banco (sem CSV)
        id_map = RecommenderService.get_id_map(db)
        
        recommended_ids = []
        for idx in indices[0]:
            if idx < len(id_map):
                recommended_ids.append(id_map[idx])

        # 4. Buscar objetos completos no banco
        return db.query(Track).filter(Track.spotify_id.in_(recommended_ids)).all()