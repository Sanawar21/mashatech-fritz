from ..base import IncomingMessage


class AmountPaidAlertMessage(IncomingMessage):
    type_ = "amountPaidAlert"

    def __init__(self, ad_link: str, chat_link: str) -> None:
        self.ad_link = ad_link
        self.chat_link = chat_link

    def from_dict(cls, data: dict):
        return cls(
            data.get('ad_link'),
            data.get('chat_link')
        )

    def process(self):
        # TODO: Implement
        pass
