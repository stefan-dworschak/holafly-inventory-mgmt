from uuid import UUID

import pytest

from inventory.adapters.messaging.celery.app import celery_app
from inventory.adapters.persistence.django_orm.models import (
    Product
)


@pytest.fixture(scope='module')
def product() -> Product:
    return Product(
        id=UUID('c12ea36e-449b-4372-a597-362421a450b6'),
        sku="P1",
        name="Product 1",
        quantity=10,
        low_stock_threshold=5,
    )


@pytest.fixture
def eager_celery():
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True  # re-raise exceptions
    yield
    celery_app.conf.task_always_eager = False

