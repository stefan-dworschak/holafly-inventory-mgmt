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
        super().__init__(
            f"There is not enough stock to process this order "
            f"(ID: {product_id}, Quantity: {quantity})"
        )


class DuplicateSkuException(Exception):
    def __init__(self, sku: str) -> None:
        super().__init__(f"A product with SKU \"{sku}\" already exists")
        self.sku = sku


class InvalidProductDataException(Exception):
    def __init__(self, product_id: UUID, errors: dict) -> None:
        super().__init__(
            f"Invalid update data for product \"{product_id}\": {errors}"
        )
        self.product_id = product_id
        self.errors = errors


class NegativeProductValueException(Exception):
    def __init__(self, field: str, value: int) -> None:
        super().__init__(
            f"Product {field} cannot be negative (got {value})"
        )
        self.field = field
        self.value = value
