# from typing import List

# from app.core.database import SessionLocal
# from app.services.playlists import PlaylistsService


# async def create_playlist(name: str):
#     """
#     Cria uma nova playlist ou recupera uma existente caso o nome seja idêntico.

#     Parâmetros:
#     - name (str): Nome da playlist desejada.

#     Retorno:
#     Um dicionário contendo o 'id' da playlist, o 'name' e um campo 'already_exists'.
#     Se 'already_exists' for True, informe ao usuário que a playlist já existia.
#     """
#     db = SessionLocal()
#     try:
#         return await PlaylistsService.create_playlist(db, name=name, owner_id=1)
#     except Exception as e:
#         return {"error": str(e)}
#     finally:
#         db.close()


# async def delete_playlist(name: str):
#     """
#     Marca uma playlist como deletada no sistema.

#     Parâmetros:
#     - name (str): Nome da playlist a ser deletada.

#     Retorno:
#     Um dicionário indicando o sucesso ou falha da operação.
#     """
#     db = SessionLocal()
#     try:
#         return await PlaylistsService.delete_playlist(db, name=name, owner_id=1)
#     except Exception as e:
#         return {"error": str(e)}
#     finally:
#         db.close()


# async def get_playlist_tracks(playlist_name: str):
#     """
#     Recupera as faixas de uma playlist específica.

#     Parâmetros:
#     - playlist_name (str): Nome da playlist cujas faixas serão recuperadas.

#     Retorno:
#     Uma lista de dicionários, cada um representando uma faixa na playlist.
#     """
#     db = SessionLocal()
#     try:
#         return await PlaylistsService.get_playlist_tracks_by_name(
#             db, playlist_name=playlist_name, owner_id=1
#         )
#     except Exception as e:
#         return {"error": str(e)}
#     finally:
#         db.close()


# async def add_tracks_to_playlist(playlist_name: str, track_names: List[str]):
#     """
#     Adiciona faixas a uma playlist existente.

#     Parâmetros:
#     - playlist_name (str): Nome da playlist onde as faixas serão adicionadas.
#     - track_names (List[str]): Lista de nomes das faixas a serem adicionadas.

#     Retorno:
#     Um dicionário indicando o sucesso ou falha da operação.
#     """
#     db = SessionLocal()
#     try:
#         return await PlaylistsService.add_tracks_batch(
#             db, playlist_name=playlist_name, track_names=track_names, owner_id=1
#         )
#     except Exception as e:
#         return {"error": str(e)}
#     finally:
#         db.close()
