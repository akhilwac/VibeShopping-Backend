# Repository Guidelines

## Project Structure & Module Organization
This repository is split into `backend/` and `frontend/`. The FastAPI service lives in `backend/app/`, organized by layer: `api/v1/routes/` for endpoints, `services/` for business logic, `repositories/` for data access, `models/` for SQLAlchemy models, and `schemas/` for Pydantic contracts. Database migrations are in `backend/alembic/`, and local config examples are in `backend/.env.example`. The Vite admin UI lives in `frontend/src/`, with page-level views in `pages/`, shared UI in `components/`, API helpers in `lib/`, and static assets in `public/` and `src/assets/`.

## Build, Test, and Development Commands
Backend:
- `cd backend && source venv/bin/activate && uvicorn app.main:app --reload` starts the API locally.
- `cd backend && alembic upgrade head` applies database migrations.
- `cd backend && pytest` runs backend tests when `backend/tests/` exists.

Frontend:
- `cd frontend && npm run dev` starts the Vite dev server.
- `cd frontend && npm run build` creates a production build.
- `cd frontend && npm run lint` runs ESLint.

## Coding Style & Naming Conventions
Python targets 3.12 with Ruff and strict MyPy settings from `backend/pyproject.toml`. Use 4-space indentation, keep lines near 88 characters, prefer typed functions, and follow the existing snake_case module naming (`product_service.py`, `payment_method_repo.py`). React code uses ES modules and JSX with ESLint 9. Name components and pages in PascalCase (`Dashboard.jsx`), helpers in camelCase, and keep route or API modules descriptive and plural where appropriate.

## Testing Guidelines
Backend pytest discovery is configured for `backend/tests/` with `test_*.py`, `Test*`, and `test_*` patterns. Mark long-running or integration cases with `@pytest.mark.slow` and `@pytest.mark.integration`. Add tests alongside new backend behavior before merging. No frontend test runner is configured yet; at minimum, run `npm run lint` and document any manual UI verification in the PR.

## Commit & Pull Request Guidelines
Current history uses short subject lines (`Initial commit: ...`, `feature impelemented`), but contributors should prefer clear imperative commits such as `backend: add order status validation`. Keep commits focused. PRs should describe the change, note schema or env updates, link the related issue, and include screenshots or API examples when UI or response shapes change.

## Security & Configuration Tips
Copy `backend/.env.example` to `backend/.env` and set a strong `JWT_SECRET_KEY`; placeholder secrets are rejected by the app. Do not commit real credentials, database URLs, AWS keys, or generated virtualenv files.
