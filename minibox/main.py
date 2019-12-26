import os
import urwid
from .spotify import Spotify

max_rows, max_columns = os.popen('stty size', 'r').read().split()
MAX_ROWS = int(max_rows) - 2
MAX_COLUMNS = int(max_columns)

# UPDATE_INTERVAL = 0.1

sp = Spotify()


class Model:
    results = []
    queue = []

    # def __init__(self):


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
    def __init__(self, track, currently_playing):
        self.currently_playing = currently_playing
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

    def play(self, button_widget):
        self.currently_playing.set_text(self.label)
        sp.play(self.uri)

    def button(self):
        return Button(self.label, self.play)


class SearchInput(urwid.LineBox):
    signals = ['enter']

    def keypress(self, size, key):
        if key != 'enter':
            return super(SearchInput, self).keypress(size, key)
        self._emit('enter')


class View(urwid.WidgetWrap):
    palette = [
        ('reverted', 'black', 'white')
    ]

    def __init__(self, controller):
        self.controller = controller
        # self.search_input = SearchInput(urwid.Edit(
        #     ''), title='Search', title_align='left')
        urwid.WidgetWrap.__init__(self, self.main_window())

    def on_search_input_keypress(self, search_input):
        self.controller.search(search_input.original_widget.edit_text)

    def search_input(self):
        w = SearchInput(urwid.Edit(''), title='Search', title_align='left')
        urwid.connect_signal(w, 'enter', self.on_search_input_keypress)
        return w

    def update_search_results(self, results):
        self.search_results_walker.clear()
        for i, track in enumerate(results):
            track_entry = TrackListEntry(track, self.currently_playing)
            self.search_results_walker.append(track_entry.button())

    # def exit_program(self, w):
        # raise urwid.ExitMainLoop()

    def main_window(self):
        # Search results
        self.search_results_walker = urwid.SimpleListWalker([])
        search_results_list = urwid.ListBox(self.search_results_walker)
        search_results_wrapper = urwid.LineBox(urwid.BoxAdapter(
            search_results_list, MAX_ROWS - 6), title='Search results', title_align='left')

        # Currently playing
        self.currently_playing = urwid.Text(('No track playing'))
        currently_playing_wrapper = urwid.LineBox(
            self.currently_playing, title='Currently playing', title_align='left')

        # Right
        right = urwid.Pile(
            [self.search_input(), search_results_wrapper, currently_playing_wrapper])

        # Main wrapper
        w = urwid.Filler(right, valign='top')
        return w


class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self)

    def search(self, search_value):
        results = sp.search(search_value)
        self.view.update_search_results(results)

    # def play(self, what):
    #     # print(what)
    #     # track.play()
    #     self.view.currently_playing.set_text('track.label')

    def main(self):
        self.loop = urwid.MainLoop(self.view, self.view.palette)
        self.loop.run()


def main():
    sp.init()
    # sp.get_devices()
    Controller().main()
