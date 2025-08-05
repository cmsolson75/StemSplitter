.PHONY: help build up-gpu up-cpu down logs clean

# Colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help: ## Show help
	@echo "$(GREEN)StemSplitter$(NC)"
	@echo ""
	@echo "$(YELLOW)Commands:$(NC)"
	@echo "  $(GREEN)build$(NC)     - Build all Docker images"
	@echo "  $(GREEN)up-gpu$(NC)   - Start with GPU (NVIDIA required)"
	@echo "  $(GREEN)up-cpu$(NC)   - Start with CPU only"
	@echo "  $(GREEN)down$(NC)     - Stop all services"
	@echo "  $(GREEN)logs$(NC)     - View logs"
	@echo "  $(GREEN)clean$(NC)    - Clean up Docker resources"

build: ## Build all images
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker-compose build

up-gpu: ## Start with GPU
	@echo "$(GREEN)Starting with GPU...$(NC)"
	docker-compose up backend-gpu frontend -d
	@echo "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:8000$(NC)"

up-cpu: ## Start with CPU
	@echo "$(GREEN)Starting with CPU...$(NC)"
	docker-compose up backend-cpu frontend -d
	@echo "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:8000$(NC)"

down: ## Stop services
	@echo "$(GREEN)Stopping services...$(NC)"
	docker-compose down

logs: ## View logs
	docker-compose logs -f

clean: ## Clean up
	@echo "$(GREEN)Cleaning up StemSplitter resources...$(NC)"
	docker-compose down -v --remove-orphans  # Add --remove-orphans
	docker system prune -f