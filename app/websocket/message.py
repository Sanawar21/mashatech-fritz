from abc import ABC, abstractmethod
from ..models import Ad, AdParser, Match
from ..utils import MESSAGES


class InvalidAdException(Exception):
    """Exception raised for unsuitable ads."""


# class MessageFactory:
#     # TODO: Implement types
#     @staticmethod
#     def create_message(message_data):
#         if message_data.get('type') == 'message':
#             return Message(message_data)
#         elif message_data.get('type') == 'command':
#             return Command(message_data)
#         else:
#             return UnknownMessage(message_data)


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

    @abstractmethod
    def build(self):
        pass


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

    def build(self, ad: Ad) -> dict:
        """Builds the message to be sent to the extension.
        Raises InvalidAdException if the Ad does not match our criteria."""

        matches = self.__parser.find_matches(ad.title, ad.description)

        if not matches:
            raise InvalidAdException

        offer_price = self.__parser.get_offer_price(matches, ad)

        if offer_price:
            # TODO: Send message to telegram
            return {
                "type": "sendOffer",
                "message": self.__get_message(),
                "link": ad.link,
                "offer_price": offer_price
            }
        else:
            raise InvalidAdException
