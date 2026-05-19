from typing import List
from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from pydantic import ConfigDict, validate_call

from inventory.adapters.persistence.django_orm.models import Product as DjangoProduct
from inventory.domain.exceptions import (
    DuplicateSkuException,
    InvalidProductDataException,
    MultipleProductsFoundException,
    NoValidUpdateDataException,
    ProductNotFoundException,
    UpdateFailedException,
)
from inventory.domain.models.product import Product as DomainProduct
from inventory.domain.ports.repositories.inventory_repository import InventoryRepository

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
    def add_product(
        self,
        sku: str,
        name: str,
        quantity: int = 0,
        low_stock_threshold: int = 5,
    ) -> DomainProduct:
        """ Adds a new product to the inventory; rejects duplicate SKUs """
        try:
            product = DjangoProduct.objects.create(
                sku=sku,
                name=name,
                quantity=quantity,
                low_stock_threshold=low_stock_threshold,
            )
        except IntegrityError:
            raise DuplicateSkuException(sku)
        return self._to_domain(product)

    @validated
    def get_product_detail(self, product_id: UUID) -> DomainProduct:
        """ Gets the product details based on a product ID """
        try:
            return self._to_domain(DjangoProduct.objects.get(id=product_id))
        except DjangoProduct.DoesNotExist:
            raise ProductNotFoundException(product_id)

    @validated
    def update_product(
        self,
        product_id: UUID,
        sku: str = None,
        name: str = None,
        quantity: int = None,
        low_stock_threshold: int = None,
    ) -> DomainProduct:
        """ Updates fields on a product, applying model validators and refreshing
        ``updated_at``. Raises ``InvalidProductDataException`` on validator failure
        and ``NoValidUpdateDataException`` when no fields are provided. """
        try:
            product = DjangoProduct.objects.get(id=product_id)
        except DjangoProduct.DoesNotExist:
            raise ProductNotFoundException(product_id)
        except DjangoProduct.MultipleObjectsReturned:
            raise MultipleProductsFoundException(product_id)

        update_data = {
            key: value
            for key, value in {
                "sku": sku,
                "name": name,
                "quantity": quantity,
                "low_stock_threshold": low_stock_threshold,
            }.items()
            if value is not None
        }
        if not update_data:
            raise NoValidUpdateDataException()

        for field, value in update_data.items():
            setattr(product, field, value)

        try:
            product.full_clean()
        except DjangoValidationError as error:
            raise InvalidProductDataException(product_id, error.message_dict)

        try:
            product.save(update_fields=[*update_data.keys(), "updated_at"])
        except IntegrityError:
            if "sku" in update_data:
                raise DuplicateSkuException(update_data["sku"])
            raise UpdateFailedException(product_id)

        return self._to_domain(product)

    @validated
    def delete_product(self, product_id: UUID) -> bool:
        """ Deletes a product from the inventory based on a product ID """
        product = DjangoProduct.objects.filter(id=product_id)
        if not product.exists():
            raise ProductNotFoundException(product_id)

        if product.count() > 1:
            raise MultipleProductsFoundException(product_id)

        deleted, _ = product.delete()
        return deleted
