from app.clients import AirtableClient

ac = AirtableClient()
new_perfects = ac.read_new_perfects()
print(new_perfects)
print(ac.old_perfect_ids)
