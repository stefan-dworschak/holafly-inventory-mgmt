from typing import List
from uuid import UUID

from pydantic import validate_call
from pydantic import ConfigDict

from inventory.domain.exceptions import (
    ProductNotFoundException,
    NoValidUpdateDataException,
    UpdateFailedException,
    MultipleProductsFoundException,
)
from inventory.adapters.persistence.django_orm.models import Product as DjangoProduct
from inventory.domain.ports.repositories.inventory_repository import InventoryRepository
from inventory.domain.models.product import Product as DomainProduct

validated = validate_call(
    config=ConfigDict(arbitrary_types_allowed=True),
    validate_return=True,
)


class DjangoInventoryAdapter(InventoryRepository):
    @staticmethod
    def _to_domain(product: DjangoProduct) -> DomainProduct:
        return DomainProduct(
            id=product.id,
            sku=product.sku,
            name=product.name,
            quantity=product.quantity,
            low_stock_threshold=product.low_stock_threshold,
        )

    @validated
    def list_products(self) -> List[DomainProduct]:
        """ List all products in the inventory """
        return [self._to_domain(product) for product in DjangoProduct.objects.all()]

    @validated
    def add_product(self, sku: str, name: str, quantity: int = None, low_stock_threshold: int = None) -> DomainProduct:
        """ Adds a new product to the inventory """
        product, created = DjangoProduct.objects.get_or_create(
            sku=sku,
            defaults={
                'name': name,
                'quantity': quantity,
                'low_stock_threshold': low_stock_threshold,
            }
        )
        return self._to_domain(product)

    @validated
    def get_product_detail(self, product_id: UUID) -> DomainProduct:
        """ Gets the product details based on an SKU """
        try:
            return self._to_domain(DjangoProduct.objects.get(id=product_id))
        except DjangoProduct.DoesNotExist:
            raise ProductNotFoundException(product_id)

    @validated
    def update_product(self, product_id: UUID, **kwargs) -> DomainProduct:
        """ Updates the name, quantity or the low stock threshold based on a product's SKU """
        product = DjangoProduct.objects.filter(id=product_id)
        if not product.exists():
            raise ProductNotFoundException(product_id)

        if product.count() > 1:
            raise MultipleProductsFoundException(product_id)

        # Update only fields that are not none
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        if not update_data:
            raise NoValidUpdateDataException()

        updated = product.update(**update_data)
        if not updated:
            raise UpdateFailedException(product_id)

        return self._to_domain(DjangoProduct.objects.get(id=product_id))

    @validated
    def delete_product(self, product_id: UUID) -> bool:
        """ Deletes a product from the inventory based on an SKU """
        product = DjangoProduct.objects.filter(id=product_id)
        if not product.exists():
            raise ProductNotFoundException(product_id)
    
        if product.count() > 1:
            raise MultipleProductsFoundException(product_id)

        deleted, deleted_count = product.delete()
        return deleted

