from typing import List

from app.core.database import SessionLocal  # Importe sua fábrica de sessões
from app.services.playlists import PlaylistsService
from app.models.user import User
from app.services.tracks import TracksService


async def create_playlist(name: str):
    """
    Cria uma nova playlist ou recupera uma existente caso o nome seja idêntico.

    Parâmetros:
    - name (str): Nome da playlist desejada.

    Retorno:
    Um dicionário contendo o 'id' da playlist, o 'name' e um campo 'already_exists'.
    Se 'already_exists' for True, informe ao usuário que a playlist já existia.
    """
    db = SessionLocal()
    try:
            return await PlaylistsService.create_playlist(db, name=name, owner_id=1)
    except Exception as e:
            return {"error": str(e)}
    finally:
            db.close()
