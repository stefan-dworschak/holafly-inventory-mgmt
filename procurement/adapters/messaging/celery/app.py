from celery import Celery

from procurement.adapters.persistence.sqlalchemy.db import init_db
from procurement.config.container import create_prod_container
from procurement.config.settings import CELERY_BROKER_URL, CELERY_TASK_QUEUE

celery_app = Celery('procurement', broker=CELERY_BROKER_URL)
celery_app.conf.task_default_queue = CELERY_TASK_QUEUE
celery_app.conf.task_ignore_result = True

init_db()
container = create_prod_container()


@celery_app.task(name='inventory.messaging.send_low_stock_alert')
def send_low_stock_alert(sku: str, quantity: int) -> None:
    container.restock_request_service.register_low_stock_alert(
        sku=sku, stock_left=quantity
    )
