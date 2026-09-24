.PHONY: init up down dev test lint build smoke observability restore-drill terraform-check

init:
	python3 scripts/init-local.py

up:
	docker compose up -d --build --wait --wait-timeout 180

down:
	docker compose down

dev:
	docker compose -f compose.yaml -f compose.dev.yaml up -d --build

test:
	bash scripts/test-backend.sh
	python3 -m unittest discover -s tests/platform
	cd frontend && npm test

lint:
	backend/.venv/bin/ruff check backend
	cd frontend && npm run lint

build:
	cd frontend && npm run build
	docker compose build

smoke:
	python3 scripts/smoke.py http://127.0.0.1:8080

observability:
	docker compose -f compose.yaml -f compose.observability.yaml up -d

restore-drill:
	python3 scripts/local-restore-drill.py

terraform-check:
	terraform -chdir=infrastructure/terraform fmt -check -recursive
	@for target in bootstrap environments/dev environments/staging environments/prod; do terraform -chdir=infrastructure/terraform/$$target validate || exit; done
