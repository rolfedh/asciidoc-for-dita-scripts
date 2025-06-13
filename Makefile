# Makefile for asciidoc-dita-toolkit development

.PHONY: help install install-dev test test-coverage clean lint format build upload-test upload demo

help:	## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install:	## Install the package in development mode
	pip install -e .

install-dev:	## Install with development dependencies
	pip install -e ".[dev]"
	pip install pre-commit
	pre-commit install

test:		## Run tests
	python -m pytest tests/ -v

test-coverage:	## Run tests with coverage report
	python -m pytest tests/ -v --cov=asciidoc_dita --cov-report=html --cov-report=term

clean:		## Clean build artifacts and cache files
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/

lint:		## Run linting checks
	flake8 asciidoc_dita_toolkit/ tests/
	black --check asciidoc_dita_toolkit/ tests/
	isort --check-only asciidoc_dita_toolkit/ tests/

format:		## Format code with black and isort
	black asciidoc_dita_toolkit/ tests/
	isort asciidoc_dita_toolkit/ tests/

build:		## Build distribution packages
	python -m build

upload-test:	## Upload to TestPyPI
	python -m twine upload --repository testpypi dist/*

upload:		## Upload to PyPI
	python -m twine upload dist/*

demo:		## Run a quick demo of the CLI
	@echo "Available plugins:"
	asciidoc-dita --list-plugins
	@echo "\nTesting EntityReference plugin:"
	echo "Test with &copy; symbol" > demo.adoc
	asciidoc-dita EntityReference -f demo.adoc
	@echo "Result:"
	cat demo.adoc
	rm -f demo.adoc
