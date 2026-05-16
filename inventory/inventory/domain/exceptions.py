class ProductNotFoundException(Exception):
    def __init__(self, sku: str) -> None:
        super().__init__(f"Product with SKU \"{sku}\" not found")
        self.sku = sku

class NoValidUpdateDataException(Exception):
    pass


class UpdateFailedException(Exception):
    def __init__(self, sku: str) -> None:
        super().__init__(f"Could not update product with SKU \"{sku}\"")
        self.sku = sku


class MultipleProductsFoundException(Exception):
    def __init__(self, sku: str) -> None:
        super().__init__(f"Multiple products with SKU \"{sku}\" found")
        self.sku = sku


class NotEnoughStockException(Exception):
    def __init__(self, sku: str, quantity: int) -> None:
        super().__init__(f"There is not enough stock for to process this order (SKU: {sku}, Quantity: {quantity}")

