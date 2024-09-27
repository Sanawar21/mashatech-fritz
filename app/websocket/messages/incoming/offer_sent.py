from ..base import IncomingMessage


class OfferSentMessage(IncomingMessage):
    type_ = "offerSentAlert"

    def __init__(self, message_id: str) -> None:
        self.message_id = message_id

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data.get('msg_id'))

    def process(self):
        # TODO: Implement
        pass
