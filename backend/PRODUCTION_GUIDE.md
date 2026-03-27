# Backend Production Guide

This guide explains how to think about backend deployment for this repository if you are starting from zero.

## 1. What a backend actually is

Your backend is the server-side part of your project. In this repository, it does four jobs:

1. Accept HTTP requests from the frontend or mobile app.
2. Validate input and apply business rules.
3. Read and write data in PostgreSQL.
4. Return JSON responses.

In this codebase, the important pieces are:

- `backend/app/main.py`: creates the FastAPI application.
- `backend/app/api/v1/routes/`: defines the API endpoints.
- `backend/app/services/`: contains the business logic.
- `backend/app/repositories/`: talks to the database.
- `backend/app/models/`: SQLAlchemy database models.
- `backend/alembic/`: database migration files.

## 2. What “production ready” means

Production ready does not mean perfect. It means the system can run reliably for real users with basic safety.

For this backend, production readiness means:

1. The app can start in a repeatable way.
2. Secrets are not hard-coded in source code.
3. PostgreSQL runs with persistent storage.
4. Migrations run before the app serves traffic.
5. Health checks exist for the app and database.
6. CORS is restricted to your real frontend domain.
7. Debug mode and public docs are disabled in production.
8. You have a backup plan for the database.
9. You can see logs when something fails.
10. You know how to redeploy safely.

## 3. Main production components for this project

When you deploy this backend, you are really deploying a small system:

1. API container
   Runs FastAPI with Uvicorn.
2. PostgreSQL container or managed database
   Stores users, products, orders, and all business data.
3. Redis container
   Present in your config already. It is not deeply integrated yet, but keeping it in the baseline gives you room for token revocation, caching, or background jobs later.
4. Reverse proxy / HTTPS layer
   Needed if you want a public domain with TLS.
5. Server
   A VPS or cloud machine that runs the containers.

## 4. Database basics you need to understand

### What PostgreSQL is

PostgreSQL is your primary database. It stores durable business data. If your server restarts, the data should still exist because it is written to disk.

### What Alembic migrations are

A migration is a versioned change to the database schema. Examples:

- create a `users` table
- add a `phone_number` column
- create an index for faster queries

Your backend already uses Alembic. The migration history is inside `backend/alembic/versions/`.

### Why migrations matter in deployment

Your code and database schema must match. If the code expects a column that does not exist yet, the app fails. That is why the deployment flow runs:

1. build image
2. start database
3. run `alembic upgrade head`
4. start API server

## 5. What I added for deployment

I added these files:

- `backend/Dockerfile`
- `backend/.dockerignore`
- `backend/.env.production.example`
- `docker-compose.production.yml`
- `backend/README.md`
- `backend/PRODUCTION_GUIDE.md`

I also added:

- `GET /healthz`: tells you the API process is running
- `GET /readyz`: tells you the API can reach PostgreSQL

These endpoints are used by load balancers, container orchestrators, or simple health checks.

## 6. Easiest way to understand deployment

Think of deployment as four layers:

1. Code
   Your Python application.
2. Runtime
   Python + installed packages inside a container.
3. Infrastructure
   Server, Docker, network, ports, domain, TLS.
4. Data
   PostgreSQL volume, backups, migrations.

If one layer is wrong, the app is not really deployed.

## 7. How to deploy this project on one server

This is the simplest beginner-friendly architecture:

1. Rent one Linux VPS.
2. Install Docker and Docker Compose.
3. Copy the project to the server.
4. Create `backend/.env` from `backend/.env.production.example`.
5. Set strong secrets and your real frontend domain.
6. Run `docker compose -f docker-compose.production.yml up -d --build`.
7. Check logs and health endpoints.
8. Put Nginx or Caddy in front later for HTTPS and domain routing.

### Why this is a good first deployment

It teaches the important concepts without forcing Kubernetes, managed services, or advanced cloud networking too early.

## 8. Exact first deployment steps

### On your local machine

1. Copy the production env template:

```bash
cp backend/.env.production.example backend/.env
```

2. Edit `backend/.env` and change:

- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `CORS_ORIGINS`
- AWS keys if you use S3

3. Start the stack:

```bash
docker compose -f docker-compose.production.yml up -d --build
```

4. Check the containers:

