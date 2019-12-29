import os
import urwid
from .spotify import Spotify
from enum import Enum

max_rows, max_columns = os.popen('stty size', 'r').read().split()
MAX_ROWS = int(max_rows) - 2
MAX_COLUMNS = int(max_columns)

# UPDATE_INTERVAL = 0.1

sp = Spotify()


class PlayerState(Enum):
    PAUSED = 1
    PLAYING = 2


class Model:
    # results = []
    # queue = []
    player_state = PlayerState['PAUSED']

    def get_player_state(self):
        return self.player_state

    def set_player_state(self, state):
        self.player_state = state


class ButtonLabel(urwid.SelectableIcon):
    def __init__(self, text):
        curs_pos = len(text) + 1
        urwid.SelectableIcon.__init__(self, text, cursor_position=curs_pos)


class Button(urwid.WidgetWrap):
    _selectable = True
    signals = ['click']

    def __init__(self, label, callback, callback_argument):
        self.label = ButtonLabel(label)
        display_widget = self.label
        urwid.WidgetWrap.__init__(self, urwid.AttrMap(
            display_widget, None, focus_map='reverted'))
        urwid.connect_signal(self, 'click', callback,
                             user_args=[callback_argument])

    def keypress(self, size, key):
        if self._command_map[key] != urwid.ACTIVATE:
            return key
        self._emit('click')


class TrackListEntry():
    def __init__(self, controller, track):
        self.controller = controller
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

    def button(self):
        return Button(self.label, self.controller.on_track_click, self)


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
            track_entry = TrackListEntry(self.controller, track)
            self.search_results_walker.append(track_entry.button())

    def on_click_play_button(self, button_instance):
        self.controller.update_player_state()

    # def play_button(self):
        # w = Button('Play', self.on_click_play_button)

    def track_options_overlay(self, track):
        play_button = Button('Play', self.controller.play, track)
        add_to_queue_button = Button('Add to queue', self.controller.add_to_queue, track)
        overlay_walker = urwid.SimpleListWalker([
            add_to_queue_button,
            play_button
        ])
        overlay_list = urwid.ListBox(overlay_walker)
        overlay = urwid.LineBox(urwid.BoxAdapter(
            overlay_list, 2), title='Track options', title_align='center')
        overlay = urwid.Overlay(
            urwid.Filler(overlay), self, 'center', 20, 'middle', 4)
        return overlay

    def main_window(self):
        # Overlay
        # self.overlay = self.track_options_overlay()

        # Search results
        self.search_results_walker = urwid.SimpleListWalker([])
        search_results_list = urwid.ListBox(self.search_results_walker)
        search_results_wrapper = urwid.LineBox(urwid.BoxAdapter(
            search_results_list, MAX_ROWS - 6), title='Search results', title_align='left')

        # Bottom
        # play_button = urwid.Button('Play', self.on_click_play_button)
        self.currently_playing = urwid.Text(('No track playing'))
        self.player_state = urwid.Text((''))
        # controls = urwid.GridFlow([
        #     # pause_button,
        #     play_button
        # ], 9, 2, 0, 'left')
        bottom = urwid.Columns([
            ('fixed', 10, self.player_state),
            self.currently_playing
        ])
        bottom = urwid.LineBox(
            bottom, title='Player', title_align='left')

        # Right
        right = urwid.Pile(
            [self.search_input(), search_results_wrapper, bottom])

        # Main wrapper
        w = urwid.Filler(right, valign='top')

        return w


class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self)
        self.update_player_state(PlayerState.PAUSED)

    def search(self, search_value):
        results = sp.search(search_value)
        self.view.update_search_results(results)

    def update_player_state(self, state):
        self.model.player_state = state
        self.view.player_state.set_text(state.name)

    def update_currently_playing(self, label):
        self.view.currently_playing.set_text(label)

    def on_track_click(self, track, button_instance):
        overlay = self.view.track_options_overlay(track)
        self.loop.widget = overlay

    def play(self, track, button_instance):
        self.update_currently_playing(track.label)
        sp.play(track.uri)
        self.update_player_state(PlayerState.PLAYING)
        self.loop.widget = self.view

    def add_to_queue(self, track, button_instance):
        print('Add to queue: ' + track.uri)
        self.loop.widget = self.view

    def unhandled_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def main(self):
        self.loop = urwid.MainLoop(
            self.view, self.view.palette, unhandled_input=self.unhandled_input)
        self.loop.run()


def main():
    sp.init()
    # sp.get_devices()
    Controller().main()
