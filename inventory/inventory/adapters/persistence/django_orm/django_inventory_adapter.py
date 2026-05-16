from typing import List

from inventory.domain.exceptions import (
    ProductNotFoundException,
    NoValidUpdateDataException,
    UpdateFailedException
)
from inventory.adapters.persistence.django_orm.models import Product
from inventory.domain.ports.repositories.inventory_repository import InventoryRepository


class DjangoInventoryAdapter(InventoryRepository):
    # How to specify database here
    def list_products(self) -> List[Product]:
        """ List all products in the inventory """
        return Product.objects.all() 
    
    def add_product(self, sku: str, name: str, quantity: int = None, low_stock_threshold: int = None) -> None:
        """ Adds a new product to the inventory """
        product, created = Product.objects.get_or_create(
            sku=sku,
            defaults={
                'name': name,
                'quantity': quantity,
                'low_stock_threshold': low_stock_threshold,
            }
        )
        return product

    def get_product_detail(self, sku: str) -> Product:
        """ Gets the product details based on an SKU """
        try:
            return Product.objects.get(sku=sku)
        except Product.DoesNotExist:
            raise ProductNotFoundException(sku)

    def update_product(self, sku: str, **kwargs) -> Product:
        """ Updates the name, quantity or the low stock threshold based on a product's SKU """
        try:
            product = Product.objects.get(sku=sku)
            # Update only fields that are not none
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            if not update_data:
                raise NoValidUpdateDataException()

            updated = product.update(**update_data)
            if not updated:
                raise UpdateFailedException(sku)

            return Product.objects.get(sku=sku)
            
        except Product.DoesNotExist:
            raise ProductNotFoundException(sku)

    def delete_product(self, sku: str) -> bool:
        """ Deletes a product from the inventory based on an SKU """
        pass

