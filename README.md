# Holafly Distributed Inventory & Procurement System

## Overview 

The goal is to build a Distributed Inventory & Procurement System. You must create a
system where an Inventory service manages stock levels and triggers a procurement alert when
stock is low.
### Technical Requirements
  1. **Microservice A:** Product Inventory (The Core)
    - **Framework:** Any (Django Rest Framework, FastAPI, Flask, or a simple Python script).
    - **Architecture:** Implement Hexagonal Architecture (Ports and Adapters).
    - **Business Logic:** A product cannot have negative stock. If stock drops below a configurable threshold (default: 5), trigger a "Low Stock" event.
  1. **Microservice B:** Procurement Mock
    - **Framework:** Any (Django Rest Framework, FastAPI, Flask, or a simple Python script).
    - **Function:** Expose an endpoint or listen to a queue to receive "Restock Requests" from Microservice A.


## Implementation

Two micro-services that communicate over a Celery/Redis message bus:

| Service       | Framework         | Port  | Persistence                              |
| ------------- | ----------------- | ----- | ---------------------------------------- |
| `inventory`   | Django + DRF      | 8000  | Django ORM → `data/inventory.sqlite3`    |
| `procurement` | FastAPI           | 8010  | SQLAlchemy → `data/procurement.sqlite3`  |

Both SQLite files live in the repo-root `data/` directory. In Docker the
host's `./data` is bind-mounted at `/data` so the DBs persist across
container restarts and rebuilds.

`inventory` tracks stock and emits a Celery task on low-stock thresholds.
`procurement` consumes that task and records a restock request, exposing it
via a small read API.

---

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/) (package + venv manager)
- Docker + Docker Compose *(optional — only if running via containers)*
- Redis 7 *(only if running locally without Docker — used as the Celery broker)*

---

## Setup

```bash
git clone <repo-url> holafly
cd holafly
cp .env.example .env
uv sync --all-packages
```

The repo is a uv workspace with two members (`inventory/`, `procurement/`).
`--all-packages` installs the runtime dependencies of both members into a
single `.venv` at the repo root.

### Environment variables

| Variable                     | Purpose                                  | Default                                |
| ---------------------------- | ---------------------------------------- | -------------------------------------- |
| `DEBUG`                      | Django debug mode                        | `True`                                 |
| `SECRET_KEY`                 | Django secret key                        | `devsecret`                            |
| `ALLOWED_HOSTS`              | Django allowed hosts                     | `*`                                    |
| `CELERY_BROKER_URL`          | Redis URL used by both services          | `redis://redis:6379/0`                 |
| `PROCUREMENT_API_TOKEN`      | Bearer token required by the FastAPI API | `devtoken`                             |
| `DATABASE_URL`               | Inventory DB URL                         | `sqlite:///<repo>/data/inventory.sqlite3`   |
| `PROCUREMENT_DATABASE_URL`   | Procurement DB URL                       | `sqlite:///<repo>/data/procurement.sqlite3` |

---

## Hexagonal Architecture

Both services follow Ports & Adapters. Domain logic is isolated from
frameworks; everything outside the domain plugs in via adapters.

```
<service>/
├── domain/
│   ├── models/         # Plain dataclasses (no ORM, no framework)
│   ├── services/       # Use cases — orchestrate domain logic
│   └── ports/          # Protocols / interfaces the domain depends on
│       └── repositories/
└── adapters/
    ├── persistence/    # Django ORM (inventory) / SQLAlchemy (procurement)
    ├── web/rest/       # DRF views / FastAPI routes
    └── messaging/      # Celery tasks (producer in inventory, consumer in procurement)
```

The rules:

- **Domain depends on nothing.** No imports from `adapters/`, no framework code.
- **Adapters depend on domain.** They implement the ports defined in `domain/ports/`.
- **Composition** is done in `<service>/config/container.py`, which wires
  concrete adapters into services at startup.

This means swapping SQLAlchemy for Postgres, or Celery for SQS, is a
one-adapter change — the domain doesn't know or care.

---

## Database

SQLite is the default for both services to keep local setup friction-free —
no extra container, no credentials, no `CREATE DATABASE` step. Clone the
repo, run the services, and the schema is provisioned into a file under
`data/`. This is ideal for development, demos, and the test suite, but
SQLite is not recommended for production (single-writer locking, limited
concurrency, no network access).

For production, swap the driver via the `DATABASE_URL` and
`PROCUREMENT_DATABASE_URL` environment variables — no code changes needed.

### PostgreSQL

```bash
# inventory (Django)
DATABASE_URL=postgres://user:password@db-host:5432/inventory

# procurement (SQLAlchemy)
PROCUREMENT_DATABASE_URL=postgresql+psycopg://user:password@db-host:5432/procurement
```

Install the driver: `uv add psycopg[binary]`.

### MySQL

```bash
# inventory (Django)
DATABASE_URL=mysql://user:password@db-host:3306/inventory

# procurement (SQLAlchemy)
PROCUREMENT_DATABASE_URL=mysql+pymysql://user:password@db-host:3306/procurement
```

