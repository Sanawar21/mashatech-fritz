from abc import ABC, abstractmethod


class InvalidAdException(Exception):
    """Exception raised for unsuitable ads."""


# ABSTRACT CLASSES


class AbstractBaseMessage(ABC):
    @property
    @abstractmethod
    def type_(self):
        pass


class IncomingMessage(AbstractBaseMessage):

    def __init__(self):
        self.response = None

    @classmethod
    @abstractmethod
    def from_dict(self, data: dict):
        pass

    @abstractmethod
    def process(self):
        pass


class OutgoingMessage(AbstractBaseMessage):

    @abstractmethod
    def to_dict(self):
        pass


class ChatLinkMessage(OutgoingMessage):

    def __init__(self, message_id) -> None:
        self.message_id = message_id
        self.chat_link = "https://www.kleinanzeigen.de/m-nachrichten.html?conversationId=" + message_id

    def to_dict(self):
        return {
            "type": self.type_,
            "chat_link": self.chat_link
        }
