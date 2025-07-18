.PHONY: help test test-coverage lint format clean install install-dev build publish-check publish changelog changelog-version release bump-version dev venv setup container-build container-build-prod container-test container-shell container-push container-push-prod container-clean container-validate check

# Default target
help:
	@echo "Available targets:"
	@echo "  help       - Show this help message"
	@echo "  test       - Run all tests"
	@echo "  test-coverage - Run tests with coverage reporting"
	@echo "  lint       - Run code linting with flake8"
	@echo "  format     - Format code with black"
	@echo "  clean      - Clean build artifacts"
	@echo "  venv       - Create virtual environment (.venv)"
	@echo "  setup      - Complete setup: venv + install-dev + format + lint + test"
	@echo "  install    - Install package in development mode"
	@echo "  install-dev - Install package with development dependencies"
	@echo "  build      - Build distribution packages"
	@echo "  publish-check - Check publishing prerequisites (twine, credentials)"
	@echo "  bump-version - Bump version in both pyproject.toml and __init__.py (VERSION=x.y.z to specify)"
	@echo "  publish    - Bump version and publish to PyPI (MAINTAINERS ONLY - requires PYPI_API_TOKEN)"
	@echo "  check      - Run comprehensive quality checks"
	@echo "  changelog  - Generate changelog entry for latest version"
	@echo "  changelog-version - Generate changelog for specific version (VERSION=x.y.z)"
	@echo "  release    - Automated release: bump patch version, commit, tag, push (MAINTAINERS ONLY) (VERSION=x.y.z to override)"
	@echo "  dev        - Complete development setup (install-dev + format + lint + test)"
	@echo ""
	@echo "Container targets:"
	@echo "  container-build     - Build development container"
	@echo "  container-build-prod - Build production container"
	@echo "  container-test      - Run tests in container"
	@echo "  container-shell     - Start interactive container shell"
	@echo "  container-push      - Push development container to registry"
	@echo "  container-push-prod - Push production container to registry"
	@echo "  container-clean     - Clean up container images"
	@echo "  container-validate  - Validate all container configurations"

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
	python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	python3 -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	python3 -m black .

# Development setup
venv:
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv .venv; \
		echo "Virtual environment created in .venv"; \
		echo "To activate: source .venv/bin/activate"; \
	else \
		echo "Virtual environment .venv already exists"; \
	fi

install:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "❌ No virtual environment active. Run 'make venv && source .venv/bin/activate' first"; \
		exit 1; \
	fi
	pip install -e .

install-dev:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "❌ No virtual environment active. Run 'make venv && source .venv/bin/activate' first"; \
		exit 1; \
	fi
	pip install -e .
	pip install -r requirements-dev.txt

# Development workflow target
setup: venv
	@echo "🚀 Starting complete development setup..."
	@echo "📦 Installing development dependencies..."
	@.venv/bin/pip install -e .
	@.venv/bin/pip install -r requirements-dev.txt
	@echo "🎨 Formatting code..."
	@.venv/bin/python -m black .
	@echo "🔍 Running linting..."
	@.venv/bin/python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
	@.venv/bin/python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics || true
	@echo "🧪 Running tests..."
	@.venv/bin/python -m unittest discover -s tests -v || true
	@echo ""
	@echo "✅ Development setup complete!"
	@echo "💡 To activate the virtual environment: source .venv/bin/activate"
	@echo "🔧 Then you can use: adt -h"

dev: install-dev format lint test
	@echo "Development setup complete!"

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python3 -m build

# Quality checks
check: lint test
	@echo "All quality checks passed!"

# Changelog targets
changelog:
	@echo "Generating changelog entry..."
	./scripts/generate-changelog.sh

changelog-version:
	@if [ -z "$(VERSION)" ]; then echo "Usage: make changelog-version VERSION=0.1.7"; exit 1; fi
	@echo "Generating changelog for version $(VERSION)..."
	./scripts/generate-changelog.sh $(VERSION)

# Version management
bump-version:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION is required. Usage: make bump-version VERSION=x.y.z"; \
		exit 1; \
	fi; \
	new_version="$(VERSION)"; \
	echo "Bumping version to $$new_version..."; \
	sed -i 's/^version = .*/version = "'"$$new_version"'"/' pyproject.toml; \
	if [ -f src/adt_core/__init__.py ]; then \
		sed -i 's/^__version__ = .*/__version__ = "'"$$new_version"'"/' src/adt_core/__init__.py; \
	else \
		echo "Warning: src/adt_core/__init__.py not found, skipping..."; \
	fi; \
	echo "Version bumped to $$new_version in both files"

# Publishing dependency check
publish-check:
	@echo "Checking publishing prerequisites..."
	@if ! python3 -c "import twine" 2>/dev/null; then \
		echo "❌ twine not installed. Run 'make install-dev' or 'pip install twine'"; \
		exit 1; \
	fi
	@echo "✅ twine is available"
	@if [ -z "$$PYPI_API_TOKEN" ] && [ ! -f ~/.pypirc ]; then \
		echo "❌ No PyPI credentials found. Set PYPI_API_TOKEN or configure ~/.pypirc"; \
		exit 1; \
	fi
	@echo "✅ PyPI credentials configured"
	@echo "✅ Ready to publish"

