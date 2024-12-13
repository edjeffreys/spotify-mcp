from typing import List

from mcp.server import Server, logger, stdio_server
import mcp.types as types
from spotipy import SpotifyException

from . import spotify_api
from .tools import GetInfo, Playback, Playlist, Queue, Search, User
from .tools.tool_model import ToolModel

server = Server("spotify-mcp")
spotify_client = spotify_api.Client(logger)


mcp_tools: List[ToolModel] = [
    GetInfo(spotify_client),
    Playback(spotify_client), 
    Playlist(spotify_client),
    Queue(spotify_client),
    Search(spotify_client),
    User(spotify_client),
]

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    logger.info("Listing available tools")
    tools = [tool.as_tool() for tool in mcp_tools]
    logger.info(f"Available tools: {[tool.name for tool in tools]}")
    return tools


@server.call_tool()
async def handle_call_tool(
        name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    assert name[:7] == "Spotify", f"Unknown tool: {name}"

    tool = next(iter([tool for tool in mcp_tools if type(tool).__name__ == name[7:]]), None)
    assert tool != None, f"Unknown tool: {name}"

    action: str | None = arguments.get("action")
    assert action != None, f"No arguments provided for tool: {name}"

    try:
        return tool.execute(action, arguments)

    except SpotifyException as se:
        error_msg = f"Spotify Client error occurred: {str(se)}"
        logger.error(error_msg, exc_info=True)
        return [types.TextContent(
            type="text",
            text=f"An error occurred with the Spotify Client: {str(se)}"
        )]
    except Exception as e:
        error_msg = f"Unexpected error occurred: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise


async def main():
    logger.info("Starting Spotify MCP server")
    try:
        options = server.create_initialization_options()
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server initialized successfully")
            await server.run(
                read_stream,
                write_stream,
                options
            )
    except Exception as e:
        logger.error(f"Server error occurred: {str(e)}", exc_info=True)
        raise
