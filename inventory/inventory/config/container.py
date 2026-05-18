from dataclasses import dataclass

from inventory.domain.services.inventory_service import InventoryService
from inventory.domain.ports.repositories.inventory_repository import InventoryRepository
from inventory.domain.ports.messaging.notification_dispatcher import NotificationDispatcher

from inventory.adapters.persistence.django_orm.django_inventory_adapter import (
    DjangoInventoryAdapter
)

from inventory.adapters.messaging.celery.celery_redis_notification_adapter import (
    CeleryRedisNotificationAdapter
)


@dataclass
class Container:
    inventory_repository: InventoryRepository
    notification_dispatcher: NotificationDispatcher

    inventory_service: InventoryService
    

def create_prod_container() -> Container:
    inventory_repository = DjangoInventoryAdapter()
    notification_dispatcher = CeleryRedisNotificationAdapter()
    inventory_service = InventoryService(inventory_repository, notification_dispatcher)
    
    return Container(
        inventory_repository=inventory_repository,
        notification_dispatcher=notification_dispatcher,
        inventory_service=inventory_service
    )

