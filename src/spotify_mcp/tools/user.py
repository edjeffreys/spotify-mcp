import json

from mcp.server import logger
import mcp.types as types
from pydantic import Field

from .tool_model import ToolModel

class User(ToolModel):
    """Search for playlists belonging to the user on Spotify.
    - get: get a list of playlists that belong to the user"""

    class Schema(ToolModel.Schema):
        action: str = Field(description="Action to perform: 'get'.")
        user: str = Field(description="Username of user")

    def get(self, arguments):
        user = arguments.get("user")
        if not user:
            logger.error("user is required for get action.")
            return [types.TextContent(
                type="text",
                text="user is required for get action"
            )]
        playlists = self._spotify_client.get_user_playlists(user) 
        return [types.TextContent(
            type="text",
            text=json.dumps(playlists, indent=2)
        )]
