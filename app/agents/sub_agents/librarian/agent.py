"""
librarian_agent: Especialista em pesquisa no catálogo musical.
Responsável por encontrar músicas e artistas usando busca aproximada (fuzzy search) no banco de dados local.
Atua como a ponte entre a intenção textual do usuário e os IDs técnicos do Spotify, suportando paginação de resultados.
"""

from google.adk import Agent
from app.core.config import settings
import app.core.prompts as prompts
from app.agents.sub_agents.librarian.tools import (
    search_tracks_fuzzy,
)


def create_librarian_agent():
    return Agent(
        model=settings.MODEL,
        name="librarian_agent",
        description=prompts.LIBRARIAN_DESCRIPTION,
        instruction=prompts.LIBRARIAN_INSTRUCTION,
        output_key="librarian_output",
        tools=[search_tracks_fuzzy],
    )
