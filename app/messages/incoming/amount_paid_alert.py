from ..base import IncomingMessage
from ...cache import MessageIDCache
from ...utils import get_chat_id_from_link


import logging


class AmountPaidAlertMessage(IncomingMessage):
    """The extension will send this message when it releases the payment."""

    type_ = "amountPaidAlert"
    __cache = MessageIDCache()

    def __init__(self, ad_link: str, chat_link: str) -> None:
        self.ad_link = ad_link
        self.chat_link = chat_link
        super().__init__()

    def from_dict(cls, data: dict):
        return cls(
            data.get('ad_link'),
            data.get('chat_link')
        )

    def process(self):
        # remove the message_id from the cache
        self.__cache.refresh()
        message_id = get_chat_id_from_link(self.chat_link)
        logging.info(f"Payment for {self.ad_link} has been released.")
        self.__cache.delete(message_id)
