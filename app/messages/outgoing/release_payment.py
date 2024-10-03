from ..base import ChatLinkMessage
from ...cache import MessageIDCache


class ReleasePaymentMessage(ChatLinkMessage):
    """Release the payment for an offer."""
    type_ = "releasePayment"
    __cache = MessageIDCache()

    def __init__(self, message_id) -> None:
        super().__init__(message_id)
        self.__cache.refresh()
        self.__cache.delete(message_id)
