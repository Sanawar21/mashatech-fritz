from abc import ABC, abstractmethod


class AbstractBaseMessage(ABC):
    def __init__(self, message_data):
        self.type = message_data.get('type')

    @abstractmethod
    def process(self):
        pass
