from .incoming import *
from .base import IncomingMessage
from ..exceptions import InvalidIncomingMessageException


class MessageFactory:
    @staticmethod
    def create_message(message_data: dict) -> IncomingMessage:
        try:
            type_ = message_data.get('type')
            messages: list[IncomingMessage] = [KeepAliveMessage, OfferSentMessage,
                                               OfferStatusAlertMessage, AmountPaidAlertMessage]
            for message in messages:
                if message.type_ == type_:
                    return message.from_dict(message_data)
        except AttributeError:
            pass
        raise InvalidIncomingMessageException(f"Invalid message type: {type_}")
