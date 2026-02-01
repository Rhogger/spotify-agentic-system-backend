"""
curator_agent: Especialista em gestão de biblioteca e playlists.
Responsável por criar, organizar e modificar as coleções musicais do usuário diretamente no Spotify.
"""

from google.adk import Agent
from app.core.config import settings
import app.core.prompts as prompts
from app.agents.sub_agents.curator.tools import (
    create_playlist,
    add_to_playlist,
    remove_from_playlist,
    list_my_playlists,
    get_playlist_tracks,
    follow_playlist,
    unfollow_playlist,
    get_playlist_details,
)


def create_curator_agent():
    return Agent(
        model=settings.MODEL,
        name="curator_agent",
        description=prompts.CURATOR_DESCRIPTION,
        instruction=prompts.CURATOR_INSTRUCTION,
        output_key="curator_output",
        tools=[
            create_playlist,
            add_to_playlist,
            remove_from_playlist,
            list_my_playlists,
            get_playlist_tracks,
            follow_playlist,
            unfollow_playlist,
            get_playlist_details,
        ],
    )
