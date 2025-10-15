# AI Dungeon Master - Build System
# This Makefile provides standardized targets for dependency management, testing, and running the application

.PHONY: deps test run clean lint format help generate-client validate-openapi-client

# Default target
help:
	@echo "Available targets:"
	@echo "  deps        - Install all dependencies using uv"
	@echo "  test        - Run all tests"
	@echo "  run         - Start the backend server"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code"
	@echo "  clean       - Clean up temporary files"
	@echo "  generate-client - Generate the frontend API client from the backend OpenAPI schema"
	@echo "  validate-openapi-client - Full OpenAPI client generation validation workflow"

# Install dependencies
deps:
	@echo "Installing dependencies with uv..."
	uv sync

# Install production dependencies only
deps-prod:
	@echo "Installing production dependencies with uv..."
	uv sync --frozen --no-dev

# Run tests
test:
	@echo "Running tests..."
	uv run pytest backend/tests/ -v

# Start the application (backend server)
run:
	@echo "Starting AI Dungeon Master backend..."
	PYTHONPATH=./backend uv run python -m app.main

# Linting
lint:
	@echo "Running linting checks..."
	uv run ruff check .

# Formatting
format:
	@echo "Formatting code..."
	uv run ruff format .

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .coverage htmlcov/

# Development setup
dev-setup: deps
	@echo "Development environment setup complete!"
	@echo "Run 'make run' to start the server"

generate-client:
	@echo "Generating frontend API client..."
	./scripts/validate-openapi-client.sh || { \
		echo \"Failed to generate API client\"; \
		exit 1; \
	}

validate-openapi-client: generate-client