Install the driver: `uv add mysqlclient` (inventory) and
`uv add pymysql` (procurement).

Inventory uses Django migrations (`manage.py migrate`); procurement uses
SQLAlchemy `create_all()` on startup, so neither service needs a separate
schema-management step when switching backends.

---

## Running

### With Docker (recommended)

```bash
docker compose up -d --build
```

This starts four containers: `redis`, `inventory`, `procurement`, and a
`celery` worker for procurement.

- inventory:    http://localhost:8000
- procurement:  http://localhost:8010
- redis:        localhost:6379

#### First-time setup (migrations + admin + DRF token)

The inventory image doesn't run migrations on boot. On a fresh checkout
(or after a model change), run them once against the running container:

```bash
docker compose run --rm inventory python manage.py migrate
```

Seed the admin user from the shipped fixture, then mint a DRF token:

```bash
docker compose run --rm inventory python manage.py loaddata fixtures/users.json
docker compose run --rm inventory python manage.py drf_create_token admin
```

Default dev credentials for the seeded admin user:
- **Username:** `admin`
- **Password:** `Password-1`

The Django admin is available at http://localhost:8000/admin/ — log in with
the credentials above.

Procurement uses SQLAlchemy's `create_all()` and provisions its schema on
app startup, so no separate migration step is needed.

### Without Docker

You'll need Redis running locally:

```bash
# In one terminal — Redis (or install via brew/apt)
docker run --rm -p 6379:6379 redis:7-alpine
```

Then start the three Python processes, each in its own terminal:

```bash
# Inventory (Django/DRF)
./start_inventory.sh

# Procurement (FastAPI)
./start_procurement.sh

# Procurement Celery worker
uv run celery -A procurement.adapters.messaging.celery.app worker --loglevel=info
```

---

## Tests

```bash
# Full suite
uv run pytest

# Just one service
uv run pytest tests/inventory
uv run pytest tests/procurement

# Verbose
uv run pytest -v
```

Tests are integration-style by default (`@pytest.mark.integration`) and hit
real local databases. The procurement suite spins up a throwaway SQLite
file per session; the inventory suite uses the `pytest-django` test DB.

### Coverage

```bash
# Terminal report with missing lines
uv run pytest --cov

# HTML report at htmlcov/index.html
uv run pytest --cov --cov-report=html

# Fail under a minimum threshold (handy in CI)
uv run pytest --cov --cov-fail-under=85
```

Coverage config lives under `[tool.coverage.*]` in `pyproject.toml`. The
source roots are `inventory/inventory` and `procurement`; migrations,
tests, `__init__.py`, and framework boilerplate (`manage.py`, `main.py`,
`wsgi.py`, `asgi.py`) are excluded.

---

## API Usage

Both APIs require a token. Examples below assume the services are running
locally on the default ports.

### Inventory (DRF — `Token` scheme)

Create a token for an existing user:

```bash
INVENTORY_TOKEN=$(uv run python inventory/manage.py drf_create_token admin | awk '{print $NF}')
```

List products:

```bash
curl -H "Authorization: Token $INVENTORY_TOKEN" \
     http://localhost:8000/api/v1/products/
```

Add a product:

```bash
curl -X POST http://localhost:8000/api/v1/products/ \
     -H "Authorization: Token $INVENTORY_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"sku": "P1", "name": "Product 1", "quantity": 10, "low_stock_threshold": 5}'
```

Get / update / delete:

```bash
curl -H "Authorization: Token $INVENTORY_TOKEN" \
     http://localhost:8000/api/v1/products/<product-id>

curl -X PATCH http://localhost:8000/api/v1/products/<product-id> \
     -H "Authorization: Token $INVENTORY_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"quantity": 2}'

curl -X DELETE http://localhost:8000/api/v1/products/<product-id> \
     -H "Authorization: Token $INVENTORY_TOKEN"
```

Dropping `quantity` below `low_stock_threshold` fires a Celery task to
procurement, which records a restock request.

The OpenAPI 3 schema is generated by `drf-spectacular` and served at:
- http://localhost:8000/api/schema/ (raw YAML)
- http://localhost:8000/api/docs/ (Swagger UI)
- http://localhost:8000/api/redoc/ (ReDoc)

### Procurement (FastAPI — `Bearer` scheme)

```bash
curl -H "Authorization: Bearer $PROCUREMENT_API_TOKEN" \
     http://localhost:8010/api/v1/restock-requests
```

Interactive docs (Swagger UI) are available at:
- http://localhost:8010/docs
- http://localhost:8010/redoc

### Postman

Both services expose OpenAPI specs — import either as a Postman collection
via *Import* → *Link*:

- **Inventory:** `http://localhost:8000/api/schema/` (YAML)
- **Procurement:** `http://localhost:8010/openapi.json` (JSON)

Then set auth at the collection level:
- **Inventory:** *Type* = `API Key`, *Key* = `Authorization`, *Value* = `Token <your-token>`, *Add to* = Header.
- **Procurement:** *Type* = `Bearer Token`, *Token* = `<your PROCUREMENT_API_TOKEN>`.

Requests in the collection inherit the auth header.
