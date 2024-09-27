from ..base import IncomingMessage


class KeepAliveMessage(IncomingMessage):
    type_ = "keepAlive"

    @classmethod
    def from_dict(cls, data: dict):
        return cls()

    def process(self):
        pass
