# SecureOps API

Python 3.14, FastAPI, PostgreSQL and authenticated Redis. Start the complete stack using the root Compose instructions. The API listens on port 8000. Container images run one Gunicorn/Uvicorn worker as UID 10001; scale replicas to retain correct per-process Prometheus metrics.

For local development, create a virtual environment, install `requirements-dev.txt`, and copy `.env.example` to `.env`. Generate a fresh JWT secret; the application rejects the example placeholder and secrets shorter than 32 characters. Environment variables override `.env` values. Replace database and Redis URL credentials. Staging and production reject debug mode and Redis URLs without passwords.

```sh
python -m pip install -r requirements-dev.txt
python -m alembic upgrade head
python -m scripts.seed_roles
python -m scripts.create_admin
python -m uvicorn app.main:app --reload
```

Run these commands from `backend/`. Role seeding is idempotent. Admin creation prompts for a password without echoing it. Migration commands are `python -m alembic upgrade head`, `python -m alembic downgrade -1`, and `python -m alembic revision --autogenerate -m "description"`; review generated migrations before applying them. Never downgrade a production database without a reviewed recovery plan.

API routes are under `/api/v1`. The schema at `/api/v1/openapi.json` and interactive documentation at `/api/v1/docs` are intentionally unauthenticated so staging DAST can discover routes; business API operations retain their authentication requirements. Self registration always creates a Viewer. Admins can list users, change roles and disable accounts; users cannot demote or disable their own admin account. Engineers can operate projects, services, deployments and incidents; only admins can delete projects and services or read audit logs. Mutation audit events commit in the same database transaction as their operation and retain actor/request IDs without recording passwords or tokens.

Access tokens expire after 15 minutes by default and check the current database role/status on every protected request. Refresh tokens expire after seven days, rotate on every refresh, and reject reuse, revoked records, expired records and disabled users. Clients must replace both returned tokens after refreshing. Logout revokes the submitted refresh token; existing access tokens retain their short lifetime. The historical example JWT secret must be rotated anywhere it was used.

`/health/live` confirms the process is alive; `/health/ready` checks PostgreSQL and Redis, returning 503 on either failure. `/metrics` is intended for the private monitoring network. All HTTP responses include `X-Request-ID`; error JSON and structured JSON request logs include the same ID. Forwarded client addresses are resolved by Uvicorn only for trusted proxy peers; configure `FORWARDED_ALLOW_IPS` appropriately at deployment.

Tests require explicit `TEST_DATABASE_URL` and `REDIS_URL` values pointing to disposable PostgreSQL and Redis instances. Tests create random PostgreSQL schemas and remove only those schemas; application `.env` database credentials are never used for tests. Per-test transactions roll back changes, including repository commits. The migration test separately verifies upgrade, metadata drift, downgrade and upgrade again.

```sh
python -m pytest -q
ruff check app tests scripts migrations
ruff format --check app tests scripts migrations
pip-audit -r requirements.txt
```
