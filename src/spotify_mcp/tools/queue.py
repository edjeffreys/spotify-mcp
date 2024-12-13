import json
from typing import Optional

from mcp.server import logger
import mcp.types as types
from pydantic import Field

from .tool_model import ToolModel

class Queue(ToolModel):
    """Manage the playback queue - get the queue or add tracks."""

    class Schema(ToolModel.Schema):
        action: str = Field(description="Action to perform: 'add' or 'get'.")
        track_id: Optional[str] = Field(default=None, description="Track ID to add to queue (required for add action)")

    def add(self, arguments):
        track_id = arguments.get("track_id")
        if not track_id:
            logger.error("track_id is required for add to queue.")
            return [types.TextContent(
                type="text",
                text="track_id is required for add action"
            )]
        self._spotify_client.add_to_queue(track_id)
        return [types.TextContent(
            type="text",
            text=f"Track added to queue successfully."
        )]

    def get(self, arguments):
        queue = self._spotify_client.get_queue()
        return [types.TextContent(
            type="text",
            text=json.dumps(queue, indent=2)
        )]
