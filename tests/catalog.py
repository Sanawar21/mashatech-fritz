from app.models.catalog import Catalog

catalog = Catalog()
print(catalog.messages)
print(catalog.catalog)
print(catalog.is_enabled("universal"))
catalog.refresh()
print(catalog.messages)
print(catalog.catalog)
print(catalog.is_enabled("universal"))
