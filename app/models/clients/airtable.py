from ...utils import AT_API_KEY, AT_BASE_ID, AT_TABLE_NAME
from ..ad import Match, Ad
from pyairtable import Table


class AirtableEntry:
    """
    AirtableEntry represents a single entry in the Airtable database.

        Attributes:        
        ad: Ad (Ad object)
        chat_link: str (Link to the chat of the ad)

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
    def from_ad(cls, ad: Ad, chat_link: str):
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
