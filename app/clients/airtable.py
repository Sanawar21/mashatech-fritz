from ..utils import AT_API_KEY, AT_BASE_ID, AT_PRODUCTS_BOUGHT_TABLE, AT_PRODUCTS_TABLE
from ..models import ATBoughtEntry, ATProductEntry
from ..cache import AirtableCache

from pyairtable import Table

import logging


class AirtableClient:

    PERFECT_CONDITION_FILTER = "{Zustand}='Perfekt'"

    def __init__(self) -> None:
        # create airtable table objects
        self.products_bought_table = Table(
            AT_API_KEY,
            AT_BASE_ID,
            AT_PRODUCTS_BOUGHT_TABLE
        )
        self.products_table = Table(
            AT_API_KEY,
            AT_BASE_ID,
            AT_PRODUCTS_TABLE
        )

        self.__messages = None
        self.__catalog = None
        self.__cache = AirtableCache()

        self.update_catalog_and_messages()
        self.old_perfect_ids = self.__cache.read_old_perfect_ids()

    def __create_messages_dict(self, products: list[ATProductEntry]) -> dict:
        return {product.product_name: product.message for product in products}

    def __create_catalog_dict(self, products: list[ATProductEntry]) -> dict:
        return {product.product_name: int(product.price) for product in products}

    @property
    def messages(self) -> dict:
        return self.__messages

    @property
    def catalog(self) -> dict:
        return self.__catalog

    def read_new_perfects(self) -> list[ATBoughtEntry]:
        results = self.products_bought_table.all(
            formula=self.PERFECT_CONDITION_FILTER)
        filtered_results = [
            result for result in results if result["id"] not in self.old_perfect_ids]
        self.old_perfect_ids.extend(
            [result["id"] for result in filtered_results])
        self.__cache.update_old_perfect_ids(self.old_perfect_ids)
        # create airtable entry objects
        filtered_results = [ATBoughtEntry.from_dict(
            result["fields"]) for result in filtered_results]
        return filtered_results

    def update_catalog_and_messages(self):
        results = [
            ATProductEntry.from_dict(result["fields"])
            for result in self.products_table.all()
        ]
        self.__messages = self.__create_messages_dict(results)
        self.__catalog = self.__create_catalog_dict(results)
        del self.__catalog["Universal"]

    def create(self, entry: ATBoughtEntry):
        """
        Create a new entry in the Airtable database.
        """
        logging.info(f"Creating new entry in Airtable for {entry.ad_uid}")
        return self.products_bought_table.create(entry.to_dict())
