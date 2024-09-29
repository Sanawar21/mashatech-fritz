from app.models.clients import AirtableClient, KleinanzeigenClient
from app.models import AirtableEntry

ac = AirtableClient()
kc = KleinanzeigenClient()

e = AirtableEntry(
    11225544,
    "12/12/2021",
    [],
    100,
    "John Doe",
    "12345",
    "https://chat.com"
)

ac.create(e)
