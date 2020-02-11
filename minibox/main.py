import urwid
from .utils import Utils
from .model import Model
from .model import PlayerState
from .view import View
from .spotify import Spotify

# UPDATE_INTERVAL = 0.001


class Controller():
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
        # self.view.player_state.set_text(state.name)

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
        self.view.current_track_duration.set_text(
            self.utils.format_time(track.duration))

    def on_play_pause_button(self):
        if self.model.player_state == PlayerState.STOPPED and len(self.model.queue) > 0:
            # print('PLAY')
            self.sp.play()
            self.model.current_track = self.model.queue[0]
            self.update_current_track_ui(self.model.current_track)
            self.update_player_state(PlayerState.PLAYING)
            # self.start_timer()
            self.start_seconds_timer()
        elif self.model.player_state == PlayerState.PLAYING:
            # print('PAUSE')
            self.sp.pause()
            self.update_player_state(PlayerState.PAUSED)
            # self.stop_timer()
            self.stop_seconds_timer()
        elif self.model.player_state == PlayerState.PAUSED:
            # print('RESUME')
            self.sp.resume()
            self.update_player_state(PlayerState.PLAYING)
            # self.start_timer()
            self.start_seconds_timer()

    def unhandled_input(self, key):
        # if key in ('q', 'Q'):
            # raise urwid.ExitMainLoop()
        if key in ('p', 'P'):
            self.on_play_pause_button()
        if key in ('n', 'N'):
            self.on_next_button()
        if key in ('o', 'O'):
            self.view.switch_page()

    def start_seconds_timer(self, loop=None, user_data=None):
        self.model.current_progress += 1
        self.view.current_track_progress.set_text(
            self.utils.format_time(self.model.current_progress))
        self.view.update_progress(self.model.current_progress)
        self.seconds_timer = self.loop.set_alarm_in(
            1, self.start_seconds_timer)

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
