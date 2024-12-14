import json

from mcp.server import logger
import mcp.types as types
from pydantic import Field

from .tool_model import ToolModel

class GetInfo(ToolModel):
    """Get detailed information about a Spotify item (track, album, artist, or playlist)."""

    class Schema(ToolModel.Schema):
        action: str = Field(description="Action to perform: 'get'")
        item_id: str = Field(description="ID of the item to get information about")
        qtype: str = Field(default="track", description="Type of item: 'track', 'album', 'artist', or 'playlist'. "
                                                    "If 'playlist' or 'album', returns its tracks. If 'artist',"
                                                    "returns albums and top tracks.")

    def get(self, arguments):
        logger.info(f"Getting item info with arguments: {arguments}")
        item_info = self._spotify.search.get_info(
            item_id=arguments.get("item_id"),
            qtype=arguments.get("qtype", "track")
        )
        return [types.TextContent(
            type="text",
            text=json.dumps(item_info, indent=2)
        )]

