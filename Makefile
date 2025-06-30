.PHONY: help test lint format clean install install-dev build publish changelog changelog-version release

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
	@echo "  publish    - Publish to PyPI (MAINTAINERS ONLY - requires PYPI_API_TOKEN)"
	@echo "  check      - Run comprehensive quality checks"
	@echo "  changelog  - Generate changelog entry for latest version"
	@echo "  changelog-version - Generate changelog for specific version (VERSION=x.y.z)"
	@echo "  release    - Automated release: bump patch version, commit, tag, push (MAINTAINERS ONLY) (VERSION=x.y.z to override)"
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
	release: check
		@set -e
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
			echo "FORCE set, skipping maintainer confirmation."; \
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
		# Portable sed for Linux and macOS
		if sed --version >/dev/null 2>&1; then \
			sed -i 's/^version = ".*"/version = "'"$$new_version"'"/' pyproject.toml; \
		else \
			sed -i '' 's/^version = ".*"/version = "'"$$new_version"'"/' pyproject.toml; \
		fi; \
		echo "Generating changelog for version $$new_version..."; \
		if [ -f "./scripts/generate-changelog.sh" ]; then \
			./scripts/generate-changelog.sh $$new_version || true; \
		else \
			echo "Changelog script not found, skipping changelog generation."; \
		fi; \
		echo "Committing version bump..."; \
		git add pyproject.toml CHANGELOG.md; \
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
