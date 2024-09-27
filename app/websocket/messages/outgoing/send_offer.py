from ..base import OutgoingMessage, InvalidAdException
from ....models import Ad, Match, AdParser
from ....utils import MESSAGES


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
