from inventory.domain.models.product import Product

from inventory.domain.ports.repositories.inventory_repository import InventoryRepository
from inventory.domain.ports.events.events_service import EventsService

from inventory.domain.exceptions import NotEnoughStockException



class InventoryService:
    def __init__(self,
            inventory_repository: InventoryRepository,
            events_service: EventsService
        ):
        self.inventory_repository = inventory_repository 
        self.events_service = events_service 

    def process_order(self, sku: str, quantity: int) -> Product:
        product = self.inventory_repository.get_product_detail(sku=sku)

        if product.quantity - quantity < 0:
            raise NotEnoughStockException()
        
        updated_product = self.inventory_repository.update_product(
            sku=sku, quantity=(product.quantity - quantity))

        if updated_product.quantity < product.low_stock_threshold:
            self.events_service.trigger_low_stock_alert(
                sku=sku,
                quantity=updated_product.quantity
            )
        return updated_product

