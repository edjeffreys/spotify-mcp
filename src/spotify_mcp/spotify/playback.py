from typing import Any, Dict, List, Optional, cast

from .. import utils
from .client import SpotifyClient
from .models import QueueInfo, SpotifyDevice, TrackInfo

class PlaybackManager:
    def __init__(self, client: SpotifyClient):
        self.client = client
        self.sp = client.sp
        self.logger = client.logger

    def get_current_track(self) -> Optional[TrackInfo]:
        """Get information about the currently playing track"""
        try:
            current = self.sp.current_user_playing_track()
            if not current:
                self.logger.info("No playback session found")
                return None
            if current.get('currently_playing_type') != 'track':
                self.logger.info("Current playback is not a track")
                return None

            if not (track_info := utils.parse_track(current['item'])):
                return None

            if 'is_playing' in current:
                track_info['is_playing'] = current['is_playing']

            self.logger.info(
                f"Current track: {track_info.get('name', 'Unknown')} by {track_info.get('artist', 'Unknown')}")
            return track_info
        except Exception as e:
            self.logger.error("Error getting current track info", exc_info=True)
            raise e

    @utils.validate
    def start_playback(self, track_id: Optional[str] = None, device: Optional[SpotifyDevice] = None) -> Optional[Dict[str, Any]]:
        try:
            if not track_id:
                if self.is_track_playing():
                    self.logger.info("No track_id provided and playback already active.")
                    return None
                if not self.get_current_track():
                    raise ValueError("No track_id provided and no current playback to resume.")

            uris = [f'spotify:track:{track_id}'] if track_id else None
            device_id = device.get('id') if device else None

            result = self.sp.start_playback(uris=uris, device_id=device_id)
            self.logger.info(f"Playback started successfully{' for track_id: ' + track_id if track_id else ''}")
            return result
        except Exception as e:
            self.logger.error(f"Error starting playback: {str(e)}", exc_info=True)
            raise e

    @utils.validate
    def pause_playback(self, device: Optional[SpotifyDevice] = None) -> None:
        playback = self.sp.current_playback()
        if playback and playback.get('is_playing'):
            self.sp.pause_playback(device.get('id') if device else None)

    @utils.validate
    def get_queue(self, device: Optional[SpotifyDevice] = None) -> QueueInfo:
        queue_info = self.sp.queue()
        self.logger.info(f"currently playing keys {queue_info['currently_playing'].keys()}")

        current_track = self.get_current_track()
        parsed_queue: List[TrackInfo] = []
        
        for track in queue_info.pop('queue', []):
            if parsed := utils.parse_track(track):
                parsed_queue.append(parsed)

        return {
            'currently_playing': current_track,
            'queue': parsed_queue
        }

    @utils.validate
    def add_to_queue(self, track_id: str, device: Optional[SpotifyDevice] = None) -> None:
        """
        Adds track to queue.
        
        Args:
            track_id: ID of track to add to queue
            device: Optional device to add the track to. If None, uses current active device
            
        Raises:
            SpotifyException: If the API request fails or no active device is found
        """
        try:
            uri = f'spotify:track:{track_id}'
            device_id = device.get('id') if device else None
            
            self.sp.add_to_queue(uri, device_id=device_id)
            self.logger.info(f"Added track {track_id} to queue")
        except Exception as e:
            self.logger.error(f"Error adding track to queue: {str(e)}", exc_info=True)
            raise e

    def is_track_playing(self) -> bool:
        curr_track = self.get_current_track()
        if not curr_track:
            return False
        return curr_track.get('is_playing', False)

    def skip_track(self, n: int = 1) -> None:
        for _ in range(n):
            self.sp.next_track()

    def previous_track(self) -> None:
        self.sp.previous_track()

    def get_devices(self) -> List[SpotifyDevice]:
        return cast(List[SpotifyDevice], self.sp.devices()['devices'])

    def is_active_device(self) -> bool:
        return any(device.get('is_active', False) for device in self.get_devices())

    def _get_candidate_device(self) -> Optional[SpotifyDevice]:
        devices = self.get_devices()
        if not devices:
            return None
            
        for device in devices:
            if device.get('is_active'):
                return device
                
        self.logger.info(f"No active device, assigning {devices[0]['name']}.")
        return devices[0]
