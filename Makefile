.PHONY: help build up down logs clean dev-backend dev-frontend test-backend test-frontend runner train ingestion

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

ingestion: ## Run ingestion script against local DB
	docker-compose exec backend python3 ingestion_api/ingestion.py

runner: ## Run the AI prediction pipeline (update + download + predict → CSV)
	docker-compose --profile runner run --rm runner

train: ## Retrain NHL goals models
	docker-compose --profile runner run --rm runner python3 philip_snat_models/nhl/train_goals_models.py

run-soft:
	sudo systemctl stop postgresql
	docker-compose down
	docker-compose up --build

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs for all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

logs-db: ## Show database logs
	docker-compose logs -f db

clean: ## Stop services and remove volumes
	docker-compose down -v
	docker system prune -f

dev-backend: ## Start only database for backend development
	docker-compose -f docker-compose.dev.yml up db

dev-frontend: ## Start backend and database for frontend development
	docker-compose -f docker-compose.dev.yml up

test-backend: ## Run backend tests
	cd backend && python -m pytest

test-frontend: ## Run frontend tests
	cd frontend && npm test

migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MESSAGE="your message")
	cd backend && alembic revision --autogenerate -m "$(MESSAGE)"

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

start-backend: ## Start backend server locally
	cd backend && uvicorn app.main:app --reload

start-frontend: ## Start frontend server locally
	cd frontend && npm start
