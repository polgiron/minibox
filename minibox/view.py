import os
import urwid
from .model import Model

max_rows, max_columns = os.popen('stty size', 'r').read().split()
MAX_ROWS = int(max_rows) - 2
MAX_COLUMNS = int(max_columns)


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
        ('pg normal', 'black', 'black'),
        ('pg complete', 'white', 'white')
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
        # self.player_state = urwid.Text((''))
        self.currently_playing = urwid.Text(('No track playing'))
        self.current_track_progress = urwid.Text(('00:00'))
        self.current_track_duration = urwid.Text(('00:00'))
        self.progress = urwid.ProgressBar('pg normal', 'pg complete', 0, 10000)
        player = urwid.Columns([
            # ('fixed', 10, self.player_state),
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
        self.progress.set_completion(
            value * 10000 / self.model.current_track.duration)
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
