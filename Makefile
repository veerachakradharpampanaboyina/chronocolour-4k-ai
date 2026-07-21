# ============================================================
# ChronoColor 4K AI — Makefile
# ============================================================

.PHONY: help dev prod down logs test lint clean models

COMPOSE = docker compose
COMPOSE_PROD = docker compose -f docker-compose.prod.yml

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Development ---

dev: ## Start all services in development mode
	$(COMPOSE) up -d --build
	@echo "\n✅ ChronoColor 4K AI is running!"
	@echo "   Dashboard:  http://localhost:3000"
	@echo "   API Docs:   http://localhost:8000/docs"
	@echo "   Flower:     http://localhost:5555"
	@echo "   MinIO:      http://localhost:9001"

dev-api: ## Start only the API server (no workers)
	$(COMPOSE) up -d api redis mongodb minio

dev-worker: ## Start only the GPU worker
	$(COMPOSE) up -d worker-gpu redis mongodb minio

# --- Production ---

prod: ## Start all services in production mode
	$(COMPOSE_PROD) up -d --build

# --- Lifecycle ---

down: ## Stop all services
	$(COMPOSE) down

down-v: ## Stop all services and remove volumes
	$(COMPOSE) down -v

restart: ## Restart all services
	$(COMPOSE) restart

logs: ## Tail logs for all services
	$(COMPOSE) logs -f

logs-api: ## Tail API server logs
	$(COMPOSE) logs -f api

logs-worker: ## Tail GPU worker logs
	$(COMPOSE) logs -f worker-gpu

# --- Testing ---

test: ## Run all tests
	$(COMPOSE) exec api pytest tests/ -v

test-api: ## Run API tests only
	$(COMPOSE) exec api pytest tests/backend/test_api/ -v

test-ai: ## Run AI module tests
	$(COMPOSE) exec worker-gpu pytest tests/backend/test_ai/ -v

# --- Code Quality ---

lint: ## Run linters
	$(COMPOSE) exec api ruff check backend/
	$(COMPOSE) exec api mypy backend/app/

format: ## Auto-format code
	$(COMPOSE) exec api ruff format backend/

# --- Models ---

models: ## Download all AI model weights
	bash scripts/download_models.sh

# --- Utilities ---

shell-api: ## Open a shell in the API container
	$(COMPOSE) exec api bash

shell-worker: ## Open a shell in the worker container
	$(COMPOSE) exec worker-gpu bash

db-shell: ## Open MongoDB shell
	$(COMPOSE) exec mongodb mongosh chronocolor

redis-cli: ## Open Redis CLI
	$(COMPOSE) exec redis redis-cli

clean: ## Remove all containers, volumes, and cached data
	$(COMPOSE) down -v --rmi local
	rm -rf backend/__pycache__ backend/app/__pycache__
	rm -rf frontend/.next frontend/node_modules
	@echo "✅ Cleaned up!"
