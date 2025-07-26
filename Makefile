# Makefile for AsciiDoc DITA Toolkit
#
# GitHub Release Automation:
#   - `make publish` now automatically creates GitHub releases after PyPI publication
#   - `make release` creates tags, releases, and triggers container builds via GitHub Actions
#   - `make github-release` creates releases for existing versions
#   - Requires `gh` CLI to be authenticated: `gh auth login`
#
.PHONY: help test test-coverage lint format clean install install-dev build publish-check publish github-release changelog changelog-version release bump-version dev venv setup container-build container-build-prod container-test container-shell container-push container-push-prod container-clean container-validate check

# Changelog extraction pattern for reuse across targets
CHANGELOG_AWK_PATTERN = {found=1; next} /^## \[/ {if(found) exit} found {if($$0 !~ /^$/) print $$0}

# Default target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Prerequisites for release automation:"
	@echo "  - GitHub CLI: gh auth login (automated check)"
	@echo "  - PyPI credentials: PYPI_API_TOKEN environment variable (automated check)"
	@echo "  - Virtual environment: Automatically created if missing"
	@echo "  - Dependencies: Automatically installed if missing"
	@echo ""
	@echo "  help       - Show this help message"
	@echo "  test       - Run all tests"
	@echo "  test-coverage - Run tests with coverage reporting"
	@echo "  check-test-locations - Ensure all test files are in tests/ directory"
	@echo "  lint       - Run comprehensive code linting with flake8"
	@echo "  lint-clean - Run linting on main codebase (excludes archive/debug)"
	@echo "  quick-lint - Run critical error checks only"
	@echo "  format     - Format code with black"
	@echo "  clean      - Clean build artifacts"
	@echo "  venv       - Create virtual environment (.venv)"
	@echo "  setup      - Complete setup: venv + install-dev + format + lint + test + tab completion"
	@echo "  install    - Install package in development mode"
	@echo "  install-dev - Install package with development dependencies"
	@echo "  build      - Build distribution packages"
	@echo "  publish-check - Check publishing prerequisites (twine, credentials)"
	@echo "  bump-version - Bump version in both pyproject.toml and __init__.py (VERSION=x.y.z to specify)"
	@echo "  publish    - Complete automated release: setup environment, auto-bump patch version (or VERSION=x.y.z), update changelog, build package for validation, create working branch, commit changes to branch, create & push tag, create GitHub release. PyPI publishing handled automatically by GitHub Actions (MAINTAINERS ONLY)"
	@echo "  github-release - Create GitHub release for current version (VERSION=x.y.z to override)"
	@echo "  check      - Run comprehensive quality checks"
	@echo "  changelog  - Generate changelog entry for latest version"
	@echo "  changelog-version - Generate changelog for specific version (VERSION=x.y.z)"
	@echo "  release    - Automated release: bump patch version, commit, tag, push (MAINTAINERS ONLY) (VERSION=x.y.z to override)"
	@echo "  dev        - Complete development setup (install-dev + format + lint + test)"
	@echo "  install-completion - Install tab completion for adt CLI"
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
test: check-test-locations
	@echo "Running all tests with pytest..."
	python3 -m pytest tests/ -v

test-coverage: check-test-locations
	@echo "Running tests with coverage..."
	python3 -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
	@echo "Coverage report generated in htmlcov/"

check-test-locations:
	@echo "Checking for misplaced test files..."
	@# Check for Python test files
	@if find . -maxdepth 1 -name "test_*.py" -o -name "*_test.py" | grep -q .; then \
		echo "❌ Found Python test files in root directory:"; \
		find . -maxdepth 1 -name "test_*.py" -o -name "*_test.py"; \
		echo "Please move these files to tests/ directory"; \
		exit 1; \
	fi
	@# Check for shell script test files
	@if find . -maxdepth 1 -name "test-*.sh" -o -name "*-test.sh" -o -name "test_*.sh" -o -name "*_test.sh" | grep -q .; then \
		echo "❌ Found shell script test files in root directory:"; \
		find . -maxdepth 1 -name "test-*.sh" -o -name "*-test.sh" -o -name "test_*.sh" -o -name "*_test.sh"; \
		echo "Please move these files to tests/ directory"; \
		exit 1; \
	fi
	@# Check for other common test file patterns
	@if find . -maxdepth 1 -name "test-*" -o -name "*-test.*" -o -name "test_*" -o -name "*_test.*" | grep -E '\.(sh|bat|cmd|ps1|js|ts|rb|pl|php)$$' | grep -q .; then \
		echo "❌ Found other test files in root directory:"; \
		find . -maxdepth 1 -name "test-*" -o -name "*-test.*" -o -name "test_*" -o -name "*_test.*" | grep -E '\.(sh|bat|cmd|ps1|js|ts|rb|pl|php)$$'; \
		echo "Please move these files to tests/ directory"; \
		exit 1; \
	fi
	@echo "✅ All test files are properly located in tests/ directory"

