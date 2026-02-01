"""curator_agent: para tarefas de curadoria e gestão de playlists"""

from google.adk import Agent
from app.core.config import settings
import app.core.prompts as prompts
# from app.agents.sub_agents.curator.tools import (
#     create_playlist,
#     delete_playlist,
#     get_playlist_tracks,
#     add_tracks_to_playlist,
# )


def create_curator_agent():
    return Agent(
        model=settings.MODEL,
        name="curator_agent",
        description=prompts.CURATOR_DESCRIPTION,
        instruction=prompts.CURATOR_INSTRUCTION,
        output_key="curator_output",
        # tools=[
        #     create_playlist,
        #     delete_playlist,
        #     get_playlist_tracks,
        #     add_tracks_to_playlist,
        # ],
    )
