from app.models import Catalog

catalog = Catalog()

print(", ".join(list(catalog.prices.keys())))
