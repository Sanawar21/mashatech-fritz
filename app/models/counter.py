import time


class Counter:
    def __init__(self, hours: int, minutes: int, seconds: int) -> None:
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.start_time = None
        self.duration_seconds = hours * 3600 + minutes * 60 + seconds

    def is_finished(self):
        return time.time() - self.start_time >= self.duration_seconds

    def start(self):
        self.start_time = time.time()

    def reset(self):
        self.start_time = None

    def restart(self):
        self.start_time = time.time()
