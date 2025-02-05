from ..base import IncomingMessage
from ...exceptions import InvalidOfferStatusException
from ...models import AirtableEntry
from ..outgoing import DeleteOfferMessage, CheckOfferStatusMessage
from ...utils import get_chat_id_from_link, get_ad_id_from_link

from typing import Literal

import logging


class OfferStatusAlertMessage(IncomingMessage):
    """The extension will send this message when we request the status of an offer."""

    type_ = "offerStatusAlert"

    def __init__(self, ad_link: str, price: float, chat_link: str, status: Literal["accepted", "rejected", "paid", "pending"]) -> None:
        self.ad_link = ad_link
        self.price = price
        self.chat_link = chat_link
        self.status = status
        self.message_id = get_chat_id_from_link(self.chat_link)
        super().__init__()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get('ad_link'),
            data.get('price'),
            data.get('chat_link'),
            data.get('status')
        )

    def process(self, ctx):
        ctx.msg_cache.refresh()
        if self.status == "accepted":
            ad_uid = get_ad_id_from_link(self.ad_link)
            logging.info(f"Offer for {self.ad_link} has been accepted.")
            ad = ctx.ka_client.get_ad(ad_uid)
            ctx.msg_cache.update_status(self.message_id, "accepted")
            ctx.tg_client.send_offer_accepted_alert(
                ad, self.price, self.chat_link)

        elif self.status == "rejected":
            logging.info(f"Offer for {self.ad_link} has been rejected.")
            ctx.msg_cache.delete(self.message_id)
            self.response = DeleteOfferMessage(self.message_id)

        elif self.status == "paid":
            logging.info(
                f"Payment for {self.ad_link} has been made, waiting for perfection confirmation.")
            ad_uid = get_ad_id_from_link(self.ad_link)
            ctx.msg_cache.update_status(self.message_id, "paid")
            ad = ctx.ka_client.get_ad(ad_uid)
            entry = AirtableEntry.from_ad(ad, self.chat_link)
            ctx.at_client.create(entry)

        elif self.status == "pending":
            pass

        else:
            raise InvalidOfferStatusException(
                f"{self.status} is not a valid offer status.")

        # send next message and restart the counter
        ctx.status_check_sub_counter.reset()

        if not ctx.check_status_queue.empty():
            id_ = ctx.check_status_queue.get()
            logging.info(
                f"Sending status check message for {id_.message_id}")
            message = CheckOfferStatusMessage(id_.message_id)
            ctx.server.send_message(message)
            ctx.status_check_sub_counter.start()
