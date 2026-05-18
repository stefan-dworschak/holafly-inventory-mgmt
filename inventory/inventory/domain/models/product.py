from uuid import uuid4

from dataclasses import asdict, dataclass


@dataclass
class Product:
    id: uuid4
    sku: str
    name: str
    quantity: int
    low_stock_threshold: int
    
    def as_dict(self):
        return asdict(self)

