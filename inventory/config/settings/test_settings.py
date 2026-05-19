import os

# Set test defaults BEFORE importing base — base.py fails fast if any required
# env var is missing, which would otherwise prevent the test suite from loading
# in environments that don't source .env (CI, fresh checkouts).
os.environ.setdefault('SECRET_KEY', 'test-secret-key')

from .base import *  # noqa

TESTING = True

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
