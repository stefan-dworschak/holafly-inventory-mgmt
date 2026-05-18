import pytest

from procurement.adapters.persistence.sqlalchemy.restock_request_adapter import (
    SQLAlchemyRestockRequestAdapter,
)
from procurement.domain.services.restock_request_service import RestockRequestService


@pytest.mark.integration
def test_list_restock_requests_no_requests():
    service = RestockRequestService(SQLAlchemyRestockRequestAdapter())
    assert service.list_restock_requests() == []


@pytest.mark.integration
def test_register_low_stock_alert():
    service = RestockRequestService(SQLAlchemyRestockRequestAdapter())
    request = service.register_low_stock_alert(sku="P1", stock_left=2)

    assert request.sku == "P1"
    assert request.stock_left == 2


@pytest.mark.integration
def test_list_restock_requests():
    service = RestockRequestService(SQLAlchemyRestockRequestAdapter())
    service.register_low_stock_alert(sku="P1", stock_left=2)
    service.register_low_stock_alert(sku="P2", stock_left=0)

    requests = service.list_restock_requests()
    assert len(requests) == 2
    assert {r.sku for r in requests} == {"P1", "P2"}
