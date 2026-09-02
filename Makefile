.PHONY: help backend-setup backend-test backend-lint frontend-setup frontend-test frontend-lint test lint up down

help:
	@echo "backend-setup   cria venv e instala deps de dev do backend"
	@echo "backend-test    roda pytest"
	@echo "backend-lint    roda ruff check"
	@echo "frontend-setup  npm install"
	@echo "frontend-test   roda vitest"
	@echo "frontend-lint   roda eslint"
	@echo "test            roda os testes dos dois lados"
	@echo "lint            roda o lint dos dois lados"
	@echo "up              docker compose up --build"
	@echo "down             docker compose down"

backend-setup:
	cd backend && python3.12 -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt

backend-test:
	cd backend && . .venv/bin/activate && pytest -v

backend-lint:
	cd backend && . .venv/bin/activate && ruff check .

frontend-setup:
	cd frontend && npm install

frontend-test:
	cd frontend && npm test

frontend-lint:
	cd frontend && npm run lint

test: backend-test frontend-test

lint: backend-lint frontend-lint

up:
	docker compose up --build

down:
	docker compose down
