from uuid import uuid4

import pytest

from inventory.domain.exceptions import NegativeProductValueException
from inventory.domain.models.product import Product


def test_product_rejects_negative_quantity():
    with pytest.raises(NegativeProductValueException) as excinfo:
        Product(
            id=uuid4(),
            sku="P-NEG",
            name="Bad Product",
            quantity=-1,
            low_stock_threshold=5,
        )
    assert excinfo.value.field == "quantity"
    assert excinfo.value.value == -1


def test_product_rejects_negative_low_stock_threshold():
    with pytest.raises(NegativeProductValueException) as excinfo:
        Product(
            id=uuid4(),
            sku="P-NEG-THR",
            name="Bad Product",
            quantity=5,
            low_stock_threshold=-1,
        )
    assert excinfo.value.field == "low_stock_threshold"
    assert excinfo.value.value == -1


def test_product_accepts_zero_quantity():
    product = Product(
        id=uuid4(),
        sku="P-ZERO",
        name="Empty Shelf",
        quantity=0,
        low_stock_threshold=0,
    )
    assert product.quantity == 0
    assert product.low_stock_threshold == 0
