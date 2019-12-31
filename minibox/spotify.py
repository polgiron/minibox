import sys
import os
import json
import spotipy
import spotipy.util as util


os.environ['SPOTIPY_CLIENT_ID'] = 'dc87388fe36544c588442d914df545bf'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'b616d8d5858b4238a566aedb55c53926'
os.environ['SPOTIPY_REDIRECT_URI'] = 'https://www.paulgiron.com'


class Track():
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


class Spotify():
    SCOPE = 'user-library-read,user-read-playback-state,streaming,user-modify-playback-state,user-read-currently-playing'
    # USERNAME = 'feuquibrule'
    USERNAME = 'alpaminibox@gmail.com'
    DEVICE_ID = '1670ecb14c549253cb5ac572c99706373b1712f9'

    # def __init__(self):
        # self.hello = 'Hello self'

    def init(self):
        print('Init spotify API...')
        self.token = util.prompt_for_user_token(self.USERNAME, self.SCOPE)

        if self.token:
            self.sp = spotipy.Spotify(auth=self.token)

        else:
            print('Can\'t get token for', self.USERNAME)

    def get_devices(self):
        devices = self.sp.devices()
        # print(devices['devices'])
        for i, device in enumerate(devices['devices']):
            # print('----------')
            print(device['name'] + ' - ' + device['id'])
        return devices['devices']

    def get_playlist_tracks(self):
        playlist_id = '4e9GyhFqo4N9yg2Y2mbo06'
        tracks = self.sp.user_playlist_tracks('feuquibrule', playlist_id)
        return tracks['items']

    def play(self, track_uri):
        self.sp.start_playback(self.DEVICE_ID, None, [track_uri])

    def pause(self):
        self.sp.pause_playback(self.DEVICE_ID)

    def search(self, search_value):
        results = self.sp.search(q='artist:' + search_value, limit=20, type='track')
        return self.parse_tracks(results['tracks']['items'])

    def parse_tracks(self, tracks):
        formatted_tracks = []
        for i, track in enumerate(tracks):
            formatted_tracks.append(Track(track))
        return formatted_tracks
