"""Agent base class"""

from app.agents.sub_agents.librarian.agent import create_librarian_agent
import app.core.prompts as prompts
from google.adk.agents import LlmAgent
from app.core.config import settings

orchestrator = LlmAgent(
    name="orchestrator",
    model=settings.MODEL,
    description=prompts.ORCHESTRATOR_DESCRIPTION,
    instruction=prompts.ORCHESTRATOR_INSTRUCTION,
    sub_agents=[
        create_librarian_agent(),
    ],
)

root_agent = orchestrator
