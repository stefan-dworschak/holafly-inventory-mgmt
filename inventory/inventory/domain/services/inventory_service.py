from pydantic import validate_call
from typing import List
from uuid import UUID

from inventory.domain.models.product import Product

from inventory.domain.ports.repositories.inventory_repository import InventoryRepository
from inventory.domain.ports.messaging.notification_dispatcher import NotificationDispatcher

from inventory.domain.exceptions import NotEnoughStockException


class InventoryService:
    def __init__(self,
            inventory_repository: InventoryRepository,
            notification_dispatcher: NotificationDispatcher 
        ):
        self.inventory_repository = inventory_repository 
        self.notification_dispatcher = notification_dispatcher

    @validate_call(validate_return=True)
    def list_stock_levels(self) -> List[Product]:
        return self.inventory_repository.list_products()

    @validate_call(validate_return=True)
    def add_product_to_stock(self, sku: str, name: str, quantity: int, low_stock_threshold: int) -> Product:
        return self.inventory_repository.add_product(
            sku=sku,
            name=name,
            quantity=quantity,
            low_stock_threshold=low_stock_threshold
        )

    @validate_call(validate_return=True)
    def get_stock_product(self, product_id: UUID) -> Product:
        return self.inventory_repository.get_product_detail(product_id=product_id)

    @validate_call(validate_return=True)
    def update_stock_for_product(self, product_id: UUID, deduct_quantity: int) -> Product:
        product = self.inventory_repository.get_product_detail(product_id=product_id)

        if product.quantity - deduct_quantity < 0:
            raise NotEnoughStockException(product_id, deduct_quantity)

        updated_product = self.inventory_repository.update_product(
            product_id=product_id, quantity=(product.quantity - deduct_quantity))

        if updated_product.quantity < product.low_stock_threshold:
            self.notification_dispatcher.dispatch_low_stock_notification(
                sku=updated_product.sku,
                quantity=updated_product.quantity
            )
        return updated_product

    @validate_call(validate_return=True)
    def delete_product_from_stock(self, product_id: UUID) -> bool:
        return self.inventory_repository.delete_product(product_id=product_id)

