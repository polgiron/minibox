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
