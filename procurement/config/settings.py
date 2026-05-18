import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR.parent / 'data'

DATABASE_URL = os.getenv(
    'PROCUREMENT_DATABASE_URL',
    f'sqlite:///{DATA_DIR / "procurement.sqlite3"}',
)

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_TASK_QUEUE = os.getenv('PROCUREMENT_CELERY_QUEUE', 'procurement')

API_TOKEN = os.getenv('PROCUREMENT_API_TOKEN', '')
