from ..base import ChatLinkMessage


class ReleasePaymentMessage(ChatLinkMessage):
    """Release the payment for an offer."""
    type_ = "releasePayment"
