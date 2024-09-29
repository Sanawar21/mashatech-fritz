import json
import time
from .message_id import MessageID


class MessageIDCache:
    def __init__(self, path="data/data.json") -> None:
        self.path = path
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self.__load_data()
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.__save_data()

    def __load_data(self):
        try:
            with open(self.path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def __save_data(self):
        with open(self.path, 'w') as file:
            json.dump(self._data, file, indent=4)

    def create(self, message_id: str, ad_id: int):
        self.data.append(
            MessageID(message_id, int(time.time()), "pending", ad_id)
            .to_dict()
        )
        self.__save_data()

    def read(self, message_id: str):
        for msg in self.data:
            if msg['message_id'] == message_id:
                return MessageID.from_dict(msg)
        return None

    def update_status(self, message_id: str, status: str):
        for msg in self.data:
            if msg['message_id'] == message_id:
                msg['status'] = status
                break
        self.__save_data()

    def delete(self, message_id: str):
        self.data = [
            msg for msg in self.data if msg['message_id'] != message_id
        ]

    def clear_data(self):
        self.data = []

    def read_n_day_old(self, days: int, status: str = None):
        threshold_time = int(time.time()) - days * 86400
        if status:
            return [
                msg for msg in self.data
                if msg['timestamp'] <= threshold_time and msg['status'] == status
            ]
        else:
            return [msg for msg in self.data if msg['timestamp'] <= threshold_time]
