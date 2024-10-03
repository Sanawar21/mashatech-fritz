from ..utils import AT_API_KEY, AT_BASE_ID, AT_TABLE_NAME
from ..models import AirtableEntry
from ..cache import AirtableCache

from pyairtable import Table


class AirtableClient(Table):

    # column names

    FORMULA = "{Zustand}='Perfekt'"

    def __init__(self) -> None:
        super().__init__(AT_API_KEY, AT_BASE_ID, AT_TABLE_NAME)
        self.__cache = AirtableCache()
        self.old_perfect_ids = self.__cache.read_old_perfect_ids()

    def read_new_perfects(self):
        results = self.all(formula=self.FORMULA)
        filtered_results = [
            result for result in results if result["id"] not in self.old_perfect_ids]
        self.old_perfect_ids.extend(
            [result["id"] for result in filtered_results])
        self.__cache.update_old_perfect_ids(self.old_perfect_ids)
        return filtered_results

    def create(self, entry: AirtableEntry):
        """
        Create a new entry in the Airtable database.
        """
        print(entry.to_dict())
        return super().create(entry.to_dict())
