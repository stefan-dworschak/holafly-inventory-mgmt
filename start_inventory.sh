#! /bin/bash
set -e

set -a
cp .env.example .env
source .env
set +a

uv run inventory/manage.py migrate
uv run inventory/manage.py loaddata fixtures/users.json
DRF_TOKEN=$(uv run python inventory/manage.py drf_create_token admin)

echo "Created DRF Token: ${DRF_TOKEN}"

uv run python inventory/manage.py runserver 0.0.0.0:8000
