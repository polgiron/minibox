from minibox.src.view.buttton import Button


class TrackListEntry:
    def __init__(self, track, on_track_results_click, on_track_queue_click):
        self.on_track_queue_click = on_track_queue_click
        self.on_track_results_click = on_track_results_click
        self.artists = track.artists
        self.name = track.name
        self.uri = track.uri
        self.label = track.label

    def search_results_button(self):
        return Button(self.label, self.on_track_results_click, self)

    def queue_button(self):
        return Button(self.label, self.on_track_queue_click, self)