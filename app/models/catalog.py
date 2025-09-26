import logging
from ..clients.googlesheets import GoogleSheetsTable

from ..utils import AT_CATALOG_NAME, AT_BASE_ID, AT_API_KEY, GOOGLE_SHEETS_URL


class Catalog:
    """
    Catalog provides access to the products catalog in the Airtable database.
    Usage:
    catalog = Catalog()
    print(catalog.messages) # {'510': 'Message 1', '520': 'Message 2', ...}
    print(catalog.prices) # {'510': 5, '520': 10, ...}
    print(catalog.is_enabled("510")) # True
    catalog.refresh() # Refresh the catalog from the Airtable database.

    Catalog().refresh changes the messages and prices across all instances of the Catalog class.
    """
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
            self.message = self.__parse_message(message)
            self.is_enabled = is_enabled

        @classmethod
        def from_dict(cls, data: dict):
            return cls(
                data.get(cls.NAME),
                data.get(cls.PRICE),
                data.get(cls.MESSAGE),
                data.get(cls.IS_ENABLED)
            )

        def __parse_message(self, message: str) -> str:
            """
            Ensures the message text is in correct UTF-8 format.
            If the string looks double-encoded (e.g., 'GerÃ¤t'),
            it is re-decoded properly. Otherwise, it is returned unchanged.
            """
            if not isinstance(message, str):
                return message

            try:
                # Fix double-encoding: str -> bytes (latin1) -> str (utf-8)
                fixed = message.encode("latin1").decode("utf-8")
                # Only replace if the conversion actually fixed something
                return fixed if fixed != message else message
            except UnicodeDecodeError:
                return message

    __entries = []
    __is_initialized = False

    def __init__(self):
        self.__table = GoogleSheetsTable(GOOGLE_SHEETS_URL)
        if Catalog.__is_initialized is False:
            self.refresh()
            Catalog.__is_initialized = True

    @property
    def messages(self):
        return {
            product.name: product.message
            for product in self.__entries
            if product.message is not None
        }

    @property
    def prices(self):
        return {
            product.name: int(product.price)
            for product in self.__entries
            if product.price is not None and product.name is not None and product.name != "universal"
        }

    def is_enabled(self, product_name: str):
        for product in self.__entries:
            if product.name == product_name:
                return product.is_enabled
        return False

    def refresh(self):
        logging.info("Refreshing catalog...")
        Catalog.__entries = [
            self.CatalogEntry.from_dict(result["fields"])
            for result in self.__table.all()
        ]
