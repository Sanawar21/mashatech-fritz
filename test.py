from app.cache import AirtableCache

atc = AirtableCache()

print(atc.read_old_perfect_ids())
# atc.update_old_perfect_ids(["1", "2", "3"])
print(atc.read_old_perfect_ids())
# atc.clear_data()
