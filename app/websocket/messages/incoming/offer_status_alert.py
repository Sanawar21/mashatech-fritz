from ..base import IncomingMessage
from ....models import MessageIDCache, TelegramClient
from ....exceptions import InvalidOfferStatusException

from typing import Literal
from urllib.parse import urlparse, parse_qs


class OfferStatusAlertMessage(IncomingMessage):
    type_ = "offerStatusAlert"
    __cache = MessageIDCache()
    __telegram = TelegramClient()

    def __init__(self, ad_link: str, price: float, chat_link: str, status: Literal["accepted", "rejected", "paid", "pending"]) -> None:
        self.ad_link = ad_link
        self.price = price
        self.chat_link = chat_link
        self.status = status
        self.message_id = self.__id_from_link()
        super().__init__()

    def __id_from_link(self) -> str:
        parsed_url = urlparse(self.ad_link)
        query_params = parse_qs(parsed_url.query)
        return query_params.get('conversationId', [None])[0]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get('ad_link'),
            data.get('price'),
            data.get('chat_link'),
            data.get('status')
        )

    def process(self):
        if self.status == "accepted":
            self.__cache.update_status(self.message_id, "accepted")
            self.__telegram.send_offer_accepted_alert(
                self.ad_link, self.price, self.chat_link)
        elif self.status == "rejected":
            self.__cache.delete(self.message_id)
        elif self.status == "paid":
            # TODO: Implement
            print(f"Offer for {self.ad_link} has been paid.")
        elif self.status == "pending":
            pass
        else:
            raise InvalidOfferStatusException(
                f"{self.status} is not a valid offer status.")
