from ..base import IncomingMessage
from ...cache import MessageIDCache

import logging


class OfferSentMessage(IncomingMessage):
    """When the extension sends an offer to the ad poster, it will send this message to the websocket."""

    type_ = "offerSentAlert"

    def __init__(self, message_id: str, ad_uid: str) -> None:
        # ad uid is offer_id
        # message_id is conversation id of the chat
        self.message_id = message_id
        self.ad_uid = ad_uid
        super().__init__()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data.get('msg_id'), data.get('offer_id'))

    def process(self, ctx):
        ctx.msg_cache.refresh()
        logging.info(f"Sending of offer for {self.ad_uid} has been confirmed")
        ctx.msg_cache.create(self.message_id, self.ad_uid)
