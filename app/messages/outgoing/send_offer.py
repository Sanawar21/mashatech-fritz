from ..base import OutgoingMessage
from ...models import Ad, Match, Catalog
from ...exceptions import InvalidAdException


class SendOfferMessage(OutgoingMessage):
    """
    This message is to be send when KleinanzeiganAPI encounters a new ad that matches our search criteria.
    format: {
        "type": "sendOffer",
        "message": < message that needs to be sent to the ad poster >,
        "link": < link of the ad >,
        "offer_price": < price to be offered >
    }
    Raises InvalidAdException if the Ad does not match our criteria."""

    type_ = 'sendOffer'

    def __init__(self, ad: Ad):

        if not ad.matches or not ad.offer_price:
            raise InvalidAdException

        self.message = self.__get_message(ad.matches)
        self.link = ad.link
        self.offer_price = ad.offer_price
        self.__catalog = Catalog()

    def __get_message(self, matches: list[Match]) -> str:
        products = [match.product for match in matches]
        messages = self.__catalog.messages
        if len(products) == 1:
            product = products[0]
            try:
                return messages[product]
            except KeyError:
                pass
        else:
            for product in products:
                if product in messages.keys():
                    return messages[product]

        return messages["universal"]

    def to_dict(self):
        return {
            "type": self.type_,
            "message": self.message,
            "link": self.link,
            "offer_price": self.offer_price
        }
