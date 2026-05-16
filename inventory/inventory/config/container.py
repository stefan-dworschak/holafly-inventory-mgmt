from dataclasses import dataclass

from inventory.domain.ports.repositories.inventory_repository import InventoryRepository

from inventory.domain.adapters.repositories.django_orm.django_inventory_repository import DjangoInventoryRepository

@dataclass
class Container:
    inventory_repository: InventoryRepository


def create_prod_container() -> Container:
    inventory_repository = DjangoInventoryRepository()


def create_test_container() -> Container:
    inventory_repository = DjangoInventoryRepository()

