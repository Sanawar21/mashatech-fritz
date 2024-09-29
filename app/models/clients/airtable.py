from ...utils import AT_API_KEY, AT_BASE_ID, AT_TABLE_NAME
from pyairtable import Table


class AirtableResult:
    # TODO: Implement this class
    def __init__(self, ):
        self.__dict__ = self


class AirtableClient(Table):

    # column names
    LINK = "Link"
    PRICE = "Price"
    DATE = "Date"
    NAME = "Name"
    PRODUCTS = "Products"
    ZUSTAND = "Zustand"
    PERFECT = "Perfekt"

    FORMULA = f"{{ZUSTAND}}='{PERFECT}'"

    def __init__(self, old_perfects: list[AirtableResult] = []) -> None:
        super().__init__(AT_API_KEY, AT_BASE_ID, AT_TABLE_NAME)
        self.old_perfects = old_perfects

    def read_new_perfects(self):
        results = self.all(formula=self.FORMULA)
        filtered_results = [
            result for result in results if result["id"] not in self.old_perfects]
        self.old_perfects.extend(
            [result["id"] for result in filtered_results])
        return filtered_results

    def create(self, data):
        """
          data: [{
            "date": "01/01/2005",
            "matches": [Match],
            "cost": 100,
            "poster_name": "Sanawar",
            "postal_code": 75100,
            "chat_link": "https://www.google.com"
        }]
        """
        for line in data:
            to_create = {
                "Date": line["date"],
                "Products": "\n".join([f"{match.quantity}x {match.product}" for match in line["matches"]]),
                "Price": line["cost"],
                "Name": f"{line['poster_name']} {line['postal_code']}",
                "Link": line["chat_link"]
            }

            to_create = {key: val if val else "<empty>" for key,
                         val in to_create.items()}

            return super().create(to_create)
