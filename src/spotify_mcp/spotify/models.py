from typing import List, Literal, Optional, TypedDict

QType = Literal['track', 'album', 'artist', 'playlist']

class SpotifyDevice(TypedDict):
    id: str
    is_active: bool
    name: str

class PlaylistInfo(TypedDict):
    name: str
    id: str
    owner: str
    tracks_total: int
    public: bool

class PlaylistResponse(TypedDict):
    playlists: List[PlaylistInfo]

class TrackInfo(TypedDict, total=False):
    name: str
    id: str
    artist: str
    is_playing: bool

class QueueInfo(TypedDict):
    currently_playing: Optional[TrackInfo]
    queue: List[TrackInfo]

class ArtistInfo(TypedDict):
    name: str
    id: str
    genres: List[str]
    popularity: int
    top_tracks: List[TrackInfo]
    albums: List[dict]  # TODO might want to create an AlbumInfo type

class AlbumInfo(TypedDict):
    name: str
    id: str
    artist: str
    release_date: str
    total_tracks: int
