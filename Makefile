# Makefile for asciidoc-dita-toolkit

.PHONY: help install test clean lint format fetch-fixtures run-tests

# Default target
help:
	@echo "Available targets:"
	@echo "  install        Install the package in development mode"
	@echo "  test          Run all tests"
	@echo "  clean         Clean up build artifacts"
	@echo "  lint          Run linting tools"
	@echo "  format        Format code with black"
	@echo "  fetch-fixtures Fetch test fixtures from upstream"

install:  ## Install the package in development mode
	pip install -e .

test:  ## Run all tests
	python -m pytest tests/ -v

test-unit:  ## Run only unit tests (excluding fixture-based tests)
	python -m pytest tests/test_cli.py tests/test_EntityReference.py::TestEntityReference::test_basic_entity_replacement -v

clean:  ## Clean up temporary files and caches
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/

lint:  ## Run linting checks
	python -m flake8 asciidoc_dita_toolkit/ tests/ --max-line-length=120 --extend-ignore=E203,W503

format:  ## Format code with black
	python -m black asciidoc_dita_toolkit/ tests/ --line-length=120

fetch-fixtures:  ## Download test fixtures from asciidoctor-dita-vale
	./fetch-fixtures.sh

run-tests: fetch-fixtures test  ## Download fixtures and run all tests

check:  ## Run all quality checks
	$(MAKE) lint
	$(MAKE) test

dev-setup:  ## Set up development environment
	pip install -e .
	pip install pytest flake8 black

build:  ## Build distribution packages
	python -m build

install-deps:  ## Install development dependencies
	pip install -r requirements-dev.txt || echo "requirements-dev.txt is empty or missing"