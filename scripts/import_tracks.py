import pandas as pd
import os
import sys
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal, engine
from app.models.track import Track

def import_tracks_from_csv(csv_path: str):
    db: Session = SessionLocal()
    
    if not os.path.exists(csv_path):
        print(f"Erro: Arquivo {csv_path} não encontrado.")
        return

    try:
        print(f"Lendo dados de {csv_path}...")
        df = pd.read_csv(csv_path)
        
        track_objects = []

        print("Transformando linhas em objetos Track...")
        for _, row in df.iterrows():
            track = Track(
                id=row['id'],
                name=row['name'],
                artists=row['artists'],
                duration_ms=int(row['duration_ms']),
                acousticness=float(row['acousticness']),
                danceability=float(row['danceability']),
                energy=float(row['energy']),
                instrumentalness=float(row['instrumentalness']),
                speechiness=float(row['speechiness']),
                valence=float(row['valence']),
                explicit=bool(row['explicit']),
                is_popular=bool(row['is_popular']),
                # Décadas (usando o prefixo d_ para evitar erro de sintaxe)
                d_1920s=bool(row['1920s']),
                d_1930s=bool(row['1930s']),
                d_1940s=bool(row['1940s']),
                d_1950s=bool(row['1950s']),
                d_1960s=bool(row['1960s']),
                d_1970s=bool(row['1970s']),
                d_1980s=bool(row['1980s']),
                d_1990s=bool(row['1990s']),
                d_2000s=bool(row['2000s']),
                d_2010s=bool(row['2010s']),
                d_2020s=bool(row['2020s'])
            )
            track_objects.append(track)

        # Inserção em lote (Batch Insert)
        print(f"Iniciando inserção de {len(track_objects)} músicas no PostgreSQL...")
        db.bulk_save_objects(track_objects)
        db.commit()
        print("✅ Importação concluída com sucesso!")

    except Exception as e:
        print(f"❌ Erro durante a importação: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Caminho para o arquivo na nova pasta data/
    FILE_PATH = "data/features.csv"
    import_tracks_from_csv(FILE_PATH)