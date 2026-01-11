.PHONY: help install install-dev setup clean lint format type-check test test-unit test-integration coverage run docker-build docker-run

.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Java Code Analyzer - Development Commands"
	@echo "=========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt
	pip install -e .

install-dev: ## Install development dependencies
	pip install --upgrade pip setuptools wheel
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install

setup: install-dev ## Complete project setup
	@echo "Creating .env file from template..."
	@if [ ! -f .env ]; then cp .env.example .env; echo ".env created - Please add your API keys!"; else echo ".env already exists"; fi
	@echo "Setup complete! Run 'make test' to verify."

clean: ## Clean build artifacts and cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .mypy_cache/
	@echo "Cleaned build artifacts and cache"

lint: ## Run linting checks
	@echo "Running ruff..."
	ruff check src/ tests/
	@echo "✓ Linting passed"

format: ## Format code with black
	@echo "Running black..."
	black src/ tests/
	@echo "Running ruff --fix..."
	ruff check --fix src/ tests/
	@echo "✓ Code formatted"

type-check: ## Run type checking with mypy
	@echo "Running mypy..."
	mypy src/
	@echo "✓ Type checking passed"

test: ## Run all tests
	pytest tests/ -v --cov=analyzer --cov-report=term-missing

test-unit: ## Run unit tests only
	pytest tests/unit/ -v -m unit

test-integration: ## Run integration tests only
	pytest tests/integration/ -v -m integration

coverage: ## Generate HTML coverage report
	pytest tests/ --cov=analyzer --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"
	@python -m webbrowser htmlcov/index.html 2>/dev/null || true

quality: lint type-check test ## Run all quality checks

run: ## Run the analyzer (example)
	@echo "Running analyzer on sample code..."
	python -m analyzer.cli.main analyze tests/fixtures/sample_code/BadCode.java

run-debug: ## Run with debug logging
	LOG_LEVEL=DEBUG python -m analyzer.cli.main analyze tests/fixtures/sample_code/BadCode.java --verbose

docker-build: ## Build Docker image
	docker build -t java-code-analyzer:latest .

docker-run: ## Run Docker container
	docker run --rm -it \
		--env-file .env \
		-v $(PWD)/data:/app/data \
		java-code-analyzer:latest

dev: ## Start development session
	@echo "Activating virtual environment and setting up development mode..."
	@echo "Run: source venv/bin/activate"
	@echo "Then: python -m analyzer.cli.main --help"

check-env: ## Check if environment is properly configured
	@echo "Checking environment configuration..."
	@python -c "from config.settings import settings; print(f'✓ Settings loaded'); print(f'  Environment: {settings.environment}'); print(f'  Primary LLM: {settings.primary_llm}'); print(f'  Log Level: {settings.log_level}')"
	@echo "✓ Environment check passed"

health: ## Run comprehensive health check
	@python scripts/health_check.py

status: health ## Alias for health check