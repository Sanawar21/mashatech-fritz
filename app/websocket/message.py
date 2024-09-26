from abc import ABC, abstractmethod
from typing import Literal

from ..models import Ad, AdParser, Match
from ..utils import MESSAGES


class InvalidAdException(Exception):
    """Exception raised for unsuitable ads."""


class MessageFactory:
    @staticmethod
    def create_message(message_data: dict):
        type_ = message_data.get('type')
        messages = [KeepAliveMessage, OfferSentMessage,
                    OfferStatusAlertMessage, AmountPaidAlertMessage]
        for message in messages:
            if message.type_ == type_:
                return message.from_dict(message_data)

# ABSTRACT CLASSES


class AbstractBaseMessage(ABC):
    @property
    @abstractmethod
    def type_(self):
        pass


class IncomingMessage(AbstractBaseMessage):

    @classmethod
    @abstractmethod
    def from_dict(self, data: dict):
        pass

    @abstractmethod
    def process(self):
        pass


class OutgoingMessage(AbstractBaseMessage):

    @abstractmethod
    def to_dict(self):
        pass


class ChatLinkMessage(OutgoingMessage):

    def __init__(self, message_id) -> None:
        self.message_id = message_id
        self.chat_link = "https://www.kleinanzeigen.de/m-nachrichten.html?conversationId=" + message_id

    def to_dict(self):
        return {
            "type": self.type_,
            "chat_link": self.chat_link
        }

# CONCRETE CLASSES (Outgoing Messages)


class SendOfferMessage(OutgoingMessage):
    """
    This message is to be send when KleinanzeiganAPI encounters a new ad that matches our search criteria.

    format: {
        "type": "sendOffer",
        "message": < message that needs to be sent to the ad poster >,
        "link": < link of the ad >,
        "offer_price": < price to be offered >
    }"""

    type_ = 'sendOffer'
    __parser = AdParser()

    def __init__(self, ad: Ad):
        """Builds the message to be sent to the extension.
        Raises InvalidAdException if the Ad does not match our criteria."""

        matches = self.__parser.find_matches(ad.title, ad.description)

        if not matches:
            raise InvalidAdException

        offer_price = self.__parser.get_offer_price(matches, ad)

        if offer_price:
            self.message = self.__get_message(matches)
            self.link = ad.link
            self.offer_price = offer_price
        else:
            raise InvalidAdException

    def __get_message(self, matches: list[Match]) -> str:
        products = [match.product for match in matches]
        if len(products) == 1:
            product = products[0]
            try:
                return MESSAGES[product]
            except KeyError:
                pass
        else:
            for product in products:
                if product in ["4020", "4040", "7490", "7530", "7530 ax", "7590", "7590 ax", "6660", "6590", "6591", "5590"]:
                    return MESSAGES[product]

        return MESSAGES["universal"]

    def to_dict(self):
        return {
            "type": self.type_,
            "message": self.message,
            "link": self.link,
            "offer_price": self.offer_price
        }


class CheckOfferStatusMessage(ChatLinkMessage):
    type_ = "checkStatus"


class ReleasePaymentMessage(ChatLinkMessage):
    type_ = "releasePayment"


class DeleteOfferMessage(ChatLinkMessage):
    type_ = "deleteMsg"


# CONCRETE CLASSES (Incoming Messages)

class KeepAliveMessage(IncomingMessage):
    type_ = "keepAlive"

    def __init__(self) -> None:
        pass

    @classmethod
    def from_dict(cls, data: dict):
        return cls()

    def process(self):
        pass


class OfferSentMessage(IncomingMessage):
    type_ = "offerSentAlert"

    def __init__(self, message_id: str) -> None:
        self.message_id = message_id

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data.get('msg_id'))

    def process(self):
        # TODO: Implement
        pass


class OfferStatusAlertMessage(IncomingMessage):
    type_ = "offerStatusAlert"

    def __init__(self, ad_link: str, price: float, chat_link: str, status: Literal["accepted", "rejected", "paid", "pending"]) -> None:
        self.ad_link = ad_link
        self.price = price
        self.chat_link = chat_link
        self.status = status

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get('ad_link'),
            data.get('price'),
            data.get('chat_link'),
            data.get('status')
        )

    def process(self):
        # TODO: Implement
        pass


class AmountPaidAlertMessage(IncomingMessage):
    type_ = "amountPaidAlert"

    def __init__(self, ad_link: str, chat_link: str) -> None:
        self.ad_link = ad_link
        self.chat_link = chat_link

    def from_dict(cls, data: dict):
        return cls(
            data.get('ad_link'),
            data.get('chat_link')
        )

    def process(self):
        # TODO: Implement
        pass
