from .base import BaseCache


class AirtableCache(BaseCache):

    def __init__(self, path="data/airtable_products.json") -> None:
        super().__init__(path)

    def update_old_perfect_ids(self, old_perfect_ids: list[str]):
        self.data = self.data + old_perfect_ids
        self.save()

    def read_old_perfect_ids(self):
        return self.data
