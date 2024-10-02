class MessageID:
    """Message ID model that will be saved to the database."""

    def __init__(self, message_id: str, timestamp: int, status: str, ad_uid: str) -> None:
        self.message_id = message_id
        self.timestamp = timestamp
        self.status = status
        self.ad_uid = ad_uid

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "ad_uid": self.ad_uid,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get('message_id'),
            data.get('timestamp'),
            data.get('status'),
            data.get('ad_uid'),
        )
