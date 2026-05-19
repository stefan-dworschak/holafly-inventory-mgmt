from uuid import uuid4

from dataclasses import asdict, dataclass

from inventory.domain.exceptions import NegativeProductValueException


@dataclass
class Product:
    id: uuid4
    sku: str
    name: str
    quantity: int
    low_stock_threshold: int

    def __post_init__(self) -> None:
        if self.quantity < 0:
            raise NegativeProductValueException("quantity", self.quantity)

        if self.low_stock_threshold < 0:
            raise NegativeProductValueException(
                "low_stock_threshold", self.low_stock_threshold
            )

    def as_dict(self):
        return asdict(self)
