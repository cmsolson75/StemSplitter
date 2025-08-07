# Makefile (Compose v2-first; set COMPOSE="docker-compose" to use v1)
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:
.SILENT:

.DEFAULT_GOAL := help
.PHONY: help build up-gpu up-cpu status logs down clean

COMPOSE ?= docker compose

# Compose project name (default matches folder name, all-lowercase)
PROJECT ?= $(shell basename $$(pwd) | tr '[:upper:]' '[:lower:]')

FRONTEND    := frontend
BACKEND_GPU := backend-gpu
BACKEND_CPU := backend-cpu

GREEN  := \033[0;32m
YELLOW := \033[1;33m
NC     := \033[0m

help: ## Show help
	printf "$(GREEN)StemSplitter$(NC)\n\n"
	printf "$(YELLOW)Commands:$(NC)\n"
	printf "  $(GREEN)build$(NC)     - Build Docker images\n"
	printf "  $(GREEN)up-gpu$(NC)    - Start GPU backend + frontend (NVIDIA)\n"
	printf "  $(GREEN)up-cpu$(NC)    - Start CPU backend + frontend\n"
	printf "  $(GREEN)status$(NC)    - Show running services and URLs\n"
	printf "  $(GREEN)logs$(NC)      - Tail logs\n"
	printf "  $(GREEN)down$(NC)      - Stop and remove services\n"
	printf "  $(GREEN)clean$(NC)     - Full teardown (containers, nets, vols)\n"

build: ## Build all images
	printf "$(GREEN)Building Docker images...$(NC)\n"
	$(COMPOSE) -p $(PROJECT) build

up-gpu: ## Start GPU backend + frontend
	printf "$(GREEN)Starting (GPU)...$(NC)\n"
	$(COMPOSE) -p $(PROJECT) up -d $(BACKEND_GPU) $(FRONTEND)
	$(MAKE) --no-print-directory status

up-cpu: ## Start CPU backend + frontend
	printf "$(GREEN)Starting (CPU)...$(NC)\n"
	$(COMPOSE) -p $(PROJECT) up -d $(BACKEND_CPU) $(FRONTEND)
	$(MAKE) --no-print-directory status

status: ## Show running services and URLs
	$(COMPOSE) -p $(PROJECT) ps
	printf "$(YELLOW)Frontend:$(NC) http://localhost:3000\n"
	printf "$(YELLOW)Backend: $(NC) http://localhost:8000\n"

logs: ## Tail logs
	$(COMPOSE) -p $(PROJECT) logs -f

down: ## Stop and remove services for this project
	printf "$(GREEN)Stopping services...$(NC)\n"
	$(COMPOSE) -p $(PROJECT) down -v --remove-orphans || true

clean: ## Full teardown for this project (force)
	printf "$(GREEN)Cleaning up StemSplitter resources...$(NC)\n"
	# Compose-aware teardown
	$(COMPOSE) -p $(PROJECT) down -v --remove-orphans || true
	# Force-remove any leftover containers, networks, volumes with the project label
	docker ps -aq --filter "label=com.docker.compose.project=$(PROJECT)" | xargs -r docker rm -f
	docker network ls -q --filter "label=com.docker.compose.project=$(PROJECT)" | xargs -r docker network rm
	docker volume ls -q --filter "label=com.docker.compose.project=$(PROJECT)" | xargs -r docker volume rm
	# Optional: prune dangling artifacts
	docker system prune -f >/dev/null 2>&1 || true
