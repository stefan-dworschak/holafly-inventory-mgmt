from uuid import UUID

import pytest

from inventory.domain.exceptions import NotEnoughStockException
from inventory.domain.services.inventory_service import InventoryService

from inventory.adapters.persistence.django_orm.django_inventory_adapter import (
    DjangoInventoryAdapter,
)

from inventory.adapters.persistence.django_orm.models import (
    Product
)

from inventory.adapters.messaging.celery.celery_redis_notification_adapter import (
    CeleryRedisNotificationAdapter
)

@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_list_stock_levels(product: Product):
    product.save()

    inventory_adapter = DjangoInventoryAdapter()
    notification_adapter = CeleryRedisNotificationAdapter()
    inventory_service = InventoryService(inventory_adapter, notification_adapter)

    stock_levels = inventory_service.list_stock_levels()
    assert len(stock_levels) == 1

    product = stock_levels[0]
    assert product.sku == "P1"
    assert product.name == "Product 1"
    assert product.quantity == 10
    assert product.low_stock_threshold == 5


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_list_stock_levels_no_stock():
    inventory_adapter = DjangoInventoryAdapter()
    notification_adapter = CeleryRedisNotificationAdapter()
    inventory_service = InventoryService(inventory_adapter, notification_adapter)

    stock_levels = inventory_service.list_stock_levels()
    assert len(stock_levels) == 0 

@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_add_product_to_stock():
    inventory_adapter = DjangoInventoryAdapter()
    notification_adapter = CeleryRedisNotificationAdapter()
    inventory_service = InventoryService(inventory_adapter, notification_adapter)
    product = inventory_service.add_product_to_stock(
        sku="P1",
        name="Product 1",
        quantity=10,
        low_stock_threshold=5,
    )

    assert product.sku == "P1"
    assert product.name == "Product 1"
    assert product.quantity == 10
    assert product.low_stock_threshold == 5


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_get_stock_product(product: Product):
    product.save()
            
    inventory_adapter = DjangoInventoryAdapter()
    notification_adapter = CeleryRedisNotificationAdapter()
    inventory_service = InventoryService(inventory_adapter, notification_adapter)
    
    product = inventory_service.get_stock_product(product_id=UUID('c12ea36e-449b-4372-a597-362421a450b6'))
    assert product.sku == "P1"
    assert product.name == "Product 1"
    assert product.quantity == 10
    assert product.low_stock_threshold == 5 

@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_inventory_service_update_stock_for_product(product: Product):
    product.save()

    inventory_adapter = DjangoInventoryAdapter()
    notification_adapter = CeleryRedisNotificationAdapter()
    inventory_service = InventoryService(inventory_adapter, notification_adapter)

    updated_product = inventory_service.update_stock_for_product(product_id=UUID('c12ea36e-449b-4372-a597-362421a450b6'), deduct_quantity=1)
    assert updated_product.quantity == 9


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_update_stock_for_product_rejects_overdraft(product: Product):
    product.save()

    inventory_service = InventoryService(
        DjangoInventoryAdapter(), CeleryRedisNotificationAdapter()
    )

    with pytest.raises(NotEnoughStockException):
        inventory_service.update_stock_for_product(
            product_id=product.id, deduct_quantity=product.quantity + 1
        )


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_delete_product_from_stock(product: Product):
    product.save()

    inventory_adapter = DjangoInventoryAdapter()
    notification_adapter = CeleryRedisNotificationAdapter()
    inventory_service = InventoryService(inventory_adapter, notification_adapter)

    deleted = inventory_service.delete_product_from_stock(product_id=UUID('c12ea36e-449b-4372-a597-362421a450b6'))
    assert deleted == 1

