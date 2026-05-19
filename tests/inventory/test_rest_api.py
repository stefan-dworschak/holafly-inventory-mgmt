from uuid import UUID
from typing import Callable

import pytest

from inventory.adapters.persistence.django_orm.models import (
    Product
)


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_list_stock_levels_api(authed_client: Callable, product: Product):
    product.save()

    client, user = authed_client()
    response = client.get("/api/v1/products/", format="json")
    assert response.status_code == 200
    assert response.json() == [{
        "id": "c12ea36e-449b-4372-a597-362421a450b6",
        "sku": "P1",
        "name": "Product 1",
        "quantity": 10,
        "low_stock_threshold": 5,        
    }]


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_add_product_to_stock_api(authed_client: Callable):
    client, user = authed_client()
    product_data = {
        "sku": "P1",
        "name": "Product 1",
        "quantity": 10,
        "low_stock_threshold": 5,        
    } 
    response = client.post("/api/v1/products/", product_data, format="json")
    assert response.status_code == 201

    added_product = response.json()
    product_uuid = added_product.pop("id")
    assert isinstance(UUID(product_uuid), UUID)
    assert response.json() == {
        "sku": "P1",
        "name": "Product 1",
        "quantity": 10,
        "low_stock_threshold": 5,
    }


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_get_stock_product_api(authed_client: Callable, product: Product):
    product.save()
    client, user = authed_client()
    
    response = client.get(f"/api/v1/products/c12ea36e-449b-4372-a597-362421a450b6", format="json")
    assert response.json() == {
        "id": "c12ea36e-449b-4372-a597-362421a450b6",
        "sku": "P1",
        "name": "Product 1",
        "quantity": 10,
        "low_stock_threshold": 5,
    }



@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_update_stock_for_product_api(authed_client: Callable, product: Product):
    product.save()
    client, user = authed_client()
    
    data = {"deduct_quantity": 5}
    response = client.patch(f"/api/v1/products/c12ea36e-449b-4372-a597-362421a450b6", data, format="json")
    assert response.json() == {
        "id": "c12ea36e-449b-4372-a597-362421a450b6",
        "sku": "P1",
        "name": "Product 1",
        "quantity": 5,
        "low_stock_threshold": 5,
    }


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_delete_product_form_stock_api(authed_client: Callable, product: Product):
    product.save()
    client, user = authed_client()

    response = client.delete(f"/api/v1/products/c12ea36e-449b-4372-a597-362421a450b6", format="json")
    assert response.status_code == 204


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_add_product_duplicate_sku_returns_409(authed_client: Callable, product: Product):
    product.save()
    client, _ = authed_client()

    duplicate = {
        "sku": "P1",
        "name": "Another Product 1",
        "quantity": 1,
        "low_stock_threshold": 1,
    }
    response = client.post("/api/v1/products/", duplicate, format="json")
    assert response.status_code == 409
    assert "P1" in response.json()["error"]


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_get_missing_product_returns_404(authed_client: Callable):
    client, _ = authed_client()
    response = client.get(
        "/api/v1/products/00000000-0000-0000-0000-000000000000", format="json"
    )
    assert response.status_code == 404

