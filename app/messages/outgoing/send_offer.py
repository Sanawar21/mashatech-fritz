from ..base import OutgoingMessage
from ...clients import AirtableClient
from ...models import Ad, Match, ATProductEntry
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

    __at_client = AirtableClient()
    __messages_list = None

    def __init__(self, ad: Ad):

        if not ad.matches or not ad.offer_price:
            raise InvalidAdException

        self.message = self.__get_message(ad.matches)
        self.link = ad.link
        self.offer_price = ad.offer_price

    @classmethod
    def update_messages_list(cls):
        results = cls.__at_client.read_products_table()
        cls.__messages_list = {
            product.product_name: product.message for product in results
        }

    def __get_message(self, matches: list[Match]) -> str:
        products = [match.product for match in matches]
        if len(products) == 1:
            product = products[0]
            try:
                return self.__messages_list[product]
            except KeyError:
                pass
        else:
            for product in products:
                if product in self.__messages_list.keys():
                    return self.__messages_list[product]

        return self.__messages_list["universal"]

    def to_dict(self):
        return {
            "type": self.type_,
            "message": self.message,
            "link": self.link,
            "offer_price": self.offer_price
        }
