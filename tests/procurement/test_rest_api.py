import pytest
from fastapi.testclient import TestClient

from procurement.adapters.persistence.sqlalchemy.db import SessionLocal
from procurement.adapters.persistence.sqlalchemy.models import RestockRequestORM


@pytest.mark.integration
def test_list_restock_requests_api_empty(fastapi_client: TestClient):
    response = fastapi_client.get("/api/v1/restock-requests")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration
def test_list_restock_requests_api(fastapi_client: TestClient):
    with SessionLocal() as session:
        session.add(RestockRequestORM(sku="P1", stock_left=2))
        session.commit()

    response = fastapi_client.get("/api/v1/restock-requests")
    assert response.status_code == 200

    body = response.json()
    assert len(body) == 1
    assert body[0]["sku"] == "P1"
    assert body[0]["stock_left"] == 2


@pytest.mark.integration
def test_list_restock_requests_api_rejects_missing_token(unauthed_fastapi_client: TestClient):
    response = unauthed_fastapi_client.get("/api/v1/restock-requests")
    assert response.status_code == 401


@pytest.mark.integration
def test_list_restock_requests_api_rejects_invalid_token(unauthed_fastapi_client: TestClient):
    response = unauthed_fastapi_client.get(
        "/api/v1/restock-requests",
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert response.status_code == 401
