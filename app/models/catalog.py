from pyairtable import Table
from ..utils import AT_CATALOG_NAME, AT_BASE_ID, AT_API_KEY


class Catalog:
    class CatalogEntry:
        """
        CatalogEntry represents a single entry in the Airtable products list
        which contains the prices, custom messages affiliated with each product and 
        whether the product is to be ignored or not.

            Attributes:
            name (str): The name of the product.
            price (int): The price of the product.
            message (str): The custom message affiliated with the product.
            is_enabled (bool): Whether the product is to be ignored or not.
        """
        # Airtable column names
        NAME = "Name"
        PRICE = "Price"
        MESSAGE = "Message"
        IS_ENABLED = "isEnabled"

        def __init__(self, name, price, message, is_enabled):
            self.name = name
            self.price = price
            self.message = message
            self.is_enabled = is_enabled

        @classmethod
        def from_dict(cls, data: dict):
            return cls(
                data.get(cls.NAME),
                data.get(cls.PRICE),
                data.get(cls.MESSAGE),
                data.get(cls.IS_ENABLED)
            )

    def __init__(self):
        self.__table = Table(AT_API_KEY, AT_BASE_ID, AT_CATALOG_NAME)
        self.__entries: list[Catalog.CatalogEntry] = []
        self.refresh()

    @property
    def messages(self):
        return {
            product.name: product.message
            for product in self.__entries
            if product.message is not None
        }

    @property
    def catalog(self):
        return {
            product.name: int(product.price)
            for product in self.__entries
            if product.name != "universal"
        }

    def is_enabled(self, product_name: str):
        for product in self.__entries:
            if product.name == product_name:
                return product.is_enabled
        return False

    def refresh(self):
        self.__entries =  [
            self.CatalogEntry.from_dict(result["fields"])
            for result in self.__table.all()
        ]
