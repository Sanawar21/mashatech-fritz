import json
import time

from .message_id import MessageID


class DataHandler:
    def __init__(self) -> None:
        self.path = "data/data.json"
        self.data = self.load_data()

    def load_data(self):
        try:
            with open(self.path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_data(self):
        with open(self.path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def add_message_id(self, message_id: str):
        self.data.append(MessageID(message_id, int(time.time())).to_dict())
        self.save_data()

    def get_message_ids(self):
        return self.data

    def clear_data(self):
        self.data = []
        self.save_data()

    def get_n_day_old_message_ids(self, days: int):
        current_time = int(time.time())
        return [msg for msg in self.data if current_time - msg['timestamp'] >= days * 86400]
