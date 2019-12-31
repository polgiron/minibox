import os
import spotipy
import spotipy.util as util

os.environ['SPOTIPY_CLIENT_ID'] = 'dc87388fe36544c588442d914df545bf'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'b616d8d5858b4238a566aedb55c53926'
os.environ['SPOTIPY_REDIRECT_URI'] = 'https://www.paulgiron.com'
SCOPE = 'user-library-read,user-read-playback-state,streaming,user-modify-playback-state,user-read-currently-playing'
USERNAME = 'alpaminibox@gmail.com'
DEVICE_ID = '1670ecb14c549253cb5ac572c99706373b1712f9'

class Track:
    def __init__(self, track):
        if track.get('track'):
            track = track['track']
        else:
            track = track
        artists = []
        for i, artist in enumerate(track['artists']):
            artists.append(artist['name'])
        self.artists = ', '.join(artists)
        self.name = track['name']
        self.uri = track['uri']
        self.label = self.artists + ' - ' + self.name


def parse_tracks(tracks):
    formatted_tracks = []
    for i, track in enumerate(tracks):
        formatted_tracks.append(Track(track))
    return formatted_tracks


class Spotify:

    def init(self):
        print('Init spotify API...')
        self.token = util.prompt_for_user_token(USERNAME, SCOPE)

        if self.token:
            self.sp = spotipy.Spotify(auth=self.token)
            if DEVICE_ID not in self.get_devices():
                raise Exception('The device ' + DEVICE_ID + ' is unknown')

        else:
            print('Can\'t get token for', USERNAME)

    def get_devices(self) -> [str]:
        devices = self.sp.devices()
        for i, device in enumerate(devices['devices']):
            # print('----------')
            print(device['name'] + ' - ' + device['id'])
        return devices['devices']

    def get_playlist_tracks(self):
        playlist_id = '4e9GyhFqo4N9yg2Y2mbo06'
        tracks = self.sp.user_playlist_tracks('feuquibrule', playlist_id)
        return tracks['items']

    def play(self, track_uri):
        self.sp.start_playback(DEVICE_ID, None, [track_uri])

    def pause(self):
        self.sp.pause_playback(DEVICE_ID)

    def search(self, search_value):
        results = self.sp.search(q='artist:' + search_value, limit=20, type='track')
        return parse_tracks(results['tracks']['items'])
