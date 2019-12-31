import urwid
from minibox.src.spotify.spotify import Spotify
from minibox.src.view.view import View, PlayerState


class Model:
    def __init__(self) -> None:
        self.queue = []
        self.player_state = PlayerState['PAUSED']

    def get_player_state(self):
        return self.player_state

    def set_player_state(self, state):
        self.player_state = state


class Minibox:
    def __init__(self, spotify_client, model):
        self.spotify_client = spotify_client
        self.model = model

    def search(self, search_value):
        return self.spotify_client.search(search_value)

    def play(self, track):
        self.spotify_client.play(track.uri)

    def unhandled_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()


def main():
    spotify_client = Spotify.build()
    minibox = Minibox(spotify_client, Model())
    view = View(minibox)
    loop = urwid.MainLoop(view, view.palette)
    loop.run()
