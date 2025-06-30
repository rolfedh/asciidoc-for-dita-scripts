.PHONY: help test lint format clean install install-dev build publish changelog

# Default target
help:
	@echo "Available targets:"
	@echo "  help       - Show this help message"
	@echo "  test       - Run all tests"
	@echo "  lint       - Run code linting with flake8"
	@echo "  format     - Format code with black"
	@echo "  clean      - Clean build artifacts"
	@echo "  install    - Install package in development mode"
	@echo "  install-dev - Install package with development dependencies"
	@echo "  build      - Build distribution packages"
	@echo "  publish    - Publish to PyPI (requires PYPI_API_TOKEN)"
	@echo "  check      - Run comprehensive quality checks"
	@echo "  changelog  - Generate changelog entry for latest version"
	@echo "  changelog-version - Generate changelog for specific version (VERSION=x.y.z)"
	@echo ""
	@echo "Container targets:"
	@echo "  container-build     - Build development container"
	@echo "  container-build-prod - Build production container"
	@echo "  container-test      - Run tests in container"
	@echo "  container-shell     - Start interactive container shell"
	@echo "  container-push      - Push development container to registry"
	@echo "  container-push-prod - Push production container to registry"
	@echo "  container-clean     - Clean up container images"

# Test targets
test:
	@echo "Running unit tests..."
	python3 -m unittest discover -s tests -v

test-coverage:
	@echo "Running tests with coverage..."
	python3 -m coverage run -m unittest discover -s tests
	python3 -m coverage report
	python3 -m coverage html

# Code quality targets
lint:
	@echo "Running flake8 linting..."
	python3 -m flake8 asciidoc_dita_toolkit/ tests/ --max-line-length=100 --ignore=E203,W503

format:
	@echo "Formatting code with black..."
	python3 -m black asciidoc_dita_toolkit/ tests/ --line-length=100

format-check:
	@echo "Checking code formatting..."
	python3 -m black asciidoc_dita_toolkit/ tests/ --line-length=100 --check

# Installation targets
install:
	@echo "Installing package in development mode..."
	python3 -m pip install -e .

install-dev:
	@echo "Installing development dependencies..."
	python3 -m pip install -r requirements-dev.txt
	python3 -m pip install -e .

# Build and distribution targets
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/
	rm -f .coverage

build: clean
	@echo "Building distribution packages..."
	python3 -m build

publish: build
	@echo "Publishing to PyPI..."
	python3 -m twine upload dist/*

# Comprehensive quality check
check: format-check lint test
	@echo "All quality checks passed!"

# CLI testing targets
test-cli: install
	@echo "Testing CLI functionality..."
	asciidoc-dita-toolkit --list-plugins
	@echo "CLI test completed successfully!"

# Development workflow target
dev: install-dev format lint test
	@echo "Development setup complete!"

# Changelog targets
changelog:
	@echo "Generating changelog entry..."
	./scripts/generate-changelog.sh

changelog-version:
	@if [ -z "$(VERSION)" ]; then echo "Usage: make changelog-version VERSION=0.1.7"; exit 1; fi
	@echo "Generating changelog for version $(VERSION)..."
	./scripts/generate-changelog.sh $(VERSION)

# Container targets
container-build:
	@echo "Building development container..."
	./scripts/container.sh build

container-build-prod:
	@echo "Building production container..."
	./scripts/container.sh build --prod

container-test:
	@echo "Running tests in container..."
	./scripts/container.sh test

container-shell:
	@echo "Starting interactive container shell..."
	./scripts/container.sh shell

container-push:
	@echo "Pushing development container to registry..."
	./scripts/container.sh push

container-push-prod:
	@echo "Pushing production container to registry..."
	./scripts/container.sh push --prod

container-clean:
	@echo "Cleaning up container images..."
	./scripts/container.sh clean
