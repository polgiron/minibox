import os
import spotipy
import spotipy.util as util

os.environ['SPOTIPY_CLIENT_ID'] = 'dc87388fe36544c588442d914df545bf'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'b616d8d5858b4238a566aedb55c53926'
os.environ['SPOTIPY_REDIRECT_URI'] = 'https://www.paulgiron.com'
SCOPE = 'user-library-read,user-read-playback-state,streaming,user-modify-playback-state,user-read-currently-playing'
USERNAME = 'alpaminibox@gmail.com'
DEVICE_ID = 'd72a12fcf07eab86536b205938098bb285c1a3a7'


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


class Spotify:

    def __init__(self, token, connection):
        self.token = token
        self.connection = connection

    @staticmethod
    def build():
        print('Init spotify API...')
        token = util.prompt_for_user_token(USERNAME, SCOPE)
        connection = Spotify(token, spotipy.Spotify(auth=token))

        if not token:
            raise Exception('Can\'t get token for ' + USERNAME)

        if not connection.validate_device():
            raise Exception('The device ' + DEVICE_ID + ' is unknown')

        return connection

    def validate_device(self):
        devices = self.get_devices()
        for device in devices:
            if device['id'] == DEVICE_ID:
                return True
        return False

    def get_devices(self) -> []:
        devices = self.connection.devices()
        for i, device in enumerate(devices['devices']):
            print(device['name'] + ' - ' + device['id'])
        return devices['devices']

    def get_playlist_tracks(self):
        playlist_id = '4e9GyhFqo4N9yg2Y2mbo06'
        tracks = self.connection.user_playlist_tracks('feuquibrule', playlist_id)
        return tracks['items']

    def play(self, track_uri):
        self.connection.start_playback(DEVICE_ID, None, [track_uri])

    def pause(self):
        self.connection.pause_playback(DEVICE_ID)

    @staticmethod
    def parse_tracks(tracks):
        formatted_tracks = []
        for i, track in enumerate(tracks):
            formatted_tracks.append(Track(track))
        return formatted_tracks

    def search(self, search_value):
        results = self.connection.search(q='artist:' + search_value, limit=20, type='track')
        return self.parse_tracks(results['tracks']['items'])
