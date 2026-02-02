from typing import List, Optional
from google.adk.tools import ToolContext
from app.services.playlists import PlaylistsService
from app.agents.sub_agents.dj.tools import _get_user_from_context
from app.services.spotify_mcp import SpotifyMCPService


async def create_playlist(tool_context: ToolContext, name: str, description: Optional[str] = None, public: bool = False) -> dict:
    """
    Cria uma nova playlist no Spotify para o usuário.

    Args:
        name: Nome da nova playlist.
        description: Descrição da playlist (opcional).
        public: Se a playlist será pública (default: False).
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return {"success": False, "message": "Usuário não autenticado."}
        
        return await PlaylistsService.create_playlist_mcp(user, db, name, description, public)
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        db.close()

async def add_to_playlist(tool_context: ToolContext, playlist_id: str, track_ids: List[str], position: Optional[int] = None) -> dict:
    """
    Adiciona uma ou mais músicas (IDs) a uma playlist específica.

    Args:
        playlist_id: O ID (Spotify ID) da playlist.
        track_ids: Lista de IDs das faixas a adicionar.
        position: Posição onde inserir as faixas (opcional).
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return {"success": False, "message": "Usuário não autenticado."}
        
        return await PlaylistsService.add_tracks_to_playlist_mcp(user, db, playlist_id, track_ids, position)
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        db.close()

async def remove_from_playlist(tool_context: ToolContext, playlist_id: str, track_ids: List[str], snapshot_id: Optional[str] = None) -> dict:
    """
    Remove músicas de uma playlist.

    Args:
        playlist_id: O ID da playlist.
        track_ids: Lista de IDs das faixas a remover.
        snapshot_id: ID do snapshot da playlist (opcional).
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return {"success": False, "message": "Usuário não autenticado."}
        
        return await PlaylistsService.remove_tracks_from_playlist_mcp(user, db, playlist_id, track_ids, snapshot_id)
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        db.close()

async def list_my_playlists(tool_context: ToolContext, limit: int = 20, offset: int = 0) -> dict:
    """
    Lista as playlists do usuário autenticado.

    Args:
        limit: Quantidade de playlists a retornar (max 50).
        offset: Deslocamento para paginação.
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return {"success": False, "message": "Usuário não autenticado."}
        
        response = await PlaylistsService.get_my_playlists_mcp(user, db, limit, offset, json_output=True, md_output=False)
        data = response.model_dump()
        
        if data.get("json") and data["json"].get("items"):
            tool_context.state["metadata:playlists"] = data["json"]["items"]
            
        return data
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        db.close()

async def get_playlist_tracks(tool_context: ToolContext, playlist_id: str, limit: int = 50, offset: int = 0) -> dict:
    """
    Recupera as faixas de uma playlist específica.

    Args:
        playlist_id: O ID da playlist no Spotify.
        limit: Quantidade de faixas a retornar (max 50).
        offset: Deslocamento para paginação.
    """
    from app.services.tracks import TracksService
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return {"success": False, "message": "Usuário não autenticado."}
        
        response = await TracksService.get_playlist_tracks_mcp(user, db, playlist_id, limit, offset, json_output=True, md_output=False)
        data = response.model_dump()

        if data.get("json") and data["json"].get("items"):
            simplified_tracks = []
            for item in data["json"]["items"]:
                if item.get("track"):
                    simplified_tracks.append(item["track"])
            tool_context.state["metadata:tracks"] = simplified_tracks

        return data
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        db.close()


async def follow_playlist(tool_context: ToolContext, playlist_id: str) -> dict:
    """
    Segue (salva) uma playlist na biblioteca do usuário.

    Args:
        playlist_id: O ID da playlist no Spotify.
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return {"success": False, "message": "Usuário não autenticado."}

        return await PlaylistsService.follow_playlist_mcp(user, db, playlist_id)
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        db.close()


async def unfollow_playlist(tool_context: ToolContext, playlist_id: str) -> dict:
    """
    Remove uma playlist da biblioteca do usuário.

    Args:
        playlist_id: O ID da playlist no Spotify.
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return {"success": False, "message": "Usuário não autenticado."}

        return await PlaylistsService.unfollow_playlist_mcp(user, db, playlist_id)
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        db.close()


async def get_playlist_details(tool_context: ToolContext, playlist_id: str, calculate_duration: bool = False) -> dict:
    """
    Obtém detalhes de uma playlist (seguidores, descrição, etc.).

    Args:
        playlist_id: O ID da playlist no Spotify.
        calculate_duration: Se deve calcular a duração total das faixas.
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return {"success": False, "message": "Usuário não autenticado."}

        response = await PlaylistsService.get_playlist_details_mcp(user, db, playlist_id, calculate_duration)
        return response.model_dump()
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        db.close()


async def find_playlists_containing_track(
    tool_context: ToolContext, track_id: str
) -> str:
    """
    Verifica em quais playlists do usuário uma determinada música está presente.

    Args:
        track_id: O ID da música no Spotify.
    """
    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return "Erro: Usuário não encontrado."
        args = {"trackId": track_id}
        return await SpotifyMCPService.call_tool(
            "findPlaylistsContainingTrack", user, db, args
        )
    finally:
        db.close()