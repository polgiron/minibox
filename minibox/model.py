from enum import Enum


class PlayerState(Enum):
    STOPPED = 1
    PAUSED = 2
    PLAYING = 3


class Model():
    # results = []
    queue = []
    player_state = PlayerState['PAUSED']
    current_track = None
    current_progress = 0

    # def get_player_state(self):
    # return self.player_state

    # def set_player_state(self, state):
    # self.player_state = state
