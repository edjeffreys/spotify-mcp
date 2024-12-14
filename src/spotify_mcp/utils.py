from collections import defaultdict
import functools
from typing import Optional, Dict, List, Callable, TypeVar, Tuple, Any, cast, Union
from urllib.parse import quote

from .spotify.models import (
    TrackInfo, 
    ArtistInfo, 
    PlaylistInfo, 
    AlbumInfo,
    QType
)

T = TypeVar('T')

def parse_track(track_item: Dict[str, Any], detailed: bool = False) -> Optional[TrackInfo]:
    if not track_item:
        return None
    narrowed_item: TrackInfo = {
        'name': track_item['name'],
        'id': track_item['id'],
    }

    if 'is_playing' in track_item:
        narrowed_item['is_playing'] = track_item['is_playing']

    if detailed:
        narrowed_item['album'] = parse_album(track_item.get('album'))
        for k in ['track_number', 'duration_ms']:
            if k in track_item:
                narrowed_item[k] = track_item[k]

    if not track_item.get('is_playable', True):
        narrowed_item['is_playable'] = False

    artists = [a['name'] for a in track_item['artists']]
    if detailed:
        artists = [parse_artist(a) for a in track_item['artists']]

    if len(artists) == 1:
        narrowed_item['artist'] = artists[0] if isinstance(artists[0], str) else artists[0]['name']
    else:
        narrowed_item['artists'] = artists

    return narrowed_item

def parse_artist(artist_item: Dict[str, Any], detailed: bool = False) -> Optional[ArtistInfo]:
    if not artist_item:
        return None
    narrowed_item: ArtistInfo = {
        'name': artist_item['name'],
        'id': artist_item['id'],
        'genres': artist_item.get('genres', []),
        'popularity': artist_item.get('popularity', 0),
        'top_tracks': [],
        'albums': []
    }
    
    return narrowed_item

def parse_playlist(playlist_item: Dict[str, Any], detailed: bool = False) -> Optional[PlaylistInfo]:
    if not playlist_item:
        return None
    narrowed_item: PlaylistInfo = {
        'name': playlist_item['name'],
        'id': playlist_item['id'],
        'owner': playlist_item['owner']['display_name'],
        'tracks_total': playlist_item['tracks']['total'],
        'public': playlist_item.get('public', False)
    }
    
    return narrowed_item

def parse_album(album_item: Dict[str, Any], detailed: bool = False) -> Optional[AlbumInfo]:
    if not album_item:
        return None
        
    narrowed_item: AlbumInfo = {
        'name': album_item['name'],
        'id': album_item['id'],
        'artist': '',  # Will be set below
        'release_date': album_item.get('release_date', ''),
        'total_tracks': album_item.get('total_tracks', 0)
    }

    artists = [a['name'] for a in album_item['artists']]
    if len(artists) == 1:
        narrowed_item['artist'] = artists[0]
    else:
        narrowed_item['artist'] = ', '.join(artists)

    return narrowed_item

def parse_search_results(
    results: Dict[str, Any], 
    qtype: Union[QType, str]
) -> Dict[str, List[Union[TrackInfo, ArtistInfo, PlaylistInfo, AlbumInfo]]]:
    _results: Dict[str, List[Any]] = defaultdict(list)

    for q in qtype.split(","):
        match q:
            case "track":
                for item in results['tracks']['items']:
                    if not item: continue
                    if parsed := parse_track(item):
                        _results['tracks'].append(parsed)
            case "artist":
                for item in results['artists']['items']:
                    if not item: continue
                    if parsed := parse_artist(item):
                        _results['artists'].append(parsed)
            case "playlist":
                for item in results['playlists']['items']:
                    if not item: continue
                    if parsed := parse_playlist(item):
                        _results['playlists'].append(parsed)
            case "album":
                for item in results['albums']['items']:
                    if not item: continue
                    if parsed := parse_album(item):
                        _results['albums'].append(parsed)
            case _:
                raise ValueError(f"unknown qtype {qtype}")

    return dict(_results)

def build_search_query(
    base_query: str,
    artist: Optional[str] = None,
    track: Optional[str] = None,
    album: Optional[str] = None,
    year: Optional[str] = None,
    year_range: Optional[Tuple[int, int]] = None,
    genre: Optional[str] = None,
    is_hipster: bool = False,
    is_new: bool = False
) -> str:
    """
    Build a search query string with optional filters.
    """
    filters = []

    if artist:
        filters.append(f"artist:{artist}")
    if track:
        filters.append(f"track:{track}")
    if album:
        filters.append(f"album:{album}")
    if year:
        filters.append(f"year:{year}")
    if year_range:
        filters.append(f"year:{year_range[0]}-{year_range[1]}")
    if genre:
        filters.append(f"genre:{genre}")
    if is_hipster:
        filters.append("tag:hipster")
    if is_new:
        filters.append("tag:new")

    query_parts = [base_query] + filters
    return quote(" ".join(query_parts))

def validate(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator for Spotify API methods that handles authentication validation.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Handle authentication via the client
        if not self.client.auth_ok():
            self.client.auth_refresh()
        return func(self, *args, **kwargs)
    return wrapper
