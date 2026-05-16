from typing import List, Protocol

from products.models import Product

class InventoryRepository(Protocol):
    def list_products(self) -> List[Product]:
        """ List all products in the inventory """
        pass
    
    def add_product(self, sku: str, name: str, quantity: int = None, low_stock_threshold: int = None) -> None:
        """ Adds a new product to the inventory """
        pass

    def get_product_detail(self, sku: str) -> Product:
        """ Gets the product details based on an SKU """
        pass

    def update_product(self, sku: str, name: str = None, quantity: int = None, low_stock_threshold: int = None) -> Product:
        """ Updates the name, quantity or the low stock threshold based on a product's SKU """
        pass

    def delete_product(self, sku: str) -> bool:
        """ Deletes a product from the inventory based on an SKU """
        pass

