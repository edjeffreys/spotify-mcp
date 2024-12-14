import json
from typing import Optional

from mcp.server import logger
import mcp.types as types
from pydantic import Field

from .tool_model import ToolModel

class Search(ToolModel):
    """Search for tracks, albums, artists, or playlists on Spotify."""

    class Schema(ToolModel.Schema):
        action: str = Field(description="Action to perform: 'search'.")
        query: str = Field(description="query term")
        qtype: Optional[str] = Field(default="track", description="Type of items to search for (track, album, artist, playlist, or comma-separated combination)")
        limit: Optional[int] = Field(default=10, description="Maximum number of items to return")

    def search(self, arguments):
        logger.info(f"Performing search with arguments: {arguments}")
        search_results = self._spotify.search.search(
            query=arguments.get("query", ""),
            qtype=arguments.get("qtype", "track"),
            limit=arguments.get("limit", 10)
        )
        logger.info("Search completed successfully")
        return [types.TextContent(
            type="text",
            text=json.dumps(search_results, indent=2)
        )]

