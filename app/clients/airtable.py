from ..utils import AT_API_KEY, AT_BASE_ID, AT_TABLE_NAME
from ..models import AirtableEntry
from ..cache import AirtableCache

from pyairtable import Table

import logging


class AirtableClient(Table):

    # column names

    FORMULA = "{Zustand}='Perfekt'"

    def __init__(self) -> None:
        super().__init__(AT_API_KEY, AT_BASE_ID, AT_TABLE_NAME)
        self.__cache = AirtableCache()
        self.old_perfect_ids = self.__cache.read_old_perfect_ids()

    def read_new_perfects(self) -> list[AirtableEntry]:
        results = self.all(formula=self.FORMULA)
        filtered_results = [
            result for result in results if result["id"] not in self.old_perfect_ids]
        self.old_perfect_ids.extend(
            [result["id"] for result in filtered_results])
        self.__cache.update_old_perfect_ids(self.old_perfect_ids)
        # create airtable entry objects
        filtered_results = [AirtableEntry.from_dict(
            result["fields"]) for result in filtered_results]
        return filtered_results

    def update(self, selector: str, field_name: str, data: str):
        """
        Find the record by 'Ad UID' and prepend `data` to the specified field (e.g., 'Products').
        """
        formula = f"{{Ad UID}} = '{selector}'"
        records = self.all(formula=formula)

        if not records:
            logging.warning(f"No record found for Ad UID: {selector}")
            return

        record = records[0]  # assuming 'Ad UID' is unique
        record_id = record["id"]
        current_value = record["fields"].get(field_name, "")

        # Prepend the new data to the existing field value
        updated_value = f"{data}\n{current_value}"

        super().update(record_id, {field_name: updated_value})
        logging.info(
            f"Updated record {record_id}: set {field_name} to '{updated_value}'")

    def create(self, entry: AirtableEntry):
        """
        Create a new entry in the Airtable database.
        """
        logging.info(f"Creating new entry in Airtable for {entry.ad_uid}")
        return super().create(entry.to_dict())
