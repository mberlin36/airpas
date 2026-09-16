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

The database starts empty and there's no signup flow, so the first thing you need to do is create some users directly through the API's Swagger docs.

### 1. Create your first users via Swagger

1. With the stack running, open http://localhost:8000/docs.
2. Expand **Users** → `POST /api/users/`, click **Try it out**.
3. Create at least one manager (approver) and one employee (submitter). Example request bodies:

   Manager:
   ```json
   {
     "first_name": "Ada",
     "last_name": "Manager",
     "email": "ada@example.com",
     "is_admin": true
   }
   ```

   Employee:
   ```json
   {
     "first_name": "Sam",
     "last_name": "Employee",
     "email": "sam@example.com",
     "is_admin": false
   }
   ```
4. Click **Execute** for each. The response body includes the new user's `id` — you won't need it for login, but it's useful if you want to inspect data later via `GET /api/users/` or `GET /api/receipts/`.

`is_admin` is what determines routing after login: `true` lands on the manager (task review) view, `false` lands on the employee (submissions) view.

### 2. Log in

1. Open http://localhost:4200 (you should land on `/login`).
2. Enter the **email** of one of the users you just created — there's no password, login is just an email lookup.
3. You'll be routed automatically based on that user's `is_admin` flag: employees go to `/employee`, managers go to `/manager`.

### 3. Walk through the workflow

As the **employee**:

1. On the submissions list, click **New Submission**.
2. Choose a receipt file (PDF or image) and pick a reviewer from the dropdown (populated from your admin/manager users).
3. Submit the dialog — this creates the receipt and uploads the file (status starts as `uploaded`).
4. Click the new row to open it in the side panel, then click **Process with AI** to run the mock extraction (status moves to `review`, with a vendor name and line items filled in).
5. Edit the vendor/line items if needed, then click **Submit for Review** (status moves to `submitted`).

As the **manager** (log out and log back in with the manager's email, or open a second browser session):

1. On the tasks list, click the row for the receipt that was just submitted.
2. Review the vendor/line items/files, add review notes, then click **Approve** or **Reject**. Rejecting requires review notes to be filled in.

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
