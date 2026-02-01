"""dj_agent: for dj tasks"""

from google.adk import Agent
from app.core.config import settings
import app.core.prompts as prompts


from app.agents.sub_agents.dj.tools import (
    play_music,
    pause_playback,
    resume_playback,
    skip_to_next,
    skip_to_previous,
    get_now_playing,
    get_queue,
    get_available_devices,
    set_volume,
    adjust_volume,
    create_playlist,
    add_tracks_to_playlist,
)


def create_dj_agent():
    return Agent(
        model=settings.MODEL,
        name="dj_agent",
        description=prompts.DJ_DESCRIPTION,
        instruction=prompts.DJ_INSTRUCTION,
        output_key="dj_output",
        tools=[
            play_music,
            pause_playback,
            resume_playback,
            skip_to_next,
            skip_to_previous,
            get_now_playing,
            get_queue,
            get_available_devices,
            set_volume,
            adjust_volume,
            create_playlist,
            add_tracks_to_playlist,
        ],
    )
