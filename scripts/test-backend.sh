#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
test_id="secureops-ci-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:12])')"
test_password="$(python3 -c 'import secrets; print(secrets.token_hex(24))')"
cleanup() { docker rm -f "$test_id-db" "$test_id-redis" >/dev/null 2>&1 || true; }
trap cleanup EXIT
docker run -d --name "$test_id-db" -e POSTGRES_USER=secureops_test -e POSTGRES_DB=secureops_test -e POSTGRES_PASSWORD="$test_password" -p 127.0.0.1::5432 postgres:16.10-alpine >/dev/null
docker run -d --name "$test_id-redis" -p 127.0.0.1::6379 redis:7.4.5-alpine redis-server --requirepass "$test_password" >/dev/null
for attempt in $(seq 1 30); do
  if docker exec "$test_id-db" pg_isready -U secureops_test >/dev/null 2>&1; then break; fi
  sleep 1
done
db_port="$(docker port "$test_id-db" 5432/tcp | awk -F: '{print $NF}')"
redis_port="$(docker port "$test_id-redis" 6379/tcp | awk -F: '{print $NF}')"
export DATABASE_URL="postgresql+psycopg://secureops_test:$test_password@127.0.0.1:$db_port/secureops_test"
export TEST_DATABASE_URL="$DATABASE_URL"
export REDIS_URL="redis://:$test_password@127.0.0.1:$redis_port/0"
export JWT_SECRET="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
export ENVIRONMENT=local
mkdir -p reports
cd backend
"${BACKEND_PYTHON:-.venv/bin/python}" -m pytest -q --junitxml=../reports/backend-tests.xml
