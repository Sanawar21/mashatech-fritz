from .incoming import *
from .base import IncomingMessage


class MessageFactory:
    @staticmethod
    def create_message(message_data: dict) -> IncomingMessage:
        type_ = message_data.get('type')
        messages: list[IncomingMessage] = [KeepAliveMessage, OfferSentMessage,
                                           OfferStatusAlertMessage, AmountPaidAlertMessage]
        for message in messages:
            if message.type_ == type_:
                return message.from_dict(message_data)
