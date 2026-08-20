.PHONY: up down seed-public prod-config prod-up prod-down prod-seed-public docker-test api-test api-lint web-check eval live-eval smoke ops-check

LIVE_API_URL ?= http://localhost:8000/api/v1

up:
	docker compose -f compose.yaml -f compose.local.yaml up --build

down:
	docker compose -f compose.yaml -f compose.local.yaml down

seed-public:
	docker compose -f compose.yaml -f compose.local.yaml exec -T api python3 -m app.seed_public

prod-config:
	docker compose -f compose.yaml -f compose.prod.yaml config --quiet

prod-up:
	docker compose -f compose.yaml -f compose.prod.yaml up -d --build

prod-down:
	docker compose -f compose.yaml -f compose.prod.yaml down

prod-seed-public:
	docker compose -f compose.yaml -f compose.prod.yaml exec -T api python3 -m app.seed_public

docker-test:
	docker build --target test -t evidence-rag-api-test ./apps/api
	docker run --rm evidence-rag-api-test
	docker build --target test -t evidence-rag-web-test ./apps/web
	docker run --rm evidence-rag-web-test

api-test:
	cd apps/api && python3 -m pytest -q

api-lint:
	cd apps/api && python3 -m ruff check app tests

web-check:
	cd apps/web && pnpm lint && pnpm typecheck && pnpm test && pnpm build

eval:
	cd apps/api && python3 ../../scripts/run_evals.py

live-eval:
	python3 scripts/run_live_evals.py --api-url $(LIVE_API_URL)

smoke:
	python3 scripts/smoke_api.py

ops-check:
	python3 infra/ops/check_policy.py
