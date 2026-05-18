import pytest

from procurement.adapters.persistence.sqlalchemy.restock_request_adapter import (
    SQLAlchemyRestockRequestAdapter,
)


@pytest.mark.integration
def test_add_restock_request():
    adapter = SQLAlchemyRestockRequestAdapter()
    request = adapter.add_restock_request(sku="P1", stock_left=2)

    assert request.sku == "P1"
    assert request.stock_left == 2


@pytest.mark.integration
def test_list_restock_requests_empty():
    adapter = SQLAlchemyRestockRequestAdapter()
    assert adapter.list_restock_requests() == []


@pytest.mark.integration
def test_list_restock_requests_orders_by_recency():
    adapter = SQLAlchemyRestockRequestAdapter()
    first = adapter.add_restock_request(sku="P1", stock_left=2)
    second = adapter.add_restock_request(sku="P2", stock_left=0)

    requests = adapter.list_restock_requests()
    assert [r.id for r in requests] == [second.id, first.id]
