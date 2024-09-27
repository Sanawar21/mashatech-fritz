class MessageID:
    """Message ID model that will be saved to the database."""

    def __init__(self, message_id: str, timestamp: int) -> None:
        self.message_id = message_id
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get('message_id'),
            data.get('timestamp')
        )
