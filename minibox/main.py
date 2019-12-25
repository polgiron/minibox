import os
import urwid
from .spotify import Spotify

max_rows, max_columns = os.popen('stty size', 'r').read().split()
MAX_ROWS = int(max_rows) - 2
MAX_COLUMNS = int(max_columns)


sp = Spotify()


def unhandled_input(key):
    # queue_list_walker.append(ListEntry(key))

    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()


palette = [
    ('reverted', 'black', 'white')
]


class ButtonLabel(urwid.SelectableIcon):
    def __init__(self, text):
        curs_pos = len(text) + 1
        urwid.SelectableIcon.__init__(self, text, cursor_position=curs_pos)


class Button(urwid.WidgetWrap):
    _selectable = True
    signals = ['click']

    def __init__(self, label, callback):
        self.label = ButtonLabel(label)
        display_widget = self.label
        urwid.WidgetWrap.__init__(self, urwid.AttrMap(
            display_widget, None, focus_map='reverted'))
        urwid.connect_signal(self, 'click', callback)

    def keypress(self, size, key):
        if self._command_map[key] != urwid.ACTIVATE:
            return key

        self._emit('click')


class TrackListEntry():
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

    def play_track(self, button_widget):
        # print(self.name + ' - ' + self.uri)
        track_playing.set_text(self.label)
        sp.play_track(self.uri)

    def add_ui(self, wrapper):
        # print('Add track to list')
        wrapper.append(Button(self.label, self.play_track))


class Search(urwid.LineBox):
    def keypress(self, size, key):
        if key != 'enter':
            return super(Search, self).keypress(size, key)
        self.search(self.original_widget.edit_text)
    
    def search(self, search_value):
        results = sp.search(search_value)
        add_tracks(results, search_results_walker)



def add_tracks(tracks, wrapper):
    for i, track in enumerate(tracks):
        trackEntry = TrackListEntry(track)
        trackEntry.add_ui(wrapper)


# LEFT
queue_list_walker = urwid.SimpleFocusListWalker([])
queue_list = urwid.ListBox(queue_list_walker)
queue_wrapper = urwid.LineBox(urwid.BoxAdapter(
    queue_list, MAX_ROWS), title='Queue', title_align='left')

# SEARCH
search_wrapper = Search(urwid.Edit(''), title='Search', title_align='left')
search_results_walker = urwid.SimpleFocusListWalker([])
search_results_list = urwid.ListBox(search_results_walker)
search_results_wrapper = urwid.LineBox(urwid.BoxAdapter(
    search_results_list, MAX_ROWS - 6), title='Search results', title_align='left')
# search_results_wrapper = SearchResults(urwid.BoxAdapter(
#     search_results_list, MAX_ROWS - 6), title='Search results', title_align='left')

track_playing = urwid.Text(('No track playing'))
track_playing_wrapper = urwid.LineBox(
    track_playing, title='Currently playing', title_align='left')
right = urwid.Pile(
    [search_wrapper, search_results_wrapper, track_playing_wrapper])

columns = urwid.Columns([
    ('weight', 1, queue_wrapper),
    ('weight', 3, right)
])
main_wrapper = urwid.Filler(columns, valign='top')


def main():
    sp.init()
    sp.get_devices()

    tracks = sp.get_playlist_tracks()
    add_tracks(tracks, queue_list_walker)

    loop = urwid.MainLoop(main_wrapper, palette,
                          unhandled_input=unhandled_input)
    loop.run()
