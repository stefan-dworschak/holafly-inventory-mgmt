#! /bin/bash
set -e

set -a
cp .env.example .env
source .env
set +a

uv run procurement/manage.py migrate
uv run procurement/manage.py loaddata fixtures/users.json
DRF_TOKEN=$(uv run python procurement/manage.py drf_create_token admin)

echo "Created DRF Token: ${DRF_TOKEN}"

uv run python procurement/manage.py runserver 0.0.0.0:8010
