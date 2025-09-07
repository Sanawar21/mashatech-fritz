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
        self.__catalog = Catalog()

        if not ad.matches or not ad.offer_price or \
                not all([self.__catalog.is_enabled(match.product) for match in ad.matches]):
            raise InvalidAdException

        self.link = ad.link
        self.offer_price = ad.offer_price
        self.message = self.__get_message(ad.matches)

    def __get_message(self, matches: list[Match]) -> str:
        products = [match.product for match in matches]
        messages = self.__catalog.messages
        message = messages["universal"]
        if len(products) == 1:
            product = products[0]
            try:
                message = messages[product]
            except KeyError:
                pass
        else:
            for product in products:
                if product in messages.keys():
                    message = messages[product]

        message.replace('" "', self.offer_price)
        return message

    def to_dict(self):
        return {
            "type": self.type_,
            "message": self.message,
            "link": self.link,
            "offer_price": self.offer_price
        }
