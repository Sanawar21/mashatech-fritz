from ..base import OutgoingMessage
from ...models import Ad, Match, CatalogState
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
    __state = CatalogState()

    def __init__(self, ad: Ad):

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
                return self.__state.messages_list[product]
            except KeyError:
                pass
        else:
            for product in products:
                if product in self.__state.messages_list.keys():
                    return self.__state.messages_list[product]

        return self.__state.messages_list["Universal"]

    def to_dict(self):
        return {
            "type": self.type_,
            "message": self.message,
            "link": self.link,
            "offer_price": self.offer_price
        }