```bash
docker compose -f docker-compose.production.yml ps
```

5. Check the API health:

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

### On the server

Use the same commands after copying the project to the VPS.

## 9. Important environment variables

### `DATABASE_URL`

This tells the app how to reach PostgreSQL.

Example:

```env
DATABASE_URL=postgresql+asyncpg://postgres:strong-password@db:5432/vibeshopping
```

The password inside `DATABASE_URL` must match `POSTGRES_PASSWORD` in the same `backend/.env` file.

### `JWT_SECRET_KEY`

This signs login tokens. If this leaks, attackers can forge user sessions. Use a long random string.

### `CORS_ORIGINS`

This controls which frontend domains can call your API from browsers.

Development example:

```env
CORS_ORIGINS=["http://localhost:5173"]
```

Production example:

```env
CORS_ORIGINS=["https://admin.yourdomain.com"]
```

### `APP_ENV` and `DEBUG`

Use:

```env
APP_ENV=production
DEBUG=false
```

That disables the docs routes and avoids noisy debug behavior.

## 10. What is still missing before you call it “fully production grade”

The backend is now deployable, but not complete in an enterprise sense. The biggest next improvements are:

1. Real HTTPS termination with Nginx or Caddy.
2. Automated database backups.
3. Better logging and log retention.
4. Tests for critical flows.
5. Monitoring and alerts.
6. Redis-backed logout token revocation.
7. Rate limiting for auth endpoints.
8. CI/CD pipeline for automated deploys.

## 11. Security basics you should know

### Secrets

Never commit:

- `.env`
- database passwords
- JWT secrets
- AWS keys

### Principle of least privilege

If you later use AWS S3, create a limited IAM user that only has permission to access the needed bucket.

### Public exposure

Do not expose PostgreSQL directly to the public internet unless you know exactly why. Usually the API should be public, but the database should stay private.

### Backups

If the database volume is lost and you have no backup, your business data is gone. Backups are not optional in production.

## 12. How requests move through this system

1. Browser sends request to the API.
2. FastAPI route receives it.
3. Service layer applies business logic.
4. Repository layer queries PostgreSQL.
5. API returns JSON.

For authenticated routes:

1. Browser sends `Authorization: Bearer <token>`.
2. `backend/app/core/dependencies.py` verifies the JWT.
3. The backend checks the user exists and is active.
4. The route continues.

## 13. What Redis means in this project

Redis is an in-memory data store. It is fast, but not your main source of truth. In this repository it is configured, but not heavily used yet.

Good future uses:

- revoked token store for logout
- caching expensive queries
- Celery task queue broker
- temporary OTP or password reset tokens

## 14. What a reverse proxy does

A reverse proxy such as Nginx or Caddy sits in front of your API.

It handles:

1. HTTPS certificates
2. domain routing
3. compression
4. security headers
5. forwarding traffic to `localhost:8000`

Without it, your app can still run, but it is not the usual internet-facing production shape.

## 15. Recommended learning order for you

Do not try to learn everything at once. Learn in this order:

1. Run the backend locally with PostgreSQL.
2. Understand `.env`, `DATABASE_URL`, and migrations.
3. Start the app with Docker Compose.
4. Learn how ports, containers, and volumes work.
5. Deploy the same compose setup to one VPS.
6. Add a reverse proxy with HTTPS.
7. Set up backups.
8. Add monitoring and CI/CD.

## 16. Simple mental model

Use this mental model when you feel lost:

- FastAPI is your application.
- Uvicorn is the process that serves the application.
- Docker packages the application.
- Docker Compose runs multiple containers together.
- PostgreSQL stores the real data.
- Alembic keeps database schema in sync with code.
- Redis is optional support infrastructure.
- Nginx or Caddy makes the app safe and public on the internet.

## 17. What I recommend you do next

Your immediate next steps should be:

1. Install Docker locally if you have not already.
2. Run `docker compose -f docker-compose.production.yml up -d --build`.
3. Open `http://localhost:8000/healthz`.
4. Confirm `http://localhost:8000/readyz` works.
5. Test login and a few API flows.
6. After local success, repeat the same stack on a VPS.

## 18. Final warning

Do not treat “container runs” as “production ready.” Production readiness is really about safe secrets, recoverable data, controlled access, and predictable redeploys.
