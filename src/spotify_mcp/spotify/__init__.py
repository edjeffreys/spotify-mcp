import logging
import os
from typing import List, Optional

from dotenv import load_dotenv

from .client import SCOPES, SpotifyClient
from .models import (
    AlbumInfo,
    ArtistInfo,
    PlaylistInfo,
    PlaylistResponse,
    QType,
    QueueInfo,
    SpotifyDevice,
    TrackInfo,
)
from .playback import PlaybackManager
from .playlists import PlaylistManager
from .search import SearchManager

class Spotify:
    """Main interface for Spotify API interactions"""
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize Spotify interface
        
        If auth parameters are not provided, attempts to load them from environment variables:
        - SPOTIFY_CLIENT_ID
        - SPOTIFY_CLIENT_SECRET
        - SPOTIFY_REDIRECT_URI
        
        Args:
            client_id: Spotify API client ID
            client_secret: Spotify API client secret
            redirect_uri: OAuth redirect URI
            scopes: List of Spotify API scopes to request
            logger: Optional logger instance
        """
        # Load from environment if not provided
        if any(param is None for param in [client_id, client_secret, redirect_uri]):
            load_dotenv()
            client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID")
            client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")
            redirect_uri = redirect_uri or os.getenv("SPOTIFY_REDIRECT_URI")
            
        if not all([client_id, client_secret, redirect_uri]):
            raise ValueError(
                "Missing required authentication parameters. "
                "Either provide them directly or set them in environment variables."
            )
        
        self.client = SpotifyClient(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scopes=scopes,
            logger=logger
        )
        self.playback = PlaybackManager(self.client)
        self.playlists = PlaylistManager(self.client)
        self.search = SearchManager(self.client)
    
    @property
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated"""
        return self.client.auth_ok()
    
    def refresh_auth(self) -> None:
        """Refresh the authentication token"""
        self.client.auth_refresh()

# For easier imports
__all__ = [
    'Spotify',
    'SpotifyClient',
    'PlaybackManager',
    'PlaylistManager',
    'SearchManager',
    'QType',
    'SpotifyDevice',
    'PlaylistInfo',
    'PlaylistResponse',
    'TrackInfo',
    'QueueInfo',
    'ArtistInfo',
    'AlbumInfo',
    'SCOPES',
]
