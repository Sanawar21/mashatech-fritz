from ..utils import CATALOG
from .match import Match


class AdParser:

    def __init__(self) -> None:
        self.tokens = None

    def __tokenize(self, text: str):
        numbers = "0123456789 "
        chunks = []
        chunk = text[0]
        chunk_is_numeric = chunk in numbers
        for char in text[1:]:
            if (chunk_is_numeric and char in numbers) or (not chunk_is_numeric and char not in numbers):
                chunk += char
            else:
                chunks.extend([x.strip() for x in chunk.split(" ") if x != ""])
                chunk = char
                chunk_is_numeric = not chunk_is_numeric
        chunks.extend([x.strip() for x in chunk.split(" ") if x != ""])
        self.tokens = chunks
        return chunks

    @staticmethod
    def get_offer_price(matches: list[Match], ad):
        """
        matches is a list of Match objects
        ad is an Ad object
        If price is less than 120% / 125% the price of the match and 
        account is not new return the offer price else return False
        """

        if ad.account_age <= 7 or ad.is_damaged or ad.is_only_pickup or not ad.price:
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
            return False

    def find_matches(self, product_title: str, product_description: str) -> list[Match]:

        products = list(CATALOG.keys())
        matched_products = []
        matches: list[Match] = []

        alphanumerics = "abcdefghijklmnopqrstuvwxyz0123456789 "
        text = " ".join([product_title, product_description])
        text = text.lower()
        special_chars = []

        for char in text:
            if char not in alphanumerics:
                special_chars.append(char)

        for char in special_chars:
            text = text.replace(char, "")

        self.__tokenize(text)

        while True:
            match = self.__find_product_match(products)
            if match == None:
                break
            products.remove(match)
            matched_products.append(match)

        match_amounts = self.__get_match_amounts(matched_products)

        for match in match_amounts.keys():
            matches.append(Match(match, match_amounts[match], CATALOG[match]))

        return matches

    def __get_match_amounts(self, matches: list[str]):
        matches_with_amounts = {}

        xs = []
        for index, x in enumerate(self.tokens):
            if self.tokens[index - 1] and x == "x" and self.tokens[index - 1] in "0123456789":
                xs.append(index - 1)

        if xs == []:
            return {m: 1 for m in matches}
        else:
            for x in xs:
                for token in self.tokens[x:]:
                    if token in matches:
                        try:
                            matches_with_amounts[token] = int(self.tokens[x-1])
                        except ValueError:
                            matches_with_amounts[token] = 1
            for match in matches:
                if match not in matches_with_amounts.keys():
                    matches_with_amounts[match] = 1
            return matches_with_amounts

    def __find_product_match(self, products: list[str]):
        """
        returns the matching product in the catalogue with its price in a tuple.
        returns None if no match found.
        """

        def check_neighbors(tokens, match):
            """
            returns True if the neighbors of the match indicate that the match is in
            fact a real match and not a false positive.
            else return False
            """
            keywords = ["repeater", "router", "box",
                        "fritz", "fritzbox", "powerline",
                        "adapter", "wlanrouter", "netzteil",
                        "wlan", "fritzpowerline", "cable",
                        "dect", "fritzrepeater", "set",
                        "powerlineadapter", "ax", "e"]
            keywords.extend(list(CATALOG.keys()))
            match_index = tokens.index(match)
            tokens.append(None)  # to prevent index out of range

            for keyword in keywords:
                if (tokens[match_index - 1] == keyword or tokens[match_index + 1] == keyword) and ("mbit" not in tokens[match_index + 1]):
                    return True
            return False

        matches = []

        for product in products:
            if product in self.tokens:
                if check_neighbors(self.tokens, product):
                    matches.append(product)
                else:
                    self.tokens.remove(product)

        if len(matches) >= 1:
            match = matches[0]
            index_of_match = self.tokens.index(match)
            if match in ["7590", "7530"]:
                # check ax
                try:
                    if "ax" == self.tokens[index_of_match + 1]:
                        if f"{match} ax" in products:
                            return f"{match} ax"
                        else:
                            return None
                except IndexError:
                    pass
            return match
