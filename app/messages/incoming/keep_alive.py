from ..base import IncomingMessage
from ..outgoing.pong import PongMessage


class KeepAliveMessage(IncomingMessage):
    """Standard incoming keep-alive message, if response is prompted, send pong, else ignore it."""
    type_ = "keepAlive"

    def __init__(self) -> None:
        super().__init__()
        self.send_reply = False

    @classmethod
    def from_dict(cls, data: dict):
        if data.get('sendReply', False):
            return cls()
        else:
            obj = cls()
            obj.send_reply = False

    def process(self):
        if self.send_reply:
            self.response = PongMessage()
        else:
            pass
