from dataclasses import dataclass


@dataclass
class Product:
    sku: str
    name: str
    quantity: int
    low_stock_threshold: int
