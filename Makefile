.PHONY: help test lint format clean install install-dev build publish

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
