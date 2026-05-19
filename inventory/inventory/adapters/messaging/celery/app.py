import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

celery_app = Celery('inventory')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()


@celery_app.task(name='inventory.messaging.send_low_stock_alert')
def send_low_stock_alert(sku: str, quantity: int) -> None:
    """Producer-side registration for the low-stock alert task.

    The inventory service only *emits* this task — the actual consumer lives
    in the procurement service (``procurement.adapters.messaging.celery``),
    where a worker subscribed to the same task name records a restock request.
    This body is intentionally a no-op; do not add inventory-side handling here.
    """
    return None
