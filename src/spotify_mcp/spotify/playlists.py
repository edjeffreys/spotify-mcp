from typing import List, Optional

from .. import utils
from .client import SpotifyClient
from .models import PlaylistInfo, PlaylistResponse

class PlaylistManager:
    def __init__(self, client: SpotifyClient):
        self.client = client
        self.sp = client.sp
        self.logger = client.logger

    def get_user_playlists(self, user: str) -> PlaylistResponse:
        """
        Returns list of playlists belonging to user
        - user: username of user
        """
        try:
            results = self.sp.user_playlists(user)
            if not results or 'items' not in results:
                return {"playlists": []}
                
            playlists: List[PlaylistInfo] = []
            for item in results['items']:
                if playlist := utils.parse_playlist(item):
                    playlists.append(playlist)
                
            return {"playlists": playlists}
        except Exception as e:
            self.logger.error(f"Error getting user playlists: {str(e)}", exc_info=True)
            raise

    @utils.validate
    def add_items(self, playlist_id: str, items: List[str]) -> None:
        """
        Adds tracks to playlist.
        - playlist_id: the id of the playlist.
        - items: a list of track URIs or URLs in the form `spotify:track:{track_id}`
        """
        formatted_items = [f"spotify:track:{id}" for id in items]
        self.sp.playlist_add_items(playlist_id, formatted_items)
        self.logger.info(f"Added {len(items)} tracks to playlist {playlist_id}")

    @utils.validate
    def remove_items(self, playlist_id: str, items: List[str]) -> None:
        """
        Removes tracks from a playlist.
        
        Args:
            playlist_id: the id of the playlist
            items: a list of track ids to remove
            
        Raises:
            SpotifyException: If the API request fails
        """
        try:
            formatted_items = [f"spotify:track:{id}" for id in items]
            self.sp.playlist_remove_all_occurrences_of_items(playlist_id, formatted_items)
            self.logger.info(f"Successfully removed {len(items)} tracks from playlist {playlist_id}")
        except Exception as e:
            self.logger.error(f"Error removing items from playlist: {str(e)}", exc_info=True)
            raise

    @utils.validate
    def get_playlist(self, playlist_id: str) -> Optional[PlaylistInfo]:
        """Get detailed information about a specific playlist"""
        try:
            playlist = self.sp.playlist(playlist_id)
            return utils.parse_playlist(playlist, detailed=True)
        except Exception as e:
            self.logger.error(f"Error getting playlist {playlist_id}: {str(e)}")
            return None
