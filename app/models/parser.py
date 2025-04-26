from .match import Match
from .catalog import Catalog
from ..clients import GeminiClient
from ..exceptions import GeminiAPIError

import logging
import deep_translator


class AdParser:

    def __init__(self) -> None:
        self.tokens = None
        self.__catalog = Catalog()
        self.__gemeni_client = GeminiClient()

    @staticmethod
    def get_offer_price(matches: list[Match], ad):
        """
        matches is a list of Match objects
        ad is an Ad object
        If price is less than 120% / 125% the price of the match and 
        account is not new return the offer price else return False
        """

        # or not ad.is_buy_now_available: (This check was removed)

        if ad.account_age <= 7:
            logging.info(f"Ad rejected. Account age too low: {ad.account_age}")
            return False
        elif ad.is_damaged:
            logging.info(f"Ad rejected. Damaged: {ad.is_damaged}")
            return False
        elif ad.is_only_pickup:
            logging.info(f"Ad rejected. Pickup only: {ad.is_only_pickup}")
            return False
        elif not ad.price:
            logging.info(f"Ad rejected. No price: {ad.price}")
            return False

        estimated_price = sum(
            [match.price * match.quantity for match in matches]
        )
        tolerance = 0.25 if ad.price >= 80 else 0.2

        if estimated_price + estimated_price * tolerance >= ad.price:
            if ad.price < estimated_price:
                return ad.price
            else:
                return estimated_price
        else:
            logging.info(
                f"Ad rejected. Price too high: {ad.price} (Reasonable price: {estimated_price})")
            return False

    def find_matches(self, product_title: str, product_description: str) -> list[Match]:
        prices = self.__catalog.prices
        products = list(prices.keys())
        matches: list[Match] = []

        # Translate the product title and description from german to English
        translator = deep_translator.GoogleTranslator(
            source="de", target="en")
        title = translator.translate(product_title)
        description = translator.translate(product_description)

        try:
            results = self.__gemeni_client.extract_products(
                title, description, products)
        except GeminiAPIError:
            return None

        for match in results:
            matches.append(
                Match(match["name"], match["quantity"], prices[match["name"]]))

        return matches
