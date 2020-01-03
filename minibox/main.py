import os
import urwid
from .spotify import Spotify
from enum import Enum

max_rows, max_columns = os.popen('stty size', 'r').read().split()
MAX_ROWS = int(max_rows) - 2
MAX_COLUMNS = int(max_columns)


class PlayerState(Enum):
    STOPPED = 1
    PAUSED = 2
    PLAYING = 3


class Model:
    # results = []
    queue = []
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

    def __init__(self, controller, model):
        self.controller = controller
        self.model = model
        # self.search_input = SearchInput(urwid.Edit(
        #     ''), title='Search', title_align='left')
        urwid.WidgetWrap.__init__(self, self.main_window())

    def on_search_input_keypress(self, search_input):
        self.controller.search(search_input.original_widget.edit_text)

    def search_input(self):
        w = SearchInput(urwid.Edit(''), title='Search', title_align='left')
        urwid.connect_signal(w, 'enter', self.on_search_input_keypress)
        return w

    def search_results(self):
        self.search_results_walker = urwid.SimpleListWalker([])
        search_results_list = urwid.ListBox(self.search_results_walker)
        search_results_wrapper = urwid.LineBox(urwid.BoxAdapter(
            search_results_list, MAX_ROWS - 6), title='Search results', title_align='left')
        return search_results_wrapper

    def queue(self):
        self.queue_list_walker = urwid.SimpleFocusListWalker([])
        queue_list = urwid.ListBox(self.queue_list_walker)
        queue = urwid.LineBox(urwid.BoxAdapter(
            queue_list, MAX_ROWS), title='Queue', title_align='left')
        return queue

    def player(self):
        self.currently_playing = urwid.Text(('No track playing'))
        self.player_state = urwid.Text((''))
        player = urwid.Columns([
            ('fixed', 10, self.player_state),
            self.currently_playing
        ])
        player = urwid.LineBox(player, title='Player', title_align='left')
        return player

    def update_search_results(self, results):
        self.search_results_walker.clear()
        for i, track in enumerate(results):
            track_entry = Button(
                track.label, self.controller.on_track_results_click, track)
            self.search_results_walker.append(track_entry)

    def update_queue(self):
        self.queue_list_walker.clear()
        for i, track in enumerate(self.model.queue):
            track_entry = Button(
                track.label, self.controller.on_track_queue_click, track)
            self.queue_list_walker.append(track_entry)

    def track_options_overlay(self, track):
        # play_button = Button('Play', self.controller.play, track)
        add_to_queue_button = Button(
            'Add to queue', self.controller.add_to_queue, track)
        cancel_button = Button(
            'Cancel', self.controller.cancel, None)
        overlay = urwid.Pile([
            add_to_queue_button,
            # play_button,
            cancel_button
        ])
        overlay = urwid.LineBox(overlay, title='Track options', title_align='center')
        overlay = urwid.Overlay(
            urwid.Filler(overlay), self, 'center', 20, 'middle', 4)
        return overlay

    def main_window(self):
        # Right
        right = urwid.Pile(
            [self.search_input(), self.search_results(), self.player()])

        # Columns
        columns = urwid.Columns([
            ('weight', 1, self.queue()),
            ('weight', 3, right)
        ])

        # Main wrapper
        w = urwid.Filler(columns, valign='top')

        return w


class Controller:
    def __init__(self):
        self.sp = Spotify()
        self.sp.init()
        self.model = Model()
        self.view = View(self, self.model)
        self.update_player_state(PlayerState.STOPPED)

    def search(self, search_value):
        results = self.sp.search(search_value)
        self.view.update_search_results(results)

    def update_player_state(self, state):
        self.model.player_state = state
        self.view.player_state.set_text(state.name)

    def update_currently_playing(self, label):
        self.view.currently_playing.set_text(label)

    def on_track_results_click(self, track, button_instance):
        overlay = self.view.track_options_overlay(track)
        self.loop.widget = overlay

    def on_track_queue_click(self, track, button_instance):
        print('click on track queue')

    def play_track(self, track):
        self.sp.play()
        self.update_currently_playing(track.label)
        self.update_player_state(PlayerState.PLAYING)
        # self.loop.widget = self.view

    def play_next(self):
        if len(self.model.queue) > 1:
            self.sp.next()
            self.model.queue.pop(0)
            self.view.update_queue()
            self.update_currently_playing(self.model.queue[0].label)

    def add_to_queue(self, track, button_instance):
        # print('Add to queue: ' + track.uri)
        self.model.queue.append(track)
        self.sp.add_to_queue(track)
        self.view.update_queue()
        self.loop.widget = self.view

    def cancel(self, nothing, button_instance):
        self.loop.widget = self.view

    def on_play_pause_button(self):
        if self.model.player_state == PlayerState.STOPPED and len(self.model.queue) > 0:
            self.play_track(self.model.queue[0])
        elif self.model.player_state == PlayerState.PLAYING:
            self.sp.pause()
            self.update_player_state(PlayerState.PAUSED)
        elif self.model.player_state == PlayerState.PAUSED:
            self.sp.resume()
            self.update_player_state(PlayerState.PLAYING)

    def unhandled_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        if key in ('p', 'P'):
            self.on_play_pause_button()
        if key in ('n', 'N'):
            self.play_next()

    def main(self):
        self.loop = urwid.MainLoop(
            self.view, self.view.palette, unhandled_input=self.unhandled_input)
        self.loop.run()


def main():
    Controller().main()
