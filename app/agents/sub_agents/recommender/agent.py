"""
recommender_agent: Especialista em descoberta e recomendação musical.
Diferente da busca por nome, este agente foca na similaridade técnica (audio features) para encontrar faixas que combinem com a "vibe" da música de referência.
Depende dos dados coletados pelo librarian_agent para realizar recomendações precisas.
"""

from google.adk import Agent
from app.core.config import settings
import app.core.prompts as prompts
from app.agents.sub_agents.recommender.tools import (
    recommend_by_features,
    )

def create_recommender_agent():
    return Agent(
        model=settings.MODEL,
        name="recommender_agent",
        description=prompts.RECOMMENDER_DESCRIPTION,
        instruction=prompts.RECOMMENDER_INSTRUCTION,
        output_key="recommender_output",
        tools=[recommend_by_features,],
    )