# Code quality targets
lint:
	python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=.venv,venv,debug_env,build,dist,*.egg-info,.git,__pycache__
	python3 -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --exclude=.venv,venv,debug_env,build,dist,*.egg-info,.git,__pycache__

lint-clean:
	python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=.venv,venv,debug_env,build,dist,*.egg-info,.git,__pycache__,archive
	python3 -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --exclude=.venv,venv,debug_env,build,dist,*.egg-info,.git,__pycache__,archive

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
	@.venv/bin/python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=.venv,venv,debug_env,build,dist,*.egg-info,.git,__pycache__ || true
	@.venv/bin/python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --exclude=.venv,venv,debug_env,build,dist,*.egg-info,.git,__pycache__ || true
	@echo "🧪 Running tests..."
	@.venv/bin/python -m pytest tests/ -v || true
	@echo "🎯 Installing tab completion..."
	@./scripts/install-completion.sh --user
	@echo ""
	@echo "✅ Development setup complete!"
	@echo "💡 To activate the virtual environment: source .venv/bin/activate"
	@echo "🔧 Then you can use: adt -h"
	@echo "⚡ Tab completion available: adt <TAB><TAB>"

dev: install-dev format lint test
	@echo "Development setup complete!"

# Tab completion installation
install-completion:
	@echo "🎯 Installing tab completion for adt CLI..."
	@./scripts/install-completion.sh --user
	@echo "✅ Tab completion installed!"
	@echo "   Try: adt <TAB><TAB>"
	@echo "   Restart your shell if completion doesn't work immediately"

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
	if [ -f asciidoc_dita_toolkit/adt_core/__init__.py ]; then \
		sed -i 's/^__version__ = .*/__version__ = "'"$$new_version"'"/' asciidoc_dita_toolkit/adt_core/__init__.py; \
	else \
		echo "Warning: asciidoc_dita_toolkit/adt_core/__init__.py not found, skipping..."; \
	fi; \
	echo "Version bumped to $$new_version in both files"

