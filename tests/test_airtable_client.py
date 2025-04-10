# from app.clients import AirtableClient

# ac = AirtableClient()
# new_perfects = ac.read_new_perfects()
# print(new_perfects)
# print(ac.old_perfect_ids)

from app.models import Context

ac = Context.new().at_client
ac.update("2924317417", "Products", "Test")
