from ..base import IncomingMessage
from ...cache import MessageIDCache

from urllib.parse import urlparse, parse_qs


class AmountPaidAlertMessage(IncomingMessage):
    """The extension will send this message when it releases the payment."""

    type_ = "amountPaidAlert"
    __cache = MessageIDCache()

    def __init__(self, ad_link: str, chat_link: str) -> None:
        self.ad_link = ad_link
        self.chat_link = chat_link
        super().__init__()

    def __id_from_link(self) -> str:
        parsed_url = urlparse(self.chat_link)
        query_params = parse_qs(parsed_url.query)
        return query_params.get('conversationId', [None])[0]

    def from_dict(cls, data: dict):
        return cls(
            data.get('ad_link'),
            data.get('chat_link')
        )

    def process(self):
        # remove the message_id from the cache
        self.__cache.delete(self.__id_from_link(self.chat_link))
