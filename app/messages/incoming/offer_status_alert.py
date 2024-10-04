from ..base import IncomingMessage
from ...cache import MessageIDCache
from ...clients import TelegramClient, AirtableClient, KleinanzeigenClient
from ...exceptions import InvalidOfferStatusException
from ...models import AirtableEntry
from ..outgoing import DeleteOfferMessage

from typing import Literal
from urllib.parse import urlparse, parse_qs

import logging


class OfferStatusAlertMessage(IncomingMessage):
    """The extension will send this message when we request the status of an offer."""

    type_ = "offerStatusAlert"
    __cache = MessageIDCache()
    __telegram = TelegramClient()
    __airtable = AirtableClient()
    __kleinanzeigen = KleinanzeigenClient()

    def __init__(self, ad_link: str, price: float, chat_link: str, status: Literal["accepted", "rejected", "paid", "pending"]) -> None:
        self.ad_link = ad_link
        self.price = price
        self.chat_link = chat_link
        self.status = status
        self.message_id = self.__id_from_link()
        super().__init__()

    def __id_from_link(self) -> str:
        parsed_url = urlparse(self.chat_link)
        query_params = parse_qs(parsed_url.query)
        return query_params.get('conversationId', [None])[0]

    def __ad_id_from_link(self) -> str:
        return self.ad_link.split("/")[-1].split("-")[0]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get('ad_link'),
            data.get('price'),
            data.get('chat_link'),
            data.get('status')
        )

    def process(self):
        self.__cache.refresh()
        if self.status == "accepted":
            ad_uid = self.__ad_id_from_link()
            logging.info(f"Offer for {self.ad_link} has been accepted.")
            ad = self.__kleinanzeigen.get_ad(ad_uid)
            self.__cache.update_status(self.message_id, "accepted")
            self.__telegram.send_offer_accepted_alert(
                ad, self.price, self.chat_link)

        elif self.status == "rejected":
            logging.info(f"Offer for {self.ad_link} has been rejected.")
            self.__cache.delete(self.message_id)
            self.response = DeleteOfferMessage(self.message_id)

        elif self.status == "paid":
            logging.info(
                f"Payment for {self.ad_link} has been made, waiting for perfection confirmation.")
            ad_uid = self.__ad_id_from_link()
            self.__cache.update_status(self.message_id, "paid")
            ad = self.__kleinanzeigen.get_ad(ad_uid)
            entry = AirtableEntry.from_ad(ad, self.chat_link)
            self.__airtable.create(entry)

        elif self.status == "pending":
            pass

        else:
            raise InvalidOfferStatusException(
                f"{self.status} is not a valid offer status.")
