import time


class Counter:
    def __init__(self, hours: int, minutes: int, seconds: int) -> None:
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.start_time = None
        self.duration_seconds = hours * 3600 + minutes * 60 + seconds

    def is_finished(self):
        if self.start_time is None:
            return False
        return time.time() - self.start_time >= self.duration_seconds

    def start(self):
        self.start_time = time.time()

    def reset(self):
        self.start_time = None

    def restart(self):
        self.start_time = time.time()

    def to_dict(self):
        return {
            "hours": self.hours,
            "minutes": self.minutes,
            "seconds": self.seconds,
            "start_time": self.start_time,
            "duration_seconds": self.duration_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict):
        obj = cls(data["hours"], data["minutes"], data["seconds"])
        obj.start_time = data["start_time"]
        obj.duration_seconds = data["duration_seconds"]
        return obj
