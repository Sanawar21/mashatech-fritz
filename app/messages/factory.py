from .incoming import *
from .base import IncomingMessage
from ..exceptions import InvalidIncomingMessageException

import json
import logging


class MessageFactory:
    @staticmethod
    def create_message(message_data: str) -> IncomingMessage:
        logging.info(f"Incoming message: {message_data}")
        try:
            message_data = json.loads(message_data)
            type_ = message_data.get('type')
            messages: list[IncomingMessage] = [KeepAliveMessage, OfferSentMessage,
                                               OfferStatusAlertMessage, AmountPaidAlertMessage]
            for message in messages:
                if message.type_ == type_:
                    return message.from_dict(message_data)
        except (AttributeError, json.decoder.JSONDecodeError):
            raise InvalidIncomingMessageException("Message type not found")
        raise InvalidIncomingMessageException(f"Invalid message type: {type_}")
