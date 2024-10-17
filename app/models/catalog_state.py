from ..clients import AirtableClient


class CatalogState:
    __at_client = AirtableClient()
    __messages_list = None
    __products_catalog = None

    def __init__(self):
        self.update()

    @property
    def messages_list(self):
        return self.__messages_list

    @property
    def products_catalog(self):
        return self.__products_catalog

    @classmethod
    def update(cls):
        results = cls.__at_client.read_products_table()
        cls.__messages_list = {
            product.product_name: product.message
            for product in results
        }
        cls.__products_catalog = {
            product.product_name: int(product.price)
            for product in results
        }
        del cls.__products_catalog["Universal"]
