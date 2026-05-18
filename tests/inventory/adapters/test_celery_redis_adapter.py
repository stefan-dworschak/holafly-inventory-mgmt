import pytest

from inventory.adapters.messaging.celery.celery_redis_notification_adapter import (
    CeleryRedisNotificationAdapter,
)

@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_low_stock_alert_runs_successfully(eager_celery):
    notification_adapter = CeleryRedisNotificationAdapter()
    result = notification_adapter.dispatch_low_stock_notification(sku="P1", quantity=2)

    assert result.successful()
    assert result.state == "SUCCESS"
