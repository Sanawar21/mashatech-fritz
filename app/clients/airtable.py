from ..utils import AT_API_KEY, AT_BASE_ID, AT_PRODUCTS_BOUGHT_TABLE, AT_PRODUCTS_TABLE
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

        self.__cache = AirtableCache()
        self.old_perfect_ids = self.__cache.read_old_perfect_ids()

    def read_new_perfects(self):
        from ..models.airtable_entry import ATBoughtEntry  # prevent circular import

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

    def read_products_table(self):
        from ..models.airtable_entry import ATProductEntry  # prevent circular import
        return [
            ATProductEntry.from_dict(result["fields"])
            for result in self.products_table.all()
        ]

    def create(self, entry):
        """
        Create a new entry in the Airtable database.
        """
        logging.info(f"Creating new entry in Airtable for {entry.ad_uid}")
        return self.products_bought_table.create(entry.to_dict())
