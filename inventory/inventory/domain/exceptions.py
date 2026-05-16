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

