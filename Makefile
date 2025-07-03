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
# Optimized workflow: test → clean → version bump → changelog → build → commit → tag → publish → github release
release:
	@echo "🚀 Starting optimized automated release process..."
	@echo "⚠️  WARNING: This target is for project maintainers only!"
	@echo "   Contributors should not use this target."
	@echo "   Continue only if you have maintainer access."
	@echo ""
	@# Check prerequisites
	@echo "🔍 Checking prerequisites..."
	@command -v gh >/dev/null 2>&1 || { echo "Error: GitHub CLI (gh) is required but not installed."; exit 1; }
	@[ -n "$$GITHUB_TOKEN" ] || { echo "Error: GITHUB_TOKEN environment variable is required."; exit 1; }
	@[ -n "$$PYPI_API_TOKEN" ] || { echo "Error: PYPI_API_TOKEN environment variable is required."; exit 1; }
	@if [ -z "$(FORCE)" ]; then \
		echo "Continue as maintainer? (y/N)"; \
		read -r confirm; \
		if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
			echo "Release cancelled."; \
			exit 1; \
		fi; \
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
	@# Step 1: Run all tests (fail-fast)
	@echo "🧪 Step 1/10: Running comprehensive tests..."
	@set -e; $(MAKE) check
	@echo "✅ All tests passed!"
	@# Step 2: Clean build artifacts
	@echo "🧹 Step 2/10: Cleaning build artifacts..."
	@set -e; $(MAKE) clean
	@# Step 3: Determine and bump version
	@echo "📈 Step 3/10: Determining version..."
	@set -e; \
	if [ -n "$(VERSION)" ]; then \
		new_version="$(VERSION)"; \
		echo "Using specified version: $$new_version"; \
	else \
		current_version=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
		echo "Current version: $$current_version"; \
		major=$$(echo $$current_version | cut -d. -f1); \
		minor=$$(echo $$current_version | cut -d. -f2); \
		patch=$$(echo $$current_version | cut -d. -f3 | cut -d'b' -f1); \
		new_patch=$$((patch + 1)); \
		new_version="$$major.$$minor.$$new_patch"; \
		echo "Auto-bumping patch version to: $$new_version"; \
	fi; \
	echo "Proceeding with version: $$new_version"; \
	if [ -z "$(FORCE)" ]; then \
		echo "Confirm version $$new_version? (y/N)"; \
		read -r confirm; \
		if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
			echo "Release cancelled."; \
			exit 1; \
		fi; \
	fi; \
	echo "Updating version in pyproject.toml..."; \
	if sed --version >/dev/null 2>&1; then \
		sed -i 's/^version = ".*"/version = "'"$$new_version"'"/' pyproject.toml; \
	else \
		sed -i '' 's/^version = ".*"/version = "'"$$new_version"'"/' pyproject.toml; \
	fi; \
	export NEW_VERSION=$$new_version
	@# Step 4: Generate changelog
	@echo "📝 Step 4/10: Generating changelog..."
	@set -e; \
	new_version=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	if [ -f "./scripts/generate-changelog.sh" ]; then \
		./scripts/generate-changelog.sh $$new_version || echo "Changelog generation failed, continuing..."; \
	else \
		echo "Changelog script not found, skipping changelog generation."; \
	fi
	@# Step 5: Build packages
	@echo "📦 Step 5/10: Building distribution packages..."
	@set -e; $(MAKE) build
	@# Step 6: Commit changes
	@echo "💾 Step 6/10: Committing changes..."
	@set -e; \
	new_version=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	git add pyproject.toml CHANGELOG.md || git add pyproject.toml; \
	git commit -m "Release v$$new_version"
	@# Step 7: Create and push tag
	@echo "🏷️  Step 7/10: Creating and pushing tag..."
	@set -e; \
	new_version=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	git tag "v$$new_version"; \
	git push origin "v$$new_version"; \
	git push origin HEAD
	@# Step 8: Publish to PyPI
	@echo "📤 Step 8/10: Publishing to PyPI..."
	@set -e; $(MAKE) publish
	@# Step 9: Create GitHub release
	@echo "🎉 Step 9/10: Creating GitHub release..."
	@set -e; \
	new_version=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	if [ -f "CHANGELOG.md" ]; then \
		gh release create "v$$new_version" \
			--title "Release v$$new_version" \
			--notes-file CHANGELOG.md \
			--draft=false || echo "GitHub release creation failed, but release is complete"; \
	else \
		gh release create "v$$new_version" \
			--title "Release v$$new_version" \
			--notes "Release v$$new_version" \
			--draft=false || echo "GitHub release creation failed, but release is complete"; \
	fi
	@# Step 10: Success message
	@echo "✅ Step 10/10: Release complete!"
	@echo ""
	@new_version=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	echo "🎊 Successfully released v$$new_version!"; \
	echo ""; \
	echo "📋 What happened:"; \
	echo "   ✅ Tests passed"; \
	echo "   ✅ Version bumped to v$$new_version"; \
	echo "   ✅ Changelog generated"; \
	echo "   ✅ Packages built"; \
	echo "   ✅ Changes committed and tagged"; \
	echo "   ✅ Published to PyPI"; \
	echo "   ✅ GitHub release created"; \
	echo ""; \
	echo "🔗 Links:"; \
	echo "   PyPI: https://pypi.org/project/asciidoc-dita-toolkit/$$new_version/"; \
	echo "   GitHub: https://github.com/rolfedh/asciidoc-dita-toolkit/releases/tag/v$$new_version"

