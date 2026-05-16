import pytest

from inventory.adapters.persistence.django_orm.models import (
    Product
)


@pytest.fixture(scope='module')
def product() -> Product:
    return Product(
        sku="P1",
        name="Product 1",
        quantity=10,
        low_stock_threshold=5,
    )

