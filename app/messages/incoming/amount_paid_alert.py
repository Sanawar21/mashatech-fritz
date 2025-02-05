from ..base import IncomingMessage
from ...cache import MessageIDCache
from ...clients import TelegramClient, KleinanzeigenClient
from ...utils import get_chat_id_from_link, get_ad_id_from_link


import logging


class AmountPaidAlertMessage(IncomingMessage):
    """The extension will send this message when it releases the payment."""

    type_ = "amountPaidAlert"

    def __init__(self, ad_link: str, chat_link: str) -> None:
        self.ad_link = ad_link
        self.chat_link = chat_link
        super().__init__()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get('link'),
            data.get('chat_link')
        )

    def process(self, ctx):
        # remove the message_id from the cache
        ctx.msg_cache.refresh()
        message_id = get_chat_id_from_link(self.chat_link)
        logging.info(f"Payment for {self.ad_link} has been released.")
        ad = ctx.ka_client.get_ad(get_ad_id_from_link(self.ad_link))
        ctx.ka_client.send_amount_paid_alert(ad, self.chat_link)
        ctx.msg_cache.delete(message_id)
