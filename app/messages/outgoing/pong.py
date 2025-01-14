from ..base import OutgoingMessage


class PongMessage(OutgoingMessage):
    """Standard outgoing pong message."""
    type_ = "pong"

    def to_dict(self):
        return {
            "type": self.type_
        }
