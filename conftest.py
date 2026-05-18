from uuid import UUID
from typing import Callable

import pytest
from django.contrib.auth.models import AbstractBaseUser
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from inventory.adapters.messaging.celery.app import celery_app
from inventory.adapters.persistence.django_orm.models import (
    Product
)

@pytest.fixture
def make_user(django_user_model) -> Callable[..., AbstractBaseUser]:
    def _make(**overrides) -> AbstractBaseUser:
        defaults = {"username": "tester", "password": "pw"}
        return django_user_model.objects.create_user(**{**defaults, **overrides})
    return _make


@pytest.fixture
def authed_client(make_user) -> Callable[..., tuple[APIClient, AbstractBaseUser]]:
    def _build(**user_overrides) -> tuple[APIClient, AbstractBaseUser]:
        user = make_user(**user_overrides)
        token, _ = Token.objects.get_or_create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        return client, user
    return _build


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

