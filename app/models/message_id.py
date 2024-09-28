class MessageID:
    """Message ID model that will be saved to the database."""

    def __init__(self, message_id: str, timestamp: int, status: str) -> None:
        self.message_id = message_id
        self.timestamp = timestamp
        self.status = status

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get('message_id'),
            data.get('timestamp'),
            data.get('status')
        )
