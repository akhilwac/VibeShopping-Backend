# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VibeShopping — a FastAPI e-commerce backend for a mobile shopping app. Python 3.12, async SQLAlchemy 2.0 with PostgreSQL (asyncpg), Alembic migrations, JWT auth, Pydantic V2 schemas.

## Commands

All commands run from `backend/`:

```bash
# Activate venv
source venv/bin/activate

# Run dev server
uvicorn app.main:app --reload

# Run all tests
pytest

# Run a single test file / specific test
pytest tests/test_auth.py
pytest tests/test_auth.py::test_login -v

# Lint
ruff check .
ruff check . --fix

# Type check
mypy app/

# Alembic migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Seed database
python seed.py
```

## Architecture

**Layered architecture**: Routes → Services → Repositories → SQLAlchemy Models

- **`app/api/v1/routes/`** — FastAPI route handlers. Each domain (auth, products, cart, orders, etc.) has its own file. All routes are prefixed with `/api/v1`.
- **`app/services/`** — Business logic layer. Named `*_service.py`. Services receive a DB session and call repositories.
- **`app/repositories/`** — Data access layer. Named `*_repo.py`. All extend `BaseRepository` (generic CRUD in `repositories/base.py`).
- **`app/models/`** — SQLAlchemy ORM models. All inherit from `Base` (in `db/base.py`). Use `TimestampMixin` for `created_at`/`updated_at`.
- **`app/schemas/`** — Pydantic V2 request/response schemas.
- **`app/core/`** — Cross-cutting concerns: config (`Settings` via pydantic-settings, reads `.env`), JWT security, FastAPI dependencies (`get_db`, `get_current_user`), exception handlers, response helpers.
- **`app/db/`** — Async engine and session factory (`AsyncSessionLocal`). Session auto-commits on success, rolls back on exception.

## Key Patterns

- **Dependency injection**: `get_db` yields an `AsyncSession`; `get_current_user` extracts UUID from JWT Bearer token. `get_current_user_optional` returns `None` instead of 401 for optional auth.
- **Generic repository**: `BaseRepository[ModelType]` provides `get_by_id`, `get_all`, `create`, `delete`. Repositories flush (not commit) — the session dependency handles commit/rollback.
- **App factory**: `create_app()` in `app/main.py` builds the FastAPI instance.
- **Config**: All settings from environment / `.env` file via `pydantic-settings`. See `.env.example` for required vars.
- **Alembic**: `env.py` overrides the connection string from app settings. Uses async engine. Import `app.models` to register all models with metadata for autogenerate.

## Tooling Config

- **ruff**: line-length 88, Python 3.12 target, rules: E, F, I, N, W, UP, B, A, SIM
- **mypy**: strict mode enabled
- **pytest**: asyncio_mode=auto, testpaths=["tests"], markers: `slow`, `integration`
