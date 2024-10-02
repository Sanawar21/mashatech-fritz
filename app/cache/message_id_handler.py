import time
from ..models import MessageID
from .base import BaseCache


class MessageIDCache(BaseCache):
    def __init__(self, path="data/message_ids.json") -> None:
        super().__init__(path)

    def create(self, message_id: str, ad_uid: str):
        data = MessageID(message_id, int(time.time()),
                         "pending", ad_uid).to_dict()
        super().create(data)

    def read(self, message_id: str):
        result = super().read('message_id', message_id)
        return MessageID.from_dict(result) if result else None

    def update_status(self, message_id: str, status: str):
        super().update('message_id', message_id, {'status': status})

    def delete(self, message_id: str):
        super().delete('message_id', message_id)

    def read_n_day_old(self, days: int, status: str = None):
        threshold_time = int(time.time()) - days * 86400
        if status:
            return [
                msg for msg in self.data
                if msg['timestamp'] <= threshold_time and msg['status'] == status
            ]
        else:
            return [msg for msg in self.data if msg['timestamp'] <= threshold_time]
