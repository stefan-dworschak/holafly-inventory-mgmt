import pytest

from tests.fixtures import product

from inventory.domain.services.inventory_service import InventoryService

from inventory.adapters.persistence.django_orm.django_inventory_adapter import (
    DjangoInventoryAdapter,
)

from inventory.adapters.persistence.django_orm.models import (
    Product
)

from inventory.adapters.events.celery.celery_events_adapter import (
    CeleryEventsAdapter
)


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_inventory_service_process_order(product: Product):
    product.save()

    inventory_adapter = DjangoInventoryAdapter()
    events_adapter = CeleryEventsAdapter()
    inventory_service = InventoryService(inventory_adapter, events_adapter)

    updated_product = inventory_service.process_order(sku="P1", quantity=1)
    assert updated_product.quantity == 9