publish: bump-version build publish-check
	@echo "Publishing to PyPI..."
	python3 -m twine upload dist/*

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

container-validate:
	@echo "Validating container configurations..."
	@echo "✅ Checking Dockerfile syntax..."
	@docker build --no-cache -f Dockerfile -t test-dev . > /dev/null 2>&1 && echo "  Dockerfile: OK" || echo "  Dockerfile: FAILED"
	@echo "✅ Checking Dockerfile.production syntax..."
	@docker build --no-cache -f Dockerfile.production -t test-prod . > /dev/null 2>&1 && echo "  Dockerfile.production: OK" || echo "  Dockerfile.production: FAILED"
	@echo "✅ Checking docker-compose syntax..."
	@docker-compose config > /dev/null 2>&1 && echo "  docker-compose.yml: OK" || (docker compose config > /dev/null 2>&1 && echo "  docker-compose.yml: OK" || echo "  docker-compose.yml: FAILED")
	@echo "✅ Cleaning up test images..."
	@docker rmi test-dev test-prod > /dev/null 2>&1 || true

# Release automation target (MAINTAINERS ONLY)
release: check
	@echo "Starting automated release process..."
	@echo "⚠️  WARNING: This target is for project maintainers only!"
	@echo "   Contributors should not use this target."
	@echo "   Continue only if you have maintainer access."
	@echo ""
	@if [ -z "$(FORCE)" ]; then \
		echo "Continue as maintainer? (y/N)"; \
		read -r confirm; \
		if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
			echo "Release cancelled."; \
			exit 1; \
		fi; \
	else \
	fi
	@# Check if we're on main/master branch
	@branch=$$(git symbolic-ref --short HEAD); \
	if [ "$$branch" != "main" ] && [ "$$branch" != "master" ]; then \
		echo "Error: Release must be done from main/master branch. Current branch: $$branch"; \
		exit 1; \
	fi
	@# Check for uncommitted changes
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Error: Working directory is not clean. Please commit or stash changes."; \
		exit 1; \
	fi
	@# Check for untracked files that might be important
	@if [ -n "$$(git status --porcelain | grep '^??')" ]; then \
		echo "Warning: Untracked files detected. Consider adding them or adding to .gitignore:"; \
		git status --porcelain | grep '^??'; \
		if [ -z "$(FORCE)" ]; then \
			echo "Continue anyway? (y/N)"; \
			read -r confirm; \
			if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
				echo "Release cancelled."; \
				exit 1; \
			fi; \
		else \
			echo "FORCE set, skipping untracked files confirmation."; \
		fi; \
	fi
	@# Determine new version
	@if [ -n "$(VERSION)" ]; then \
		new_version="$(VERSION)"; \
		echo "Using specified version: $$new_version"; \
	else \
		current_version=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
		echo "Current version: $$current_version"; \
		major=$$(echo $$current_version | cut -d. -f1); \
		minor=$$(echo $$current_version | cut -d. -f2); \
		patch=$$(echo $$current_version | cut -d. -f3); \
		new_patch=$$((patch + 1)); \
		new_version="$$major.$$minor.$$new_patch"; \
		echo "Auto-bumping patch version to: $$new_version"; \
	fi; \
	echo "Proceeding with version: $$new_version"; \
	if [ -z "$(FORCE)" ]; then \
		echo "Continue? (y/N)"; \
		read -r confirm; \
		if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
			echo "Release cancelled."; \
			exit 1; \
		fi; \
	else \
		echo "FORCE set, skipping version confirmation."; \
	fi; \
	release_branch="release/v$$new_version"; \
	echo "Creating release branch: $$release_branch"; \
	git checkout -b "$$release_branch"; \
	echo "Updating version in pyproject.toml..."; \
	if sed --version >/dev/null 2>&1; then \
		sed -i 's/^version = ".*"/version = "'"$$new_version"'"/' pyproject.toml; \
	else \
		sed -i '' 's/^version = ".*"/version = "'"$$new_version"'"/' pyproject.toml; \
	fi; \
	echo "Updating version in src/adt_core/__init__.py..."; \
	if sed --version >/dev/null 2>&1; then \
		sed -i 's/^__version__ = ".*"/__version__ = "'"$$new_version"'"/' src/adt_core/__init__.py; \
	else \
		sed -i '' 's/^__version__ = ".*"/__version__ = "'"$$new_version"'"/' src/adt_core/__init__.py; \
	fi; \
	echo "Generating changelog for version $$new_version..."; \
	if [ -f "./scripts/generate-changelog.sh" ]; then \
		./scripts/generate-changelog.sh $$new_version || true; \
	else \
		echo "Changelog script not found, skipping changelog generation."; \
	fi; \
	echo "Committing version bump..."; \
	git add pyproject.toml src/adt_core/__init__.py CHANGELOG.md; \
	git commit -m "Bump version to $$new_version"; \
	echo "Pushing release branch..."; \
	git push origin "$$release_branch"; \
	echo ""; \
	echo "🚀 Release branch $$release_branch created and pushed!"; \
	echo ""; \
	echo "Next steps:"; \
	echo "1. Create a Pull Request from $$release_branch to main"; \
	echo "2. Title: 'Release v$$new_version'"; \
	echo "3. Once CI passes, merge the PR"; \
	echo "4. After merging, create and push the tag:"; \
	echo "   git checkout main"; \
	echo "   git pull origin main"; \
	echo "   git tag v$$new_version"; \
	echo "   git push origin v$$new_version"; \
	echo "5. GitHub Actions will automatically build and publish to PyPI"