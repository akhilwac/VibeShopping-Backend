# VibeShopping Backend

This backend is a FastAPI application with:

- FastAPI for HTTP APIs
- SQLAlchemy async ORM for database access
- Alembic for database migrations
- PostgreSQL as the primary database
- JWT authentication for user sessions

## Local development

1. Copy `backend/.env.example` to `backend/.env`.
2. Set a strong `JWT_SECRET_KEY`.
3. Start PostgreSQL locally.
4. Run migrations:

```bash
cd backend
alembic upgrade head
```

5. Start the API:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

## Production deployment

Use the compose file at the repository root:

```bash
cp backend/.env.production.example backend/.env
docker compose -f docker-compose.production.yml up -d --build
```

The API exposes:

- `GET /healthz` for liveness
- `GET /readyz` for database readiness

Read the deployment guide in `backend/PRODUCTION_GUIDE.md` before deploying.
