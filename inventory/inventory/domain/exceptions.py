from uuid import UUID


class ProductNotFoundException(Exception):
    def __init__(self, product_id: UUID) -> None:
        super().__init__(f"Product with ID \"{product_id}\" not found")
        self.product_id = product_id

class NoValidUpdateDataException(Exception):
    pass


class UpdateFailedException(Exception):
    def __init__(self, product_id: UUID) -> None:
        super().__init__(f"Could not update product with ID \"{product_id}\"")
        self.product_id = product_id


class MultipleProductsFoundException(Exception):
    def __init__(self, product_id: UUID) -> None:
        super().__init__(f"Multiple products with ID \"{product_id}\" found")
        self.product_id = product_id


class NotEnoughStockException(Exception):
    def __init__(self, product_id: UUID, quantity: int) -> None:
        super().__init__(f"There is not enough stock for to process this order (ID: {product_id}, Quantity: {quantity}")

