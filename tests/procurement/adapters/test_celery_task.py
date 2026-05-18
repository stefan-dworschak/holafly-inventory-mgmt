import pytest

from procurement.adapters.messaging.celery.app import send_low_stock_alert
from procurement.adapters.persistence.sqlalchemy.db import SessionLocal
from procurement.adapters.persistence.sqlalchemy.models import RestockRequestORM


@pytest.mark.integration
def test_send_low_stock_alert_runs_successfully(eager_celery):
    result = send_low_stock_alert.delay(sku="P1", quantity=2)

    assert result.successful()
    assert result.state == "SUCCESS"


@pytest.mark.integration
def test_send_low_stock_alert_persists_request(eager_celery):
    send_low_stock_alert.delay(sku="P1", quantity=2)

    with SessionLocal() as session:
        rows = session.query(RestockRequestORM).all()
        assert len(rows) == 1
        assert rows[0].sku == "P1"
        assert rows[0].stock_left == 2
