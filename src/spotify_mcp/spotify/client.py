import logging
from typing import List, Optional

import spotipy
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth

SCOPES = [
    # spotify connect
    "user-read-currently-playing",
    "user-read-playback-state",
    "user-read-currently-playing",
    # playback
    "app-remote-control",
    "streaming",
    # playlists
    "playlist-read-private",
    "playlist-read-collaborative",
    "playlist-modify-private",
    "playlist-modify-public",
    # listening history
    "user-read-playback-position",
    "user-top-read",
    "user-read-recently-played",
    # library
    "user-library-modify",
    "user-library-read",
]

class SpotifyClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: Optional[List[str]] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """Initialize Spotify client with necessary permissions
        
        Args:
            client_id: Spotify API client ID
            client_secret: Spotify API client secret
            redirect_uri: OAuth redirect URI
            scopes: List of Spotify API scopes to request. If None, uses default scopes
            logger: Optional logger instance. If None, creates a new logger
        """
        self.logger = logger or logging.getLogger(__name__)
        
        scope = ",".join(scopes if scopes is not None else SCOPES)
        
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                scope=scope,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri
            ))
            self.auth_manager: SpotifyOAuth = self.sp.auth_manager
            self.cache_handler: CacheFileHandler = self.auth_manager.cache_handler
        except Exception as e:
            self.logger.error(f"Failed to initialize Spotify client: {str(e)}", exc_info=True)
            raise

    def auth_ok(self) -> bool:
        """Check if the current authentication token is valid"""
        try:
            result = self.auth_manager.is_token_expired(self.cache_handler.get_cached_token())
            self.logger.info(f"Auth check result: {'valid' if not result else 'expired'}")
            return result
        except Exception as e:
            self.logger.error(f"Error checking auth status: {str(e)}", exc_info=True)
            raise

    def auth_refresh(self) -> None:
        """Refresh the authentication token"""
        self.auth_manager.validate_token(self.cache_handler.get_cached_token())
