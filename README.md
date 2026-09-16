# AI Receipt Processing & Approval System (Airpas)

A small full-stack app for submitting receipts, running them through a mock AI/OCR extraction pipeline, and routing them to a manager for approval.

- **`api/`** — FastAPI + SQLModel backend, Postgres database, Alembic migrations.
- **`ui/airpas/`** — Angular 21 frontend (Material, `@ngrx/signals`).
- **`compose.yml`** — orchestrates `db`, `api`, and `ui` together for local development.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)

That's all you need for the standard workflow below. Running the pieces outside Docker is also possible — see [Running without Docker](#running-without-docker).

## Quick start

From the repository root:

```bash
docker compose up --build
```

This builds and starts three services:

| Service | URL                          | Notes                                   |
| ------- | ----------------------------- | ---------------------------------------- |
| `ui`    | http://localhost:4200         | Angular dev server, live-reloads on save |
| `api`   | http://localhost:8000         | FastAPI, auto-reloads on save            |
| `db`    | localhost:5432                | Postgres 17 (user/pass/db: `test`/`test`/`airpas`) |

API docs (Swagger UI) are available at http://localhost:8000/docs.

The first time you start the stack, the database will be empty — apply migrations before using the app (see below).

## Applying database migrations

With the stack running, apply migrations inside the `api` container:

```bash
docker compose exec api uv run alembic upgrade head
```

Any time you pull changes that include a new file under `api/alembic/versions/`, re-run this command.

## Using the app

1. Open http://localhost:4200 — you'll land on the login page.
2. Login is a simple mock: enter the email of an existing user in the database. There's no password; the app looks up the user by email and routes you based on their role (`is_admin` → manager view, otherwise → employee view).
3. Since the database starts empty, create a user first via the API docs (http://localhost:8000/docs) using `POST /api/users/`, setting `is_admin: true` for a manager or `false` for an employee, then log in with that email.
4. As an employee: use **New Submission** to upload a receipt (PDF/image) and pick a reviewing manager. Open the submission to run **Process with AI** (mock extraction), edit the extracted vendor/line items, then **Submit for Review**.
5. As a manager: open a submitted task to **Approve** or **Reject** (rejecting requires review notes).

## Common commands

Stop the stack:

```bash
docker compose down
```

Rebuild after dependency changes (`pyproject.toml`/`uv.lock` or `package.json`):

```bash
docker compose up --build
```

Tail logs for a single service:

```bash
docker compose logs -f api   # or ui / db
```

Open a shell in a running container:

```bash
docker compose exec api bash
docker compose exec ui sh
```

Generate a new Alembic migration after changing a model in `api/airpas/models/`:

```bash
docker compose exec api uv run alembic revision --autogenerate -m "describe the change"
docker compose exec api uv run alembic upgrade head
```

## Running without Docker

### API

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13+, plus a Postgres instance reachable from your machine.

```bash
cd api
uv sync
DATABASE_URL="postgresql://test:test@localhost:5432/airpas" uv run alembic upgrade head
DATABASE_URL="postgresql://test:test@localhost:5432/airpas" uv run uvicorn main:app --reload
```

Note: `api/dev.env` sets `DATABASE_URL` to use the Docker Compose service name `db` as the host, which only resolves inside the Compose network. When running the API directly on your host (against a Postgres exposed on `localhost:5432`, e.g. via `docker compose up db`), override `DATABASE_URL` as shown above instead of relying on `dev.env`.

### UI

Requires Node 20+.

```bash
cd ui/airpas
npm install
npm start
```

The dev server proxies `/api/*` requests to `http://api:8000` (see `ui/airpas/proxy.conf.json`), which assumes the API is reachable via Docker Compose. If running the API outside Docker, update the proxy target to `http://localhost:8000`.

## Project structure

```
api/
  airpas/
    models/      # SQLModel tables + Create/Read/Update schemas
    services/    # Business logic per resource
    routes/      # FastAPI routers
    config/      # DB connection, local file storage
  alembic/       # Migrations
ui/airpas/
  src/app/
    features/    # login, employee (submissions), manager (tasks)
    shared/      # services, signal stores, models, shared components
    style/       # global SCSS theme + component style mixins
```
