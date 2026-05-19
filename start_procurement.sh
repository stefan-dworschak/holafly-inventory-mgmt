#! /bin/bash
set -e

set -a
cp .env.example .env
source .env
set +a

export CELERY_BROKER_URL=redis://localhost:6379/0

uv run --package procurement uv run \
                 uvicorn procurement.adapters.web.rest.app:app \
                 --host 0.0.0.0 --port 8010

DRF_TOKEN=$(uv run --package procurement python procurement/manage.py drf_create_token admin)

echo "Created DRF Token: ${DRF_TOKEN}"

uv run --package procurement python procurement/manage.py runserver 0.0.0.0:8010
