#! /bin/bash
set -e

set -a
cp .env.example .env
source .env
set +a

export CELERY_BROKER_URL=redis://localhost:6379/0
uv run --package procurement celery -A procurement.adapters.messaging.celery.app worker --loglevel=info

