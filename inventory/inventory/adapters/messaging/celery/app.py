import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

celery_app = Celery('inventory')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()


@celery_app.task(name='inventory.messaging.send_low_stock_alert')
def send_low_stock_alert(sku: str, quantity: int) -> None:
    # TODO: notify the Procurement System that stock is low for `sku`.
    pass
