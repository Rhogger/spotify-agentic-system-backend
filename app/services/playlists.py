from typing import List

from app.models.playlist import Playlist, PlaylistItem
from app.models.track import Track
from sqlalchemy import func
from sqlalchemy.orm import Session


class PlaylistsService:
    @staticmethod
    async def create_playlist(db: Session, name: str, owner_id: int):
        """Verifica se a playlist já existe ou cria uma nova."""
        
        # 1. Busca se já existe uma com esse nome (ignora as deletadas)
        existing_playlist = (
            db.query(Playlist)
            .filter(
                Playlist.name == name, 
                Playlist.owner_id == owner_id,
                ~Playlist.system_deleted
            )
            .first()
        )

        if existing_playlist:
            # Se achou, busca o count de músicas
            count = db.query(func.count(PlaylistItem.id)).filter(PlaylistItem.playlist_id == existing_playlist.id).scalar()
            
            # RETORNO IMPORTANTE: Dicionário puro para evitar erro de serialização
            return {
                "id": existing_playlist.id,
                "name": existing_playlist.name,
                "owner_id": existing_playlist.owner_id,
                "music_count": count or 0,
                "status": "success",
                "message": "Playlist existente recuperada."
            }

        # 2. Se não existir, cria uma nova
        try:
            db_playlist = Playlist(name=name, owner_id=owner_id)
            db.add(db_playlist)
            db.commit()
            db.refresh(db_playlist)
            
            return {
                "id": db_playlist.id,
                "name": db_playlist.name,
                "owner_id": db_playlist.owner_id,
                "music_count": 0,
                "status": "success",
                "message": "Nova playlist criada com sucesso."
            }
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}

    @staticmethod
    async def get_all_playlists(db: Session, owner_id: int):
        """Retorna todas as playlists do usuário"""
        playlists = (
            db.query(Playlist)
            .filter(Playlist.owner_id == owner_id, ~Playlist.system_deleted)
            .all()
        )

        results = []
        for p in playlists:
            count = (
                db.query(func.count(PlaylistItem.id))
                .filter(PlaylistItem.playlist_id == p.id)
                .scalar()
            )
            items = (
                db.query(PlaylistItem)
                .filter(PlaylistItem.playlist_id == p.id)
                .limit(10)
                .all()
            )
            results.append(
                {
                    "id": p.id,
                    "name": p.name,
                    "owner_id": p.owner_id,
                    "music_count": count,
                    "items": items,
                }
            )
        return results

    @staticmethod
    async def get_playlist(db: Session, playlist_id: int):
        """Retorna uma playlist específica"""
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            return None

        count = (
            db.query(func.count(PlaylistItem.id))
            .filter(PlaylistItem.playlist_id == playlist_id)
            .scalar()
        )
        items = db.query(PlaylistItem).filter(PlaylistItem.playlist_id == playlist_id).all()

        return {
            "id": playlist.id,
            "name": playlist.name,
            "owner_id": playlist.owner_id,
            "music_count": count,
            "items": items,
        }

    @staticmethod
    async def add_tracks_batch(db: Session, playlist_id: int, track_ids: List[int]):
        """Adiciona múltiplas faixas a uma playlist"""
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            return None

        added_count = 0
        for t_id in track_ids:
            if not db.query(Track).filter(Track.id == t_id).first():
                continue
            exists = (
                db.query(PlaylistItem)
                .filter_by(playlist_id=playlist_id, track_id=t_id)
                .first()
            )
            if not exists:
                db.add(PlaylistItem(playlist_id=playlist_id, track_id=t_id))
                added_count += 1

        db.commit()
        return added_count

    @staticmethod
    async def delete_playlist(db: Session, playlist_id: int):
        """Deleta uma playlist (soft delete)"""
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            return False

        playlist.system_deleted = True
        db.commit()
        return True

    @staticmethod
    async def get_playlist_tracks(
        db: Session, playlist_id: int, skip: int = 0, limit: int = 20
    ):
        """Retorna as faixas de uma playlist com paginação"""
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            return None

        tracks = (
            db.query(Track)
            .join(PlaylistItem, Track.id == PlaylistItem.track_id)
            .filter(PlaylistItem.playlist_id == playlist_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return tracks

    @staticmethod
    async def remove_track_from_playlist(
        db: Session, playlist_id: int, track_id: int
    ):
        """Remove uma faixa de uma playlist"""
        item = (
            db.query(PlaylistItem)
            .filter(
                PlaylistItem.playlist_id == playlist_id, PlaylistItem.track_id == track_id
            )
            .first()
        )

        if not item:
            return False

        db.delete(item)
        db.commit()
        return True