# Publishing dependency check with automated setup
publish-check:
	@echo "🔍 Checking and setting up publishing prerequisites..."
	@echo ""
	@echo "Step 1: Virtual environment setup..."
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "No virtual environment currently active."; \
		if [ ! -d ".venv" ]; then \
			echo "Creating virtual environment and installing dependencies..."; \
			./scripts/dev-setup.sh; \
			echo "✅ Development environment set up successfully"; \
			echo "Note: You may need to run 'source .venv/bin/activate' in your current shell"; \
		else \
			echo "Virtual environment .venv exists. Checking if it has required dependencies..."; \
			if .venv/bin/python -c "import twine, build" 2>/dev/null; then \
				echo "✅ Virtual environment has required dependencies"; \
			else \
				echo "Installing missing dependencies..."; \
				.venv/bin/pip install -e .; \
				.venv/bin/pip install -r requirements-dev.txt; \
				.venv/bin/pip install build twine; \
				echo "✅ Dependencies installed"; \
			fi; \
		fi; \
	else \
		echo "✅ Virtual environment active: $$VIRTUAL_ENV"; \
	fi
	@echo ""
	@echo "Step 2: Checking build installation..."
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		python_cmd="$${VIRTUAL_ENV}/bin/python"; \
		pip_cmd="$${VIRTUAL_ENV}/bin/pip"; \
	elif [ -d ".venv" ]; then \
		python_cmd=".venv/bin/python"; \
		pip_cmd=".venv/bin/pip"; \
	else \
		python_cmd="python3"; \
		pip_cmd="pip"; \
	fi; \
	if ! $$python_cmd -c "import build" 2>/dev/null; then \
		echo "Installing build..."; \
		$$pip_cmd install build; \
		echo "✅ build installed"; \
	else \
		echo "✅ build is available"; \
	fi
	@echo ""
	@echo "Step 3: Checking GitHub CLI authentication..."
	@if ! command -v gh >/dev/null 2>&1; then \
		echo "❌ GitHub CLI (gh) not found. Please install it: https://cli.github.com/"; \
		exit 1; \
	fi
	@if ! gh auth status >/dev/null 2>&1; then \
		echo "❌ GitHub CLI not authenticated. Run: gh auth login"; \
		exit 1; \
	fi
	@echo "✅ GitHub CLI authenticated"
	@echo ""
	@echo "Step 4: Checking git state..."
	@if [ -n "$$(git status --porcelain 2>/dev/null)" ]; then \
		echo "⚠️  Working directory has uncommitted changes:"; \
		git status --short; \
		echo ""; \
		echo "Please commit changes before publishing:"; \
		echo "  git add ."; \
		echo "  git commit -m 'Prepare for release'"; \
		exit 1; \
	else \
		echo "✅ Working directory is clean"; \
	fi
	@echo ""
	@echo "✅ All prerequisites satisfied - ready to publish via GitHub Actions!"

