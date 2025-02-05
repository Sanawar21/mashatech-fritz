from ..base import IncomingMessage


class KeepAliveMessage(IncomingMessage):
    """Standard incoming keep-alive message, ignore it."""
    type_ = "keepAlive"

    @classmethod
    def from_dict(cls, data: dict):
        return cls()

    def process(self, ctx):
        pass
