from uuid import UUID
from uuid import uuid4

import pytest

from inventory.domain.exceptions import (
    ProductNotFoundException,
    NoValidUpdateDataException,
    UpdateFailedException,
    MultipleProductsFoundException,
)

from inventory.adapters.persistence.django_orm.django_inventory_adapter import (
    DjangoInventoryAdapter,
)

from inventory.adapters.persistence.django_orm.models import (
    Product
)


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_add_product():
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


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_list_products(product: Product):
    product.save()

    adapter = DjangoInventoryAdapter()
    products = adapter.list_products()
    assert len(products) == 1

    product = products[0]
    assert product.sku == "P1"
    assert product.name == "Product 1"
    assert product.quantity == 10
    assert product.low_stock_threshold == 5


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_get_product_detail(product: Product):
    product.save()

    adapter = DjangoInventoryAdapter()
    product = adapter.get_product_detail(
        product_id=UUID('c12ea36e-449b-4372-a597-362421a450b6')
    )

    assert product.sku == "P1"
    assert product.name == "Product 1"
    assert product.quantity == 10
    assert product.low_stock_threshold == 5


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_update_product(product: Product):
    product.save()

    adapter = DjangoInventoryAdapter()
    updated_product = adapter.update_product(
        product_id=UUID('c12ea36e-449b-4372-a597-362421a450b6'),
        name="Product 2"
    )

    assert updated_product.sku == "P1"
    assert updated_product.name == "Product 2"
    assert updated_product.quantity == 10
    assert updated_product.low_stock_threshold == 5

@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_update_product_exceptions(product: Product):
    product.save()

    adapter = DjangoInventoryAdapter()

    ProductNotFoundException,
    NoValidUpdateDataException,
    UpdateFailedException,
    MultipleProductsFoundException,
    with pytest.raises(ProductNotFoundException):
        adapter.update_product(product_id=uuid4())

    with pytest.raises(NoValidUpdateDataException):
        adapter.update_product(
            product_id=UUID('c12ea36e-449b-4372-a597-362421a450b6')
        )
    
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_delete_product(product: Product):
    product.save()

    adapter = DjangoInventoryAdapter()
    deleted = adapter.delete_product(product_id=product.id)
    assert deleted == 1 

