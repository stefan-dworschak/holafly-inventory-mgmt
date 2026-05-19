import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR.parent / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv(
    'PROCUREMENT_DATABASE_URL',
    f'sqlite:///{DATA_DIR / "procurement.sqlite3"}',
)

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_TASK_QUEUE = os.getenv('PROCUREMENT_CELERY_QUEUE', 'procurement')

# Required — fail fast at startup rather than booting with an empty token
# (which would silently reject every request as "Invalid bearer token").
try:
    API_TOKEN = os.environ['PROCUREMENT_API_TOKEN']
except KeyError as exc:
    raise RuntimeError(
        "PROCUREMENT_API_TOKEN is not set. Configure it via the "
        "PROCUREMENT_API_TOKEN environment variable (see .env.example). "
        "Never reuse the example value in production."
    ) from exc
