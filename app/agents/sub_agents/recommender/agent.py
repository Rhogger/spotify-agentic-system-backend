"""recommender agent: for recommender tasks"""

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