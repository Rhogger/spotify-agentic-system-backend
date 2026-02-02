from sqlalchemy.orm import Session
from typing import List, Optional, Any
from app.services.spotify_mcp import SpotifyMCPService
from app.models.user import User

class PlayerService:
    @staticmethod
    async def play(
        db: Session,
        user: User,
        uri: Optional[str] = None,
        uris: Optional[List[str]] = None,
        context_uri: Optional[str] = None,
        offset: Optional[dict] = None,
        device_id: Optional[str] = None
    ) -> Any:
        """
        Inicia ou retoma a reprodução no Spotify.
        
        Args:
            db: Sessão do banco de dados.
            user: Usuário autenticado.
            uri: URI individual para reprodução.
            uris: Lista de URIs de faixas para reprodução.
            context_uri: URI de contexto (álbum, playlist, artista).
            offset: Onde iniciar a reprodução no contexto.
            device_id: ID do dispositivo alvo.
        """
        arguments = {
            "uri": uri,
            "uris": uris,
            "contextUri": context_uri,
            "offset": offset,
            "deviceId": device_id
        }
        # Clear None values
        arguments = {k: v for k, v in arguments.items() if v is not None}
        return await SpotifyMCPService.call_tool("playMusic", user, db, arguments)

    @staticmethod
    async def pause(db: Session, user: User, device_id: Optional[str] = None) -> Any:
        """
        Pausa a reprodução atual.
        
        Args:
            db: Sessão do banco de dados.
            user: Usuário autenticado.
            device_id: ID do dispositivo alvo.
        """
        arguments = {"deviceId": device_id} if device_id else {}
        return await SpotifyMCPService.call_tool("pausePlayback", user, db, arguments)

    @staticmethod
    async def resume(db: Session, user: User, device_id: Optional[str] = None) -> Any:
        """
        Retoma a reprodução pausada.
        
        Args:
            db: Sessão do banco de dados.
            user: Usuário autenticado.
            device_id: ID do dispositivo alvo.
        """
        arguments = {"deviceId": device_id} if device_id else {}
        return await SpotifyMCPService.call_tool("resumePlayback", user, db, arguments)

    @staticmethod
    async def next(db: Session, user: User, device_id: Optional[str] = None) -> Any:
        """
        Pula para a próxima faixa na fila.
        
        Args:
            db: Sessão do banco de dados.
            user: Usuário autenticado.
            device_id: ID do dispositivo alvo.
        """
        arguments = {"deviceId": device_id} if device_id else {}
        return await SpotifyMCPService.call_tool("skipToNext", user, db, arguments)

    @staticmethod
    async def previous(db: Session, user: User, device_id: Optional[str] = None) -> Any:
        """
        Volta para a faixa anterior.
        
        Args:
            db: Sessão do banco de dados.
            user: Usuário autenticado.
            device_id: ID do dispositivo alvo.
        """
        arguments = {"deviceId": device_id} if device_id else {}
        return await SpotifyMCPService.call_tool("skipToPrevious", user, db, arguments)

    @staticmethod
    async def set_volume(db: Session, user: User, volume_percent: int, device_id: Optional[str] = None) -> Any:
        """
        Define o volume do dispositivo.
        
        Args:
            db: Sessão do banco de dados.
            user: Usuário autenticado.
            volume_percent: Volume de 0 a 100.
            device_id: ID do dispositivo alvo.
        """
        arguments = {"volumePercent": volume_percent, "deviceId": device_id}
        if device_id is None:
            del arguments["deviceId"]
        return await SpotifyMCPService.call_tool("setVolume", user, db, arguments)

    @staticmethod
    async def set_shuffle(db: Session, user: User, state: bool, device_id: Optional[str] = None) -> Any:
        """
        Ativa ou desativa o modo aleatório.
        
        Args:
            db: Sessão do banco de dados.
            user: Usuário autenticado.
            state: True para ativar, False para desativar.
            device_id: ID do dispositivo alvo.
        """
        arguments = {"state": state, "deviceId": device_id}
        if device_id is None:
            del arguments["deviceId"]
        return await SpotifyMCPService.call_tool("setShuffle", user, db, arguments)

    @staticmethod
    async def set_repeat_mode(db: Session, user: User, state: str, device_id: Optional[str] = None) -> Any:
        """
        Define o modo de repetição.
        
        Args:
            db: Sessão do banco de dados.
            user: Usuário autenticado.
            state: 'track', 'context' ou 'off'.
            device_id: ID do dispositivo alvo.
        """
        arguments = {"state": state, "deviceId": device_id}
        if device_id is None:
            del arguments["deviceId"]
        return await SpotifyMCPService.call_tool("setRepeatMode", user, db, arguments)

    @staticmethod
    async def transfer_playback(db: Session, user: User, device_id: str, play: bool = False) -> Any:
        """
        Transfere a reprodução para um novo dispositivo.
        
        Args:
            db: Sessão do banco de dados.
            user: Usuário autenticado.
            device_id: ID do novo dispositivo.
            play: Se deve iniciar a reprodução imediatamente.
        """
        arguments = {"deviceId": device_id, "play": play}
        return await SpotifyMCPService.call_tool("transferPlayback", user, db, arguments)

    @staticmethod
    async def get_queue(db: Session, user: User) -> Any:
        """
        Obtém a fila de reprodução atual do usuário.
        """
        return await SpotifyMCPService.call_tool("getQueue", user, db)

    @staticmethod
    async def get_now_playing(db: Session, user: User) -> Any:
        """
        Obtém informações sobre a faixa que está tocando agora.
        """
        return await SpotifyMCPService.call_tool("getNowPlaying", user, db)

    @staticmethod
    async def get_devices(db: Session, user: User) -> Any:
        """
        Lista os dispositivos Spotify disponíveis para o usuário.
        """
        return await SpotifyMCPService.call_tool("getAvailableDevices", user, db)
