.PHONY: help test run clean install examples lint format

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync

test:  ## Run all tests
	uv run pytest tests/ -v

test-fast:  ## Run tests without verbose output
	uv run pytest tests/

test-coverage:  ## Run tests with coverage report
	uv run pytest tests/ --cov=src --cov-report=term-missing

run:  ## Run the parser (50 messages)
	uv run src/ndov_train_composition.py --max-messages 50

run-debug:  ## Run the parser in debug mode (10 messages)
	uv run src/ndov_train_composition.py --debug --max-messages 10

example-1:  ## Run example 1: Basic usage
	uv run examples/example_usage.py 1

example-2:  ## Run example 2: Custom callback
	uv run examples/example_usage.py 2

example-3:  ## Run example 3: Filter by coach count
	uv run examples/example_usage.py 3

example-4:  ## Run example 4: Statistics collection
	uv run examples/example_usage.py 4

example-5:  ## Run example 5: Monitor specific train type
	uv run examples/example_usage.py 5

example-units:  ## Run units analysis example
	uv run examples/example_units_analysis.py

examples:  ## List all available examples
	uv run examples/example_usage.py

clean:  ## Clean output and data directories
	rm -rf output/* data/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

clean-all: clean  ## Clean everything including .venv
	rm -rf .venv

format:  ## Format code with ruff (if installed)
	uv run ruff format src/ tests/ examples/ 2>/dev/null || echo "ruff not installed, skipping format"

lint:  ## Lint code with ruff (if installed)
	uv run ruff check src/ tests/ examples/ 2>/dev/null || echo "ruff not installed, skipping lint"

.DEFAULT_GOAL := help
