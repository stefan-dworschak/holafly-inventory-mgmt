#! /bin/bash
set -e

uv run inventory/manage.py migrate
uv run inventory/manage.py loaddata fixtures/users.json
DRF_TOKEN=$(uv run python inventory/manage.py drf_create_token admin)

echo "Created DRF Token: ${DRF_TOKEN}"

cp .env.example .env
source .env

uv run python inventory/manage.py runserver 0.0.0.0:8000
