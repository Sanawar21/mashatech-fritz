from ..base import ChatLinkMessage


class DeleteOfferMessage(ChatLinkMessage):
    """Delete an offer message."""
    type_ = "deleteMsg"
