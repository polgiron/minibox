import os
import urwid
from .spotify import Spotify
from enum import Enum

max_rows, max_columns = os.popen('stty size', 'r').read().split()
MAX_ROWS = int(max_rows) - 2
MAX_COLUMNS = int(max_columns)

UPDATE_INTERVAL = 0.001


class Utils():
    def format_time(self, seconds: int):
        minutes = seconds // 60
        seconds = seconds - minutes * 60
        minutes = str(minutes)
        seconds = str(seconds)
        if len(minutes) < 2:
            minutes = '0' + str(minutes)
        if len(seconds) < 2:
            seconds = '0' + str(seconds)
        return minutes + ':' + seconds


class PlayerState(Enum):
    STOPPED = 1
    PAUSED = 2
    PLAYING = 3


class Model:
    # results = []
    queue = []
    player_state = PlayerState['PAUSED']
    current_progress = 0

    # def get_player_state(self):
        # return self.player_state

    # def set_player_state(self, state):
        # self.player_state = state


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
        ('reverted', 'black', 'white'),
        ('pg normal', 'white', 'black', 'standout'),
        ('pg complete', 'white', 'dark magenta')
    ]

    def __init__(self, controller, model):
        self.controller = controller
        self.model = model
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
            search_results_list, MAX_ROWS - 7), title='Search results', title_align='left')
        return search_results_wrapper

    def queue(self):
        self.queue_list_walker = urwid.SimpleFocusListWalker([])
        queue_list = urwid.ListBox(self.queue_list_walker)
        queue = urwid.LineBox(urwid.BoxAdapter(
            queue_list, MAX_ROWS), title='Queue', title_align='left')
        return queue

    def player(self):
        self.player_state = urwid.Text((''))
        self.currently_playing = urwid.Text(('No track playing'))
        self.current_track_progress = urwid.Text(('00:00'))
        self.current_track_duration = urwid.Text(('00:00'))
        self.progress = urwid.ProgressBar('pg normal', 'pg complete', 0, 10000)
        player = urwid.Columns([
            ('fixed', 10, self.player_state),
            urwid.Pile([
                urwid.Columns([
                    ('fixed', 5, self.current_track_progress),
                    ('fixed', 1, urwid.Text('/')),
                    ('fixed', 5, self.current_track_duration),
                    ('fixed', 3, urwid.Text(' | ')),
                    self.currently_playing
                ]),
                self.progress
            ])
        ])
        player = urwid.LineBox(player, title='Player', title_align='left')
        return player
    
    def update_progress(self, value):
        self.progress.set_completion(value)
        # self.progress.render((1, ))

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
        overlay = urwid.LineBox(
            overlay, title='Track options', title_align='center')
        overlay = urwid.Overlay(
            urwid.Filler(overlay), self, 'center', 20, 'middle', 4)
        return overlay

    def main_window(self):
        # Right
        right = urwid.Pile([
            self.search_input(),
            self.search_results(),
            self.player()
        ])

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
        self.utils = Utils()
        self.view = View(self, self.model)
        self.timer = None
        self.seconds_timer = None
        self.update_player_state(PlayerState.STOPPED)

    def search(self, search_value):
        results = self.sp.search(search_value)
        self.view.update_search_results(results)

    def update_player_state(self, state):
        self.model.player_state = state
        self.view.player_state.set_text(state.name)

    def on_track_results_click(self, track, button_instance):
        overlay = self.view.track_options_overlay(track)
        self.loop.widget = overlay

    def on_track_queue_click(self, track, button_instance):
        print('click on track queue')

    def on_next_button(self):
        if len(self.model.queue) > 1:
            self.model.current_progress = 0
            self.sp.next()
            self.model.queue.pop(0)
            self.view.update_queue()
            self.update_current_track_ui(self.model.queue[0])

    def add_to_queue(self, track, button_instance):
        self.model.queue.append(track)
        self.sp.add_to_queue(track)
        self.view.update_queue()
        self.loop.widget = self.view

    def cancel(self, nothing, button_instance):
        self.loop.widget = self.view

    def update_current_track_ui(self, track):
        self.view.currently_playing.set_text(track.label)
        self.view.current_track_duration.set_text(self.utils.format_time(track.duration))

    def on_play_pause_button(self):
        if self.model.player_state == PlayerState.STOPPED and len(self.model.queue) > 0:
            print('PLAY')
            self.sp.play()
            self.update_current_track_ui(self.model.queue[0])
            self.update_player_state(PlayerState.PLAYING)
            # self.start_timer()
            self.start_seconds_timer()
        elif self.model.player_state == PlayerState.PLAYING:
            print('PAUSE')
            self.sp.pause()
            self.update_player_state(PlayerState.PAUSED)
            # self.stop_timer()
            self.stop_seconds_timer()
        elif self.model.player_state == PlayerState.PAUSED:
            print('RESUME')
            self.sp.resume()
            self.update_player_state(PlayerState.PLAYING)
            # self.start_timer()
            self.start_seconds_timer()

    def unhandled_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        if key in ('p', 'P'):
            self.on_play_pause_button()
        if key in ('n', 'N'):
            self.on_next_button()

    def start_seconds_timer(self, loop=None, user_data=None):
        self.model.current_progress += 1
        self.view.current_track_progress.set_text(
            self.utils.format_time(self.model.current_progress))
        self.seconds_timer = self.loop.set_alarm_in(1, self.start_seconds_timer)

    # def start_timer(self, loop=None, user_data=None):
    #     self.model.current_progress += 1
    #     self.view.update_progress(self.model.current_progress)
    #     self.timer = self.loop.set_alarm_in(
    #         UPDATE_INTERVAL, self.start_timer)

    def stop_seconds_timer(self):
        if self.seconds_timer:
            self.loop.remove_alarm(self.seconds_timer)
        self.seconds_timer = None

    # def stop_timer(self):
    #     if self.timer:
    #         self.loop.remove_alarm(self.timer)
    #     self.timer = None

    def main(self):
        self.loop = urwid.MainLoop(
            self.view, self.view.palette, unhandled_input=self.unhandled_input)
        self.loop.run()


def main():
    Controller().main()
