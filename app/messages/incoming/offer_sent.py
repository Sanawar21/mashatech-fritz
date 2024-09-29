from ..base import IncomingMessage
from ....cache_handlers import MessageIDCache


class OfferSentMessage(IncomingMessage):
    type_ = "offerSentAlert"
    __cache = MessageIDCache()

    def __init__(self, message_id: str, ad_uid: int) -> None:
        """When the extension sends and offer to the ad poster, 
        the extension will send this message to the websocket."""

        self.message_id = message_id
        self.ad_uid = int(ad_uid)
        super().__init__()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data.get('msg_id'), data.get('ad_uid'))

    def process(self):
        self.__cache.create(self.message_id, self.ad_uid)
