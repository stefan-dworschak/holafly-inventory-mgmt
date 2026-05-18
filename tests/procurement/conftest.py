import os
import tempfile

# Must be set before any `procurement.*` import so the SQLAlchemy engine
# binds to the throwaway test database rather than the real db.sqlite3.
_db_fd, _db_path = tempfile.mkstemp(suffix=".sqlite3", prefix="procurement_test_")
os.close(_db_fd)
os.environ["PROCUREMENT_DATABASE_URL"] = f"sqlite:///{_db_path}"
os.environ["PROCUREMENT_API_TOKEN"] = "test-token"

import pytest
from fastapi.testclient import TestClient

from procurement.adapters.messaging.celery.app import celery_app
from procurement.adapters.persistence.sqlalchemy.db import SessionLocal, init_db
from procurement.adapters.persistence.sqlalchemy.models import RestockRequestORM
from procurement.adapters.web.rest.app import app

API_TOKEN = "test-token"


@pytest.fixture(autouse=True)
def procurement_db():
    init_db()
    yield
    with SessionLocal() as session:
        session.query(RestockRequestORM).delete()
        session.commit()


@pytest.fixture
def fastapi_client() -> TestClient:
    client = TestClient(app)
    client.headers.update({"Authorization": f"Bearer {API_TOKEN}"})
    return client


@pytest.fixture
def unauthed_fastapi_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def eager_celery():
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    yield
    celery_app.conf.task_always_eager = False
