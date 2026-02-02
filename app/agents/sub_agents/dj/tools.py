from typing import Optional, Literal
from google.adk.tools import ToolContext
from app.services.spotify_mcp import SpotifyMCPService
from app.core.database import SessionLocal
from app.models.user import User
import re


# --- HELPERS ---
def _get_user_from_context(tool_context: ToolContext):
    """
    Extrai os dados do usuário do state da sessão ADK e retorna um objeto User.
    O state é populado pelo ChatService quando a sessão é criada/atualizada.
    """
    db = SessionLocal()

    user_id = tool_context.state.get("user:id")
    if not user_id:
        return None, db

    # Busca o user atualizado do banco (para ter refresh token atualizado se necessário)
    user = db.query(User).filter(User.id == user_id).first()

    if user:
        # Atualiza com tokens do state caso sejam mais recentes
        state_access_token = tool_context.state.get("user:spotify_access_token")
        if state_access_token:
            user.spotify_access_token = state_access_token

    return user, db


# --- WRAPPERS ---


async def play_music(
    tool_context: ToolContext,
    query: Optional[str] = None,
    uri: Optional[str] = None,
    uris: Optional[list[str]] = None,
    context_uri: Optional[str] = None,
    offset: Optional[dict] = None,
    type: Optional[Literal["track", "album", "artist", "playlist"]] = None,
) -> str:
    """
    Inicia a reprodução de música, álbum, artista ou playlist no Spotify.

    Args:
        query: Termo de busca (ex: "Pink Floyd", "Despacito"). Use se não tiver URI.
        uri: URI direto do Spotify (ex: "spotify:track:...") se disponível.
        uris: Lista de URIs do Spotify para tocar.
        context_uri: URI de contexto (álbum, playlist, artista).
        offset: Objeto para definir onde começar (ex: {"position": 0}).
        type: Tipo de item caso use URI/ID (opcional, defaults to track).

    Returns:
        Mensagem de status da ação.
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return (
                "Erro: Nenhum usuário autenticado encontrado no contexto da requisição."
            )

        if query and not (uri or uris or context_uri):
            search_args = {"query": query, "type": type or "track", "limit": 1}
            search_result = await SpotifyMCPService.call_tool(
                "searchSpotify", user, db, search_args
            )

            id_match = re.search(r"ID:\s*([a-zA-Z0-9]+)", search_result)
            if id_match:
                track_id = id_match.group(1)
                play_uri = f"spotify:track:{track_id}"
                await SpotifyMCPService.call_tool(
                    "playMusic", user, db, {"uris": [play_uri]}
                )
                return f"🎵 Tocando agora! {search_result}"
            else:
                return f"Busca realizada, mas não encontrei resultado válido: {search_result}"

        args = {
            "uri": uri,
            "uris": uris,
            "contextUri": context_uri,
            "offset": offset,
            "type": type,
        }
        args = {k: v for k, v in args.items() if v is not None}

        result = await SpotifyMCPService.call_tool("playMusic", user, db, args)
        return f"🎵 Reprodução iniciada: {result}"

    finally:
        db.close()


async def pause_playback(tool_context: ToolContext) -> str:
    """Pausa a reprodução atual no Spotify."""
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        return await SpotifyMCPService.call_tool("pausePlayback", user, db, {})
    finally:
        db.close()


async def resume_playback(tool_context: ToolContext) -> str:
    """Retoma a reprodução pausada no Spotify."""
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        return await SpotifyMCPService.call_tool("resumePlayback", user, db, {})
    finally:
        db.close()


async def skip_to_next(tool_context: ToolContext) -> str:
    """Pula para a próxima faixa."""
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        return await SpotifyMCPService.call_tool("skipToNext", user, db, {})
    finally:
        db.close()


async def skip_to_previous(tool_context: ToolContext) -> str:
    """Volta para a faixa anterior."""
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        return await SpotifyMCPService.call_tool("skipToPrevious", user, db, {})
    finally:
        db.close()


async def get_now_playing(tool_context: ToolContext) -> str:
    """Retorna informações sobre o que está tocando agora (música, artista, progresso)."""
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        return await SpotifyMCPService.call_tool("getNowPlaying", user, db, {})
    finally:
        db.close()


async def get_queue(tool_context: ToolContext) -> str:
    """Retorna a fila de reprodução atual."""
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        return await SpotifyMCPService.call_tool("getQueue", user, db, {})
    finally:
        db.close()


async def set_volume(tool_context: ToolContext, volume_percent: int) -> str:
    """Define o volume do dispositivo ativo (0 a 100)."""
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        return await SpotifyMCPService.call_tool(
            "setVolume", user, db, {"volumePercent": volume_percent}
        )
    finally:
        db.close()


async def adjust_volume(tool_context: ToolContext, adjustment: int) -> str:
    """
    Ajusta o volume relativamente (+10, -10, etc).
    Use valores positivos para aumentar e negativos para diminuir.
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        return await SpotifyMCPService.call_tool(
            "adjustVolume", user, db, {"adjustment": adjustment}
        )
    finally:
        db.close()


async def get_available_devices(tool_context: ToolContext) -> str:
    """Lista dispositivos disponíveis para conexão."""
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        return await SpotifyMCPService.call_tool("getAvailableDevices", user, db, {})
    finally:
        db.close()


async def transfer_playback(
    tool_context: ToolContext, device_id: str, play: bool = False
) -> str:
    """
    Transfere a reprodução para um novo dispositivo.

    Args:
        device_id: ID do dispositivo para onde transferir.
        play: Se deve iniciar a reprodução imediatamente no novo dispositivo.
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        args = {"deviceId": device_id, "play": play}
        return await SpotifyMCPService.call_tool("transferPlayback", user, db, args)
    finally:
        db.close()


async def set_shuffle(tool_context: ToolContext, state: bool) -> str:
    """
    Ativa ou desativa o modo aleatório (shuffle).

    Args:
        state: True para ativar, False para desativar.
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        args = {"state": state}
        return await SpotifyMCPService.call_tool("setShuffle", user, db, args)
    finally:
        db.close()


async def set_repeat_mode(
    tool_context: ToolContext, state: Literal["track", "context", "off"]
) -> str:
    """
    Define o modo de repetição.

    Args:
        state: "track" (repetir música), "context" (repetir contexto/álbum) ou "off" (desligado).
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        args = {"state": state}
        return await SpotifyMCPService.call_tool("setRepeatMode", user, db, args)
    finally:
        db.close()
