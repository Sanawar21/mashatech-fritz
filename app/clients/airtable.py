from ..utils import AT_API_KEY, AT_BASE_ID, AT_TABLE_NAME
from ..models import Match, Ad, AirtableEntry
from pyairtable import Table


class AirtableClient(Table):

    # column names

    FORMULA = "{Zustand}='Perfekt'"

    def __init__(self, old_perfects: list[AirtableEntry] = []) -> None:
        super().__init__(AT_API_KEY, AT_BASE_ID, AT_TABLE_NAME)
        self.old_perfects = old_perfects

    def read_new_perfects(self):
        results = self.all(formula=self.FORMULA)
        filtered_results = [
            result for result in results if result["id"] not in self.old_perfects]
        self.old_perfects.extend(
            [result["id"] for result in filtered_results])
        return filtered_results

    def create(self, entry: AirtableEntry):
        """
        Create a new entry in the Airtable database.
        """
        return super().create(entry.to_dict())
