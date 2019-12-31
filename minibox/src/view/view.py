import os
from enum import Enum

import urwid

from minibox.src.view.track_list_entry import TrackListEntry
from minibox.src.view.buttton import Button

max_rows, max_columns = os.popen('stty size', 'r').read().split()
MAX_COLUMNS = int(max_columns)
MAX_ROWS = int(max_rows) - 2


class PlayerState(Enum):
    PAUSED = 1
    PLAYING = 2


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

    def __init__(self, minibox):
        self.minibox = minibox
        self.currently_playing = urwid.Text('No track playing')
        self.search_results_walker = urwid.SimpleListWalker([])
        self.queue_list_walker = urwid.SimpleFocusListWalker([])
        self.player_state = urwid.Text('')
        urwid.WidgetWrap.__init__(self, self.main_window())

    def on_search_input_keypress(self, search_input):
        result = self.minibox.search(search_input.original_widget.edit_text)
        self.update_search_results(result)

    def on_track_results_click(self, track, button_instance):
        overlay = self.track_options_overlay(track)
        self.widget = overlay

    def on_track_queue_click(self, track, button_instance):
        print('click on track queue')

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
        self.currently_playing = urwid.Text('No track playing')
        player = urwid.Columns([
            ('fixed', 10, urwid.Text('')), self.currently_playing])
        player = urwid.LineBox(player, title='Player', title_align='left')
        return player

    def update_search_results(self, results):
        self.search_results_walker.clear()
        for i, track in enumerate(results):
            track_entry = TrackListEntry(track, self.on_track_results_click, self.on_track_queue_click)
            self.search_results_walker.append(
                track_entry.search_results_button())

    def update_queue(self):
        self.queue_list_walker.clear()
        for i, track in enumerate(self.minibox.model.queue):
            self.queue_list_walker.append(track.queue_button())

    def play(self, track, button_instance):
        self.view.currently_playing.set_text(track.label)
        self.player_state.set_text(PlayerState.PLAYING)
        self.widget = self.view
        self.minibox.play()

    def add_to_queue(self, track, button_instance):
        self.minibox.model.queue.append(track)
        self.view.update_queue()
        self.widget = self.view

    def cancel(self, nothing, button_instance):
        self.widget = self.view

    def track_options_overlay(self, track):
        play_button = Button('Play', self.play, track)
        add_to_queue_button = Button(
            'Add to queue', self.add_to_queue, track)
        cancel_button = Button(
            'Cancel', self.cancel, None)
        overlay = urwid.Pile([
            add_to_queue_button,
            play_button,
            cancel_button
        ])
        overlay = urwid.LineBox(overlay, title='Track options', title_align='center')
        overlay = urwid.Overlay(overlay, self, 'center', 0, 'middle', 0)
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
