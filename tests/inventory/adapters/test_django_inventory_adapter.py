import pytest

from inventory.adapters.persistence.django_orm.django_inventory_adapter import (
    DjangoInventoryAdapter,
)


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_create_product():
    adapter = DjangoInventoryAdapter()
    product = adapter.add_product(
        sku="P1",
        name="Product 1",
        quantity=10,
        low_stock_threshold=5,
    )
    assert product.sku == "P1"
    assert product.name == "Product 1"
    assert product.quantity == 10
    assert product.low_stock_threshold == 5
