from app.models import AirtableClient

ac = AirtableClient()
t = ac.read_new_perfects()
print(t)
