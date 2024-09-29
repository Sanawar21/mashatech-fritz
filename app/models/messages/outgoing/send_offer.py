from ..base import OutgoingMessage
from ....ad import Ad, Match
from .....utils import MESSAGES
from .....exceptions import InvalidAdException


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

    def __init__(self, ad: Ad):
        """Builds the message to be sent to the extension.
        Raises InvalidAdException if the Ad does not match our criteria."""

        if not ad.matches or not ad.offer_price:
            raise InvalidAdException

        self.message = self.__get_message(ad.matches)
        self.link = ad.link
        self.offer_price = ad.offer_price

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
                if product in MESSAGES.keys():
                    return MESSAGES[product]

        return MESSAGES["universal"]

    def to_dict(self):
        return {
            "type": self.type_,
            "message": self.message,
            "link": self.link,
            "offer_price": self.offer_price
        }
