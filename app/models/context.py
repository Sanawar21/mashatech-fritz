from io import TextIOWrapper
from .counter import Counter
import queue
import json


class Context:
    def __init__(self,
                 kl_prev_ads: list,
                 pending_msgs_queue: queue.Queue,
                 offers_sent_count: int,
                 status_check_counter: Counter,
                 offers_reset_counter: Counter,
                 pending_deletion_counter: Counter,
                 accepted_deletion_counter: Counter,
                 catalog_refresh_counter: Counter,
                 self_connect_counter: Counter
                 ) -> None:
        self.kl_prev_ads = kl_prev_ads
        self.pending_msgs_queue = pending_msgs_queue
        self.offers_sent_count = offers_sent_count
        self.status_check_counter = status_check_counter
        self.offers_reset_counter = offers_reset_counter
        self.pending_deletion_counter = pending_deletion_counter
        self.accepted_deletion_counter = accepted_deletion_counter
        self.catalog_refresh_counter = catalog_refresh_counter
        self.self_connect_counter = self_connect_counter

    @classmethod
    def new(cls):
        status_check_counter = Counter(0, 5, 0)
        offers_reset_counter = Counter(1, 0, 0)
        pending_deletion_counter = Counter(48, 0, 0)
        accepted_deletion_counter = Counter(24, 0, 0)
        catalog_refresh_counter = Counter(0, 5, 0)
        self_connect_counter = Counter(0, 5, 0)
        kl_prev_ads = []
        pending_msgs_queue = queue.Queue()
        offers_sent_count = 0
        obj = cls(
            kl_prev_ads,
            pending_msgs_queue,
            offers_sent_count,
            status_check_counter,
            offers_reset_counter,
            pending_deletion_counter,
            accepted_deletion_counter,
            catalog_refresh_counter,
            self_connect_counter
        )
        return obj

    @classmethod
    def from_json(cls, data: str):
        return cls.from_dict(json.loads(data))

    @classmethod
    def from_dict(cls, data: dict):
        kl_prev_ads = data.get("kl_prev_ads")

        pending_msgs_queue = queue.Queue()
        for item in data.get("pending_msgs_queue", []):
            pending_msgs_queue.put(item)

        offers_sent_count = data.get("offers_sent_count")
        status_check_counter = Counter.from_dict(
            data.get("status_check_counter"))
        offers_reset_counter = Counter.from_dict(
            data.get("offers_reset_counter"))
        pending_deletion_counter = Counter.from_dict(
            data.get("pending_deletion_counter"))
        accepted_deletion_counter = Counter.from_dict(
            data.get("accepted_deletion_counter"))
        catalog_refresh_counter = Counter.from_dict(
            data.get("catalog_refresh_counter"))
        self_connect_counter = Counter.from_dict(
            data.get("self_connect_counter"))

        return cls(
            kl_prev_ads,
            pending_msgs_queue,
            offers_sent_count,
            status_check_counter,
            offers_reset_counter,
            pending_deletion_counter,
            accepted_deletion_counter,
            catalog_refresh_counter,
            self_connect_counter
        )

    @classmethod
    def from_file(cls, file: TextIOWrapper):
        data = eval(file.read())
        return cls.from_dict(data)

    def to_json(self):
        return json.dumps({
            "kl_prev_ads": self.kl_prev_ads,
            "pending_msgs_queue": list(self.pending_msgs_queue.queue),
            "offers_sent_count": self.offers_sent_count,
            "status_check_counter": self.status_check_counter.to_dict(),
            "offers_reset_counter": self.offers_reset_counter.to_dict(),
            "pending_deletion_counter": self.pending_deletion_counter.to_dict(),
            "accepted_deletion_counter": self.accepted_deletion_counter.to_dict(),
            "catalog_refresh_counter": self.catalog_refresh_counter.to_dict(),
            "self_connect_counter": self.self_connect_counter.to_dict()
        })

    def save(self, file: TextIOWrapper):
        file.write(self.to_json())

    def start_counters(self):
        self.status_check_counter.start()
        self.offers_reset_counter.start()
        self.pending_deletion_counter.start()
        self.accepted_deletion_counter.start()
        self.catalog_refresh_counter.start()
        self.self_connect_counter.start()
