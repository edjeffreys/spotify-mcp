import json
from typing import Optional

from mcp.server import logger
import mcp.types as types
from pydantic import Field

from .tool_model import ToolModel

class Playback(ToolModel):
    """Manages the current playback with the following actions:
    - get: Get information about user's current track.
    - start: Starts of resumes playback.
    - pause: Pauses current playback.
    - skip: Skips current track.
    """

    class Schema(ToolModel.Schema):
        action: str = Field(description="Action to perform: 'get', 'start', 'pause' or 'skip'.")
        track_id: Optional[str] = Field(default=None, description="Specifies track to play for 'start' action. If omitted, resumes current playback.")
        num_skips: Optional[int] = Field(default=1, description="Number of tracks to skip for `skip` action.")

    def get(self, arguments):
        logger.info("Attempting to get current track")
        curr_track = self._spotify.playback.get_current_track()
        if curr_track:
            logger.info(f"Current track retrieved: {curr_track.get('name', 'Unknown')}")
            return [types.TextContent(
                type="text",
                text=json.dumps(curr_track, indent=2)
            )]
        logger.info("No track currently playing")
        return [types.TextContent(
            type="text",
            text="No track playing."
        )]

    def start(self, arguments):
        logger.info(f"Starting playback with arguments: {arguments}")
        self._spotify.playback.start_playback(track_id=arguments.get("track_id"))
        logger.info("Playback started successfully")
        return [types.TextContent(
            type="text",
            text="Playback starting with no errors."
        )]

    def pause(self, arguments):
        logger.info("Attempting to pause playback")
        self._spotify.playback.pause_playback()
        logger.info("Playback paused successfully")
        return [types.TextContent(
            type="text",
            text="Playback paused successfully."
        )]

    def skip(self, arguments):
        num_skips = int(arguments.get("num_skips", 1))
        logger.info(f"Skipping {num_skips} tracks.")
        self._spotify.playback.skip_track(n=num_skips)
        return [types.TextContent(
            type="text",
            text="Skipped to next track."
        )]
