class Match:
    def __init__(self, product: str, quantity: int, price: float) -> None:
        self.product = product
        self.quantity = quantity
        self.price = price

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get('product'),
            data.get('quantity'),
            data.get('price'),
        )

    def to_dict(self):
        return {
            "product": self.product,
            "quantity": self.quantity,
            "price": self.price
        }
