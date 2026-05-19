from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from inventory.domain.models.product import Product


class InventoryRepository(ABC):
    @abstractmethod
    def list_products(self) -> List[Product]:
        """ List all products in the inventory """

    @abstractmethod
    def add_product(
        self,
        sku: str,
        name: str,
        quantity: int = 0,
        low_stock_threshold: int = 5,
    ) -> Product:
        """ Adds a new product to the inventory """

    @abstractmethod
    def get_product_detail(self, product_id: UUID) -> Product:
        """ Gets the product details based on a product ID """

    @abstractmethod
    def update_product(
        self,
        product_id: UUID,
        sku: str = None,
        name: str = None,
        quantity: int = None,
        low_stock_threshold: int = None,
    ) -> Product:
        """ Updates the sku, name, quantity, or the low stock threshold of a product """

    @abstractmethod
    def delete_product(self, product_id: UUID) -> bool:
        """ Deletes a product from the inventory based on a product ID """
