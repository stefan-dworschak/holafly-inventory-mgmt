from pydantic import validate_call

from inventory.adapters.messaging.celery.app import send_low_stock_alert
from inventory.domain.ports.messaging.notification_dispatcher import NotificationDispatcher


class CeleryRedisNotificationAdapter(NotificationDispatcher):
    @validate_call
    def dispatch_low_stock_notification(self, sku: str, quantity: int) -> None:
        return send_low_stock_alert.delay(sku=sku, quantity=quantity)
