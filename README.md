# read_track_app_backend
Backend API for Read Track, a reading-habit tracker built with Flask and PostgreSQL

-----

## Database Setup (Local Development)

This project uses PostgreSQL, run locally via Docker, with SQLAlchemy + Flask-Migrate for schema management.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Python dependencies installed: `pip install -r requirements.txt`

### 1. Set up environment variables

Copy the example env file and fill in real values:

```bash
cp .env.example .env
```

The default `DATABASE_URL` in `.env.example` already matches the port and credentials configured in `docker-compose.yml` — you shouldn't need to change it.

You'll also need to add your own `NYT_BOOKS_API_KEY` to `.env`.

### 2. Start Postgres

```bash
docker compose up -d
```

Confirm it's healthy:

```bash
docker compose ps
```

You should see `bookapp-local-db` with status `Up (healthy)`.

### 3. Apply migrations

```bash
export FLASK_APP=app.app
flask db upgrade
```

This creates all tables (`books`, `users`, `reading_lists`, `progress`) based on the existing migration history in `migrations/`. You should **not** need to run `flask db init` or `flask db migrate` — those are one-time/schema-change commands already reflected in this repo.

### 4. Verify

```bash
docker exec -it bookapp-local-db psql -U postgres -d bookapp -c "\dt"
```

You should see all four tables plus `alembic_version`.

Then run the app:

```bash
flask run
```

### Troubleshooting

- **`FATAL: database "bookapp" does not exist`** — the Docker container's data volume may be stale or corrupted. Reset it and start fresh:
```bash
  docker compose down -v
  docker compose up -d
  flask db upgrade
```
- **Migration errors after pulling new changes** — someone may have added a new migration file. Just re-run `flask db upgrade` to apply anything new.