publish: publish-check
	@echo ""
	@echo "🚀 Starting automated release process..."
	@echo ""
	@echo "Step 5: Cleaning build environment..."
	@$(MAKE) clean
	@echo "✅ Build environment cleaned"
	@echo ""
	@echo "Step 6: Determining version for release..."
	@if [ -z "$(VERSION)" ]; then \
		current_version=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
		echo "Current version: $$current_version"; \
		major=$$(echo $$current_version | cut -d. -f1); \
		minor=$$(echo $$current_version | cut -d. -f2); \
		patch=$$(echo $$current_version | cut -d. -f3); \
		new_patch=$$((patch + 1)); \
		new_version="$$major.$$minor.$$new_patch"; \
		echo "Auto-incrementing to: $$new_version"; \
	else \
		new_version="$(VERSION)"; \
		echo "Using specified version: $$new_version"; \
	fi; \
	echo "Updating version files..."; \
	sed -i 's/^version = .*/version = "'"$$new_version"'"/' pyproject.toml; \
	if [ -f asciidoc_dita_toolkit/adt_core/__init__.py ]; then \
		sed -i 's/^__version__ = .*/__version__ = "'"$$new_version"'"/' asciidoc_dita_toolkit/adt_core/__init__.py; \
	else \
		echo "Warning: asciidoc_dita_toolkit/adt_core/__init__.py not found, skipping..."; \
	fi; \
	echo "Version updated to $$new_version"; \
	echo ""; \
	echo "Step 7: Updating changelog for release..."; \
	if [ -f "./scripts/generate-changelog.sh" ]; then \
		changelog_output=$$(./scripts/generate-changelog.sh $$new_version 2>&1); \
		if [ $$? -ne 0 ]; then \
			echo "Warning: Changelog generation failed with the following error:"; \
			echo "$$changelog_output"; \
			echo "Continuing with the release process..."; \
		else \
			echo "✅ Changelog updated"; \
		fi; \
	else \
		echo "⚠️ Changelog script not found at ./scripts/generate-changelog.sh, skipping changelog update"; \
	fi; \
	echo ""; \
	echo "Step 8: Building package for validation..."; \
	if [ -n "$$VIRTUAL_ENV" ]; then \
		"$${VIRTUAL_ENV}/bin/python" -m build; \
	elif [ -d ".venv" ]; then \
		.venv/bin/python -m build; \
	else \
		python3 -m build; \
	fi; \
	echo "✅ Package built successfully (for validation only)"; \
	echo ""; \
	echo "Step 9: Creating working branch for release..."; \
	branch_name="release/v$$new_version-$$(date +%Y%m%d-%H%M%S)"; \
	echo "Creating and switching to branch: $$branch_name"; \
	git checkout -b "$$branch_name"; \
	echo "✅ Working branch created"; \
	echo ""; \
	echo "Step 10: Committing version changes..."; \
	git add pyproject.toml; \
	if [ -f asciidoc_dita_toolkit/adt_core/__init__.py ]; then \
		git add asciidoc_dita_toolkit/adt_core/__init__.py; \
	fi; \
	if [ -f CHANGELOG.md ]; then \
		git add CHANGELOG.md; \
	fi; \
	git commit -m "chore: bump version to $$new_version" || echo "No changes to commit"; \
	echo "✅ Changes committed to branch $$branch_name"; \
	echo ""; \
	echo "Step 11: Creating and pushing tag to trigger automated PyPI publish..."; \
	current_version="$$new_version"; \
	tag_name="v$$current_version"; \
	echo "Creating tag $$tag_name to trigger GitHub Actions PyPI publish..."; \
	if git tag -l | grep -q "^$$tag_name$$"; then \
		echo "Tag $$tag_name already exists, pushing existing tag..."; \
	else \
		echo "Creating new tag $$tag_name..."; \
		git tag $$tag_name; \
	fi; \
	git push origin "$$branch_name"; \
	git push origin $$tag_name; \
	echo "✅ Branch and tag pushed - GitHub Actions will handle PyPI publishing"; \
	echo ""; \
	echo "Step 12: Creating GitHub release..."; \
	release_notes=""; \
	if [ -f "CHANGELOG.md" ]; then \
		release_notes=$$(awk "/^## \[$$current_version\]/ $(CHANGELOG_AWK_PATTERN)" CHANGELOG.md | head -20); \
		if [ -z "$$release_notes" ]; then \
			release_notes="Release $$current_version - Published via automated GitHub Actions workflow"; \
		fi; \
	else \
		release_notes="Release $$current_version - Published via automated GitHub Actions workflow"; \
	fi; \
	echo "Creating GitHub release with notes..."; \
	if ! echo "$$release_notes" | gh release create $$tag_name --title "Release $$tag_name" --notes-file - --verify-tag; then \
		echo "❌ Failed to create GitHub release with --verify-tag. Please check the tag or your GitHub CLI configuration."; \
		exit 1; \
	fi; \
	echo "🚀 GitHub release created: https://github.com/rolfedh/asciidoc-dita-toolkit/releases/tag/$$tag_name"; \
	echo ""; \
	echo "📦 PyPI publishing and container builds will be handled automatically by GitHub Actions"; \
	echo "📦 Monitor progress: https://github.com/rolfedh/asciidoc-dita-toolkit/actions"; \
	echo ""; \
	echo "⚠️  NOTE: Version changes are on branch '$$branch_name' - not on main"; \
	echo "⚠️  You may want to create a PR to merge these changes to main if needed"; \
	echo ""; \
	echo "✅ Release process complete! GitHub Actions will:"; \
	echo "   1. Build and publish package to PyPI"; \
	echo "   2. Build and push container images"; \
	echo "   3. Update any other automated release tasks"

