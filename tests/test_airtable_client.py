from app.clients import AirtableClient

ac = AirtableClient()
products = ac.read_products_sheet()

print(len(products))
# for product in products:
#     print(product)
