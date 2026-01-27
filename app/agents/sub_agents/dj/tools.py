from typing import Optional, Literal
from google.adk.tools import ToolContext
from app.services.spotify_mcp import SpotifyMCPService
from app.core.database import SessionLocal
from app.models.user import User


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
    type: Optional[Literal["track", "album", "artist", "playlist"]] = None,
) -> str:
    """
    Inicia a reprodução de música, álbum, artista ou playlist no Spotify.

    Args:
        query: Termo de busca (ex: "Pink Floyd", "Despacito"). Use se não tiver URI.
        uri: URI direto do Spotify (ex: "spotify:track:...") se disponível.
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

        if query and not uri:
            # 1. Buscar a música
            search_args = {"query": query, "type": type or "track", "limit": 1}
            search_result = await SpotifyMCPService.call_tool(
                "searchSpotify", user, db, search_args
            )
            
            # 2. Extrair o ID do resultado e tocar imediatamente
            import re
            id_match = re.search(r'ID:\s*([a-zA-Z0-9]+)', search_result)
            if id_match:
                track_id = id_match.group(1)
                play_uri = f"spotify:track:{track_id}"
                await SpotifyMCPService.call_tool(
                    "playMusic", user, db, {"uri": play_uri, "type": "track"}
                )
                return f"🎵 Tocando agora! {search_result}"
            else:
                return f"Busca realizada, mas não encontrei resultado válido: {search_result}"

        args = {"uri": uri, "type": type}
        result = await SpotifyMCPService.call_tool("playMusic", user, db, args)
        return f"🎵 Tocando agora! {result}"

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


async def create_playlist(
    tool_context: ToolContext,
    name: str, 
    description: str = "", 
    public: bool = False
) -> str:
    """
    Cria uma nova playlist no Spotify.

    Args:
        name: Nome da playlist.
        description: Descrição da playlist (opcional).
        public: Se a playlist deve ser pública (default: False).
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        args = {"name": name, "description": description, "public": public}
        return await SpotifyMCPService.call_tool("createPlaylist", user, db, args)
    finally:
        db.close()


async def add_tracks_to_playlist(
    tool_context: ToolContext,
    playlist_id: str, 
    track_ids: list[str]
) -> str:
    """
    Adiciona músicas a uma playlist existente.

    Args:
        playlist_id: ID da playlist.
        track_ids: Lista de IDs das músicas (não URIs completos, apenas IDs) a serem adicionadas.
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        args = {"playlistId": playlist_id, "trackIds": track_ids}
        return await SpotifyMCPService.call_tool("addTracksToPlaylist", user, db, args)
    finally:
        db.close()


async def get_my_playlists(tool_context: ToolContext, limit: int = 20) -> str:
    """
    Lista as playlists do usuário atual. Ute quando precisa saber o ID de uma playlist pelo nome.

    Args:
        limit: Número máximo de playlists a retornar (default: 20).
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        args = {"limit": limit}
        return await SpotifyMCPService.call_tool("getMyPlaylists", user, db, args)
    finally:
        db.close()
