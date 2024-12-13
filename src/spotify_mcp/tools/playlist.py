from typing import List

from mcp.server import logger
import mcp.types as types
from pydantic import Field

from .tool_model import ToolModel

class Playlist(ToolModel):
    """Manage a playlist with the following actions:
    - add: adds a list of tracks to a playlist"""

    class Schema(ToolModel.Schema):
        action: str = Field(description="Action to perform: 'add', 'remove'.")
        playlist_id: str = Field(description="ID of the playlist to add items to")
        items: List[str] = Field(description="a list of tracks to add to the playlist`")

    def add(self, arguments):
        playlist_id = arguments.get("playlist_id")
        items = arguments.get("items")
        if not playlist_id:
            logger.error("playlist_id is required for add action.")
            return [types.TextContent(
                type="text",
                text="playlist_id is required for add action"
            )]
        self._spotify_client.playlist_add_items(playlist_id, items)
        return [types.TextContent(
            type="text",
            text=f"Items added to playlist successfully."
        )]

    def remove(self, arguments):
        playlist_id = arguments.get("playlist_id")
        items = arguments.get("items")
        if not playlist_id:
            logger.error("playlist_id is required for remove action.")
            return [types.TextContent(
                type="text",
                text="playlist_id is required for remove action"
            )]
        if not items:
            logger.error("items list is required for remove action.")
            return [types.TextContent(
                type="text",
                text="items list is required for remove action"
            )]
            
        self._spotify_client.playlist_remove_items(playlist_id, items)
        return [types.TextContent(
            type="text",
            text=f"Items removed from playlist successfully."
        )]
