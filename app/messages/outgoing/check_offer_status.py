from ..base import ChatLinkMessage


class CheckOfferStatusMessage(ChatLinkMessage):
    """Check the status of an offer."""
    type_ = "checkStatus"
