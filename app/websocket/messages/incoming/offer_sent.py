from ..base import IncomingMessage
from ....models import MessageIDCache


class OfferSentMessage(IncomingMessage):
    type_ = "offerSentAlert"
    __cache = MessageIDCache()

    def __init__(self, message_id: str) -> None:
        """When the extension sends and offer to the ad poster, 
        the extension will send this message to the websocket."""

        self.message_id = message_id
        super().__init__()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data.get('msg_id'))

    def process(self):
        self.__cache.create_message_id(self.message_id)
