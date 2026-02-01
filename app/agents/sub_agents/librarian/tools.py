from typing import List
from google.adk.tools import ToolContext
from app.schemas.tracks import TrackResponse
from app.services.tracks import TracksService


async def search_tracks_fuzzy(
    tool_context: ToolContext, query: str, limit: int = 5, offset: int = 0
) -> List[dict]:
    """
    Busca músicas no banco de dados local por nome ou artista usando busca aproximada (fuzzy search).

    Use esta ferramenta quando o usuário fornecer um termo de busca textual (ex: "Metallica", "Avenged Sevenfold", "Gunslinger").
    A ferramenta também suporta paginação para quando o usuário solicitar "mais resultados" ou se os primeiros resultados não forem o que ele buscava.
    A busca fuzzy serve para não prejudicar a busca quando o usuário informa os nomes errados, por exemplo "avged sevefoild" e a busca traz músicas do "Avenged Sevenfold".

    Args:
        query: O termo de busca (nome da música ou artista).
        limit: Quantidade de músicas a retornar por página. Máximo recomendado: 10. (Default: 5).
        offset: Deslocamento para paginação (pula N músicas). Útil para ver os próximos resultados de uma busca anterior. (Default: 0).

    Returns:
        Uma lista de dicionários contendo os detalhes das músicas encontradas, incluindo metadados técnicos e capas.
    """
    from app.agents.sub_agents.dj.tools import _get_user_from_context

    user, db = _get_user_from_context(tool_context)
    try:
        if not user:
            return [{"error": "Usuário não autenticado."}]

        safe_limit = max(1, min(limit, 10))

        results = await TracksService.search_tracks_fuzzy(
            user, db, query, limit=safe_limit, offset=offset
        )

        tracks_dict = [TrackResponse.model_validate(t).model_dump() for t in results]
        
        tool_context.state["metadata:tracks"] = tracks_dict
        
        return tracks_dict
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()
