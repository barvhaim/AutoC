# AutoC Development Makefile
# Streamlines development workflows and code quality tasks

# Variables
PYTHON := uv run python
FRONTEND_DIR := frontend

# Set default target
.DEFAULT_GOAL := help

# Phony targets (not actual files)
.PHONY: help install setup dev dev-backend dev-frontend lint lint-frontend format format-backend format-frontend build-frontend clean clean-all extract

# Help target - displays available commands
help: ## Show this help message
	@echo "AutoC Development Makefile"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup & Installation
install: ## Install all dependencies (Python + Node.js)
	@echo "Installing Python dependencies..."
	uv sync
	@echo "Installing Node.js dependencies..."
	cd $(FRONTEND_DIR) && npm install
	@echo "Installation complete!"

setup: install ## Setup project (install deps + check .env)
	@if [ ! -f .env ]; then \
		echo ""; \
		echo "\033[33mWarning: .env file not found!\033[0m"; \
		echo "Please copy .env.sample to .env and configure your API keys:"; \
		echo "  cp .env.sample .env"; \
		echo ""; \
	else \
		echo ".env file found."; \
	fi

# Development Workflow
dev: ## Start backend dev server (then run dev-frontend in another terminal)
	@echo "\033[36mStarting backend server on http://localhost:8000\033[0m"
	@echo "API docs will be available at http://localhost:8000/docs"
	@echo ""
	@echo "\033[33mNote: Run 'make dev-frontend' in another terminal to start the frontend\033[0m"
	@echo ""
	$(PYTHON) -m uvicorn main:app --reload

dev-backend: ## Start backend server with hot reload
	@echo "Starting backend server on http://localhost:8000"
	@echo "API docs: http://localhost:8000/docs"
	$(PYTHON) -m uvicorn main:app --reload

dev-frontend: ## Start frontend dev server
	@echo "Starting frontend dev server on http://localhost:5173"
	cd $(FRONTEND_DIR) && npm run dev

# Code Quality
lint: lint-frontend ## Run all linters
	@echo "Linting complete!"

lint-frontend: ## Run ESLint on frontend code
	@echo "Running ESLint..."
	cd $(FRONTEND_DIR) && npm run lint

format: format-backend format-frontend ## Format all code
	@echo "Formatting complete!"

format-backend: ## Run Black on Python code
	@echo "Running Black..."
	uv run black .

format-frontend: ## Run Prettier on frontend code
	@echo "Running Prettier..."
	cd $(FRONTEND_DIR) && npm run pretty

# Build Commands
build-frontend: ## Build frontend for production
	@echo "Building frontend..."
	cd $(FRONTEND_DIR) && npm run build
	@echo "Frontend build complete! Output: $(FRONTEND_DIR)/dist"

# Utility Commands
clean: ## Remove build artifacts and caches
	@echo "Cleaning build artifacts and caches..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf $(FRONTEND_DIR)/dist 2>/dev/null || true
	@rm -rf $(FRONTEND_DIR)/node_modules/.cache 2>/dev/null || true
	@echo "Clean complete!"

clean-all: clean ## Deep clean (remove all dependencies)
	@echo "Deep cleaning all dependencies..."
	@rm -rf $(FRONTEND_DIR)/node_modules 2>/dev/null || true
	@rm -rf .venv 2>/dev/null || true
	@rm -f uv.lock 2>/dev/null || true
	@echo "Deep clean complete!"

# CLI Wrapper
extract: ## Extract IoCs from URL (usage: make extract URL=https://example.com/blog)
	@if [ -z "$(URL)" ]; then \
		echo "\033[31mError: URL parameter required\033[0m"; \
		echo "Usage: make extract URL=https://example.com/blog"; \
		exit 1; \
	fi
	@echo "Extracting IoCs from: $(URL)"
	$(PYTHON) cli.py extract --url $(URL)
