from typing import Dict, List, Optional, Union

from .. import utils
from .client import SpotifyClient
from .models import AlbumInfo, ArtistInfo, PlaylistInfo, QType, TrackInfo

class SearchManager:
    def __init__(self, client: SpotifyClient):
        self.client = client
        self.sp = client.sp
        self.logger = client.logger

    def search(self, query: str, qtype: Union[QType, str] = 'track', limit: int = 10) -> Dict[str, List[Union[TrackInfo, ArtistInfo, PlaylistInfo, AlbumInfo]]]:
        """
        Searches based of query term.
        - query: query term
        - qtype: the types of items to return. One or more of 'artist', 'album',  'track', 'playlist'.
                 If multiple types are desired, pass in a comma separated string; e.g. 'track,album'
        - limit: max # items to return
        """
        results = self.sp.search(q=query, limit=limit, type=qtype)
        return utils.parse_search_results(results, qtype)

    def recommendations(self, 
                       artists: Optional[List[str]] = None, 
                       tracks: Optional[List[str]] = None, 
                       limit: int = 20) -> Dict[str, List[TrackInfo]]:
        recs = self.sp.recommendations(seed_artists=artists, seed_tracks=tracks, limit=limit)
        if 'tracks' not in recs:
            return {'tracks': []}
        
        tracks: List[TrackInfo] = []
        for track in recs['tracks']:
            if parsed := utils.parse_track(track):
                tracks.append(parsed)
        return {'tracks': tracks}

    def get_info(self, item_id: str, qtype: QType = 'track') -> Optional[Union[TrackInfo, AlbumInfo, ArtistInfo, PlaylistInfo]]:
        """
        Returns more info about item.
        - item_id: id.
        - qtype: Either 'track', 'album', 'artist', or 'playlist'.
        """
        try:
            match qtype:
                case 'track':
                    track = self.sp.track(item_id)
                    return utils.parse_track(track, detailed=True)
                    
                case 'album':
                    album = self.sp.album(item_id)
                    if album_info := utils.parse_album(album, detailed=True):
                        return album_info
                    return None
                    
                case 'artist':
                    artist = self.sp.artist(item_id)
                    if not (artist_info := utils.parse_artist(artist, detailed=True)):
                        return None
                        
                    albums = self.sp.artist_albums(item_id)
                    top_tracks = self.sp.artist_top_tracks(item_id)['tracks']
                    
                    albums_and_tracks = {
                        'albums': albums,
                        'tracks': {'items': top_tracks}
                    }
                    parsed_info = utils.parse_search_results(albums_and_tracks, qtype="album,track")
                    artist_info['top_tracks'] = parsed_info.get('tracks', [])
                    artist_info['albums'] = parsed_info.get('albums', [])
                    return artist_info
                    
                case 'playlist':
                    playlist = self.sp.playlist(item_id)
                    if playlist_info := utils.parse_playlist(playlist, detailed=True):
                        return playlist_info
                    return None

            raise ValueError(f"unknown qtype {qtype}")
            
        except Exception as e:
            self.logger.error(f"Error getting info for {qtype} {item_id}: {str(e)}")
            return None
