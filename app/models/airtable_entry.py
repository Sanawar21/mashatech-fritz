from .match import Match


class ATProductEntry:
    """
    ATProductEntry represents a single entry in the Airtable products list
    which contains the prices, custom messages affiliated with each product and 
    whether the product is to be ignored or not.

        Attributes:
        product_name (str): The name of the product.
        price (int): The price of the product.
        message (str): The custom message affiliated with the product.
        is_enabled (bool): Whether the product is to be ignored or not.
    """
    # Airtable column names
    PRODUCT_NAME = "Name"
    PRICE = "Price"
    MESSAGE = "Message"
    IS_ENABLED = "isEnabled"

    def __init__(self, product_name, price, message, is_enabled):
        self.product_name = product_name
        self.price = price
        self.message = message
        self.is_enabled = is_enabled

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get(cls.PRODUCT_NAME),
            data.get(cls.PRICE),
            data.get(cls.MESSAGE),
            data.get(cls.IS_ENABLED)
        )


class ATBoughtEntry:
    """
    ATBoughtEntry represents a single entry in the Airtable products bought table.

        Attributes:        
        ad_uid (str): The unique identifier of the ad.
        date (str): The date the ad was posted.
        matches (list[Match]): The list of products matched in the ad.
        cost (str): The price of the ad.
        poster_name (str): The name of the poster.
        postal_code (str): The postal code of the poster.
        chat_link (str): The link to the chat with the poster.
    """
    # Airtable column names
    AD_UID = "Ad UID"
    LINK = "Link"
    PRICE = "Price"
    DATE = "Date"
    NAME = "Name"
    PRODUCTS = "Products"
    ZUSTAND = "Zustand"
    POSTAL_CODE = "Postal Code"

    def __init__(self, ad_uid, date, matches, cost, poster_name, postal_code, chat_link):
        self.ad_uid = ad_uid
        self.date = date
        self.matches = matches
        self.cost = cost
        self.poster_name = poster_name
        self.postal_code = postal_code
        self.chat_link = chat_link

    @classmethod
    def from_ad(cls, ad, chat_link: str):
        return cls(
            ad.uid,
            ad.date,
            ad.matches,
            ad.offer_price,
            ad.poster_name,
            ad.zip_code,
            chat_link
        )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get(cls.AD_UID),
            data.get(cls.DATE),
            [Match.from_dict(match)
             for match in eval(data.get(cls.PRODUCTS))],
            data.get(cls.PRICE),
            data.get(cls.NAME),
            data.get(cls.POSTAL_CODE),
            data.get(cls.LINK)
        )

    def to_dict(self):
        return {
            self.AD_UID: self.ad_uid,
            self.DATE: self.date,
            self.PRODUCTS: str([match.to_dict() for match in self.matches]),
            self.PRICE: self.cost,
            self.NAME: self.poster_name,
            self.POSTAL_CODE: self.postal_code,
            self.LINK: self.chat_link
        }
