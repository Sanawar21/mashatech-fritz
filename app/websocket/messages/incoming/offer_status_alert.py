from ..base import IncomingMessage
from typing import Literal


class OfferStatusAlertMessage(IncomingMessage):
    type_ = "offerStatusAlert"

    def __init__(self, ad_link: str, price: float, chat_link: str, status: Literal["accepted", "rejected", "paid", "pending"]) -> None:
        self.ad_link = ad_link
        self.price = price
        self.chat_link = chat_link
        self.status = status

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get('ad_link'),
            data.get('price'),
            data.get('chat_link'),
            data.get('status')
        )

    def process(self):
        # TODO: Implement
        pass
