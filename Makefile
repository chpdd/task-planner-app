# Makefile for Task Planner

# Variables
DC = docker compose
DC_DEV = $(DC)
DC_PROD = $(DC) -f docker-compose.yml
DC_TEST = $(DC) -f docker-compose.yml -f docker-compose.test.yml
FRONTEND_DIR = frontend

.PHONY: dev prod test down build help logs shell lint clean db-shell run-all run-all-stop alembic-revision alembic-upgrade alembic-upgrade-active alembic-downgrade alembic-heads

default: dev

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  dev           Run backend services (docker compose)"
	@echo "  run-all       Start full application (backend + frontend)"
	@echo "  run-all-stop  Stop full application (backend + frontend)"
	@echo "  prod          Run production verification (strict build)"
	@echo "  test          Run tests"
	@echo "  build         Build/Rebuild all images"
	@echo "  down          Stop all containers"
	@echo "  logs          Follow logs for all services"
	@echo "  shell         Enter the web container shell"
	@echo "  lint          Run code linting (ruff)"
	@echo "  clean         Remove all containers, networks, and volumes"

full:
	$(DC_DEV) up -d

planner:
	$(DC_DEV) up planner -d

prod: ## Run production verification
	$(DC_PROD) up -d

prod-build:
	$(DC_PROD) up -d --build

test: ## Run tests
	$(DC_TEST) run --rm --build planner uv run pytest -v

test-coverage:
	$(DC_TEST) run --rm planner uv run pytest --cov=.

build: ## Build images
	$(DC) build

logs: ## Follow logs
	$(DC) logs -f

shell: ## Enter web container
	$(DC_DEV) exec web bash

lint: ## Run linting
	$(DC_DEV) run --rm planner uv run ruff check .

lint-watch:
	$(DC_DEV) run --rm web planner run ruff check . -w


clean: ## Nuke everything
	$(DC) down -v --remove-orphans --rmi local

db-shell: ## Enter Postgres shell
	$(DC) exec postgres psql -U admin -d task_planner_db

# Alembic migration commands (using uv)
alembic-revision: ## Create new migration (usage: make alembic-revision msg="description")
	$(DC_DEV) run --rm planner uv run alembic -x tenant=public revision --autogenerate -m $(msg)
	$(DC) down --remove-orphans

alembic-upgrade: ## Upgrade migrations (default: head)
	$(DC_DEV) run --rm planner uv run alembic upgrade head
	$(DC) down --remove-orphans

alembic-upgrade-active: ## Upgrade in running container (default: head)
	docker compose exec planner uv run alembic upgrade head

alembic-downgrade: ## Downgrade migrations (default: -1)
	$(DC_DEV) run --rm planner uv run alembic downgrade -1
	$(DC) down --remove-orphans

alembic-heads: ## Show current migration heads
	$(DC_DEV) run --rm planner uv run alembic heads
	$(DC) down --remove-orphans

# Full application startup (backend + frontend)
up: ## Start full application (backend + frontend)
	$(DC_DEV) up -d
	@sleep 5
	@cd $(FRONTEND_DIR) && npm run dev &
	@echo "Backend: http://localhost:8081"
	@echo "Frontend: http://localhost:5173"

down: ## Stop full application (backend + frontend)
	@pkill -f "vite" 2>/dev/null || true
	$(DC) down --remove-orphans