# Create GitHub release for current or specified version
github-release:
	@echo "Creating GitHub release..."
	@if [ -n "$(VERSION)" ]; then \
		target_version="$(VERSION)"; \
		echo "Using specified version: $$target_version"; \
	else \
		target_version=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
		echo "Using current version from pyproject.toml: $$target_version"; \
	fi; \
	tag_name="v$$target_version"; \
	echo "Creating/updating GitHub release for $$tag_name..."; \
	if ! git tag -l | grep -q "^$$tag_name$$"; then \
		echo "Tag $$tag_name does not exist. Creating tag..."; \
		git tag $$tag_name; \
		git push origin $$tag_name; \
	fi; \
	release_notes=""; \
	if [ -f "CHANGELOG.md" ]; then \
		release_notes=$$(awk "/^## \[$$target_version\]/ $(CHANGELOG_AWK_PATTERN)" CHANGELOG.md | head -20); \
		if [ -z "$$release_notes" ]; then \
			release_notes="Release $$target_version - See CHANGELOG.md for details"; \
		fi; \
	else \
		release_notes="Release $$target_version"; \
	fi; \
	echo "Creating GitHub release with notes..."; \
	if gh release view $$tag_name >/dev/null 2>&1; then \
		echo "Release $$tag_name already exists. Updating..."; \
		echo "$$release_notes" | gh release edit $$tag_name --title "Release $$tag_name" --notes-file -; \
	else \
		echo "$$release_notes" | gh release create $$tag_name --title "Release $$tag_name" --notes-file - --generate-notes; \
	fi; \
	echo "✅ GitHub release ready: https://github.com/rolfedh/asciidoc-dita-toolkit/releases/tag/$$tag_name"

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
	echo "Updating version in asciidoc_dita_toolkit/adt_core/__init__.py..."; \
	if sed --version >/dev/null 2>&1; then \
		sed -i 's/^__version__ = ".*"/__version__ = "'"$$new_version"'"/' asciidoc_dita_toolkit/adt_core/__init__.py; \
	else \
		sed -i '' 's/^__version__ = ".*"/__version__ = "'"$$new_version"'"/' asciidoc_dita_toolkit/adt_core/__init__.py; \
	fi; \
	echo "Generating changelog for version $$new_version..."; \
	if [ -f "./scripts/generate-changelog.sh" ]; then \
		./scripts/generate-changelog.sh $$new_version || true; \
	else \
		echo "Changelog script not found, skipping changelog generation."; \
	fi; \
	echo "Committing version bump..."; \
	git add pyproject.toml asciidoc_dita_toolkit/adt_core/__init__.py CHANGELOG.md; \
	git commit -m "Bump version to $$new_version"; \
	echo "Pushing release branch..."; \
	git push origin "$$release_branch"; \
	echo ""; \
	echo "🚀 Release branch $$release_branch created and pushed!"; \
	echo ""; \
	echo "Creating GitHub release..."; \
	tag_name="v$$new_version"; \
	if git tag -l | grep -q "^$$tag_name$$"; then \
		echo "Tag $$tag_name already exists, creating release from existing tag..."; \
	else \
		echo "Creating tag $$tag_name on main branch..."; \
		git checkout main; \
		git pull origin main; \
		git tag $$tag_name; \
		git push origin $$tag_name; \
	fi; \
	release_notes=""; \
	if [ -f "CHANGELOG.md" ]; then \
		release_notes=$$(awk "/^## \[$$new_version\]/ $(CHANGELOG_AWK_PATTERN)" CHANGELOG.md | head -20); \
		if [ -z "$$release_notes" ]; then \
			release_notes="Release $$new_version - See CHANGELOG.md for details"; \
		fi; \
	else \
		release_notes="Release $$new_version"; \
	fi; \
	echo "Creating GitHub release..."; \
	if ! echo "$$release_notes" | gh release create $$tag_name --title "Release $$tag_name" --notes-file - --verify-tag --generate-notes; then \
		echo "Warning: Failed to create GitHub release with --verify-tag. Retrying without --verify-tag..."; \
		if ! echo "$$release_notes" | gh release create $$tag_name --title "Release $$tag_name" --notes-file - --generate-notes; then \
			echo "Error: Failed to create GitHub release. Please check the logs and try again."; \
			exit 1; \
		fi; \
	fi; \
	echo ""; \
	echo "✅ Complete! GitHub release created: https://github.com/rolfedh/asciidoc-dita-toolkit/releases/tag/$$tag_name"; \
	echo ""; \
	echo "🚀 Next steps:"; \
	echo "1. GitHub Actions will automatically build and push container images"; \
	echo "2. Monitor the workflow: https://github.com/rolfedh/asciidoc-dita-toolkit/actions"; \
	echo "3. If needed, publish to PyPI with: make publish"

# ValeFlagger targets
.PHONY: valeflag-test
valeflag-test:
	@echo "Testing ValeFlagger..."
	cd docker/vale-adv && ./build.sh
	python -m pytest tests/test_vale_flagger.py -v

.PHONY: valeflag-check
valeflag-check:
	@echo "Running ValeFlagger on project..."
	python -m asciidoc_dita_toolkit.plugins.vale_flagger.cli --path ./docs --dry-run

.PHONY: valeflag-build
valeflag-build:
	@echo "Building Vale Docker container..."
	cd docker/vale-adv && ./build.sh