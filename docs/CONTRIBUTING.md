# Contributing to AsciiDoc DITA Toolkit

Thank you for your interest in contributing! This guide is for developers and maintainers.

## Project Structure

For the complete package structure, see [asciidoc-dita-toolkit.md](asciidoc-dita-toolkit.md).

**Key directories for developers:**

- **`asciidoc_dita_toolkit/asciidoc_dita/`**: Main source code
- **`tests/`**: Automated tests and test fixtures  
- **`docs/`**: Project documentation
- **`requirements-dev.txt`**: Development dependencies
- **`Makefile`**: Development automation commands
- **`Dockerfile`**: Development container configuration
- **`Dockerfile.production`**: Production container configuration
- **`scripts/container.sh`**: Container management script

## Getting Started

1. **Fork and clone the repository**

   ```sh
   git clone https://github.com/<your-org>/asciidoc-dita-toolkit.git
   cd asciidoc-dita-toolkit
   ```

2. **(Recommended) Set up a virtual environment**

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   python3 -m pip install -r requirements.txt
   ```

3. **Install your local code in editable mode for development. This way, changes you make to the code are immediately reflected without reinstalling.**

   ```sh
   python3 -m pip install -e .
   ```

4. **(If needed) Install development dependencies**

   ```sh
   python3 -m pip install -r requirements-dev.txt
   ```

## Development Commands

The project includes a comprehensive Makefile for common development tasks:

### Testing

```sh
# Run all tests
make test

# Run tests with coverage reporting
make test-coverage
```

### Code Quality

```sh
# Check code formatting and style
make lint

# Auto-format code with black
make format

# Check if code is properly formatted (without changing)
make format-check

# Run comprehensive quality checks
make check
```

### Building

Manual building is rarely needed since the `make release` command handles building automatically:

```sh
# Clean and build (if needed manually)
make clean && make build
```

### Container Development

For containerized development and testing:

```sh
# Development workflow
make container-build      # Build development container
make container-test       # Run tests in container
make container-shell      # Interactive debugging

# Production (maintainers only)
make container-build-prod # Build optimized container
make container-push-prod  # Publish to registries
```

Multi-platform containers (linux/amd64, linux/arm64) with automated CI/CD. See `docs/CONTAINER_DISTRIBUTION.md` for details.

### Installation

```sh
# Install package in development mode
make install

# Install with all development dependencies
make install-dev
```

Run `make help` to see all available commands.

## Workflow Overview

Standard GitHub workflow with branch protection on `main`:

- **Pull requests required** - All changes go through PRs
- **CI must pass** - Tests and quality checks must succeed  
- **Linear history** - Uses rebase/squash merges

**Standard workflow:** Fork → Branch → Develop → Test → PR → Review → Merge

## Adding Plugins

- Add new plugins to `asciidoc_dita_toolkit/plugins/` (e.g., `MyPlugin.py`)
- Each plugin must have a `register_subcommand` function and `__description__`
- Follow structure and conventions used in `EntityReference.py`
- Plugins are automatically discovered as CLI subcommands

## Testing Guide

### Test Structure

Our comprehensive test suite ensures code quality and functionality:

- **`tests/test_cli.py`**: CLI interface and plugin discovery tests (13 tests)
- **`tests/test_EntityReference.py`**: Plugin-specific functionality tests (7 tests)
- **`tests/asciidoc_testkit.py`**: Shared testing utilities and fixture discovery
- **`tests/fixtures/`**: Test input files (`.adoc`) and expected outputs (`.expected`) organized by plugin name

### Running Tests

**Run all tests (recommended):**

```sh
python3 -m unittest discover -s tests -v
```

**Run specific test modules:**

```sh
python3 -m unittest tests.test_cli -v
python3 -m unittest tests.test_EntityReference -v
```

**Run individual test cases:**

```sh
python3 -m unittest tests.test_cli.TestCLI.test_discover_plugins -v
```

### Test Coverage

Our test suite covers:

- ✅ CLI argument parsing and validation
- ✅ Plugin discovery and loading
- ✅ Error handling for broken plugins
- ✅ Help message functionality
- ✅ Entity replacement and content type detection
- ✅ File processing with proper mocking
- ✅ Graceful handling of missing test fixtures

## Test Files and Manual Testing

For manual testing and development of plugins (especially the ContentType plugin), the project includes a comprehensive test files directory with backup and restore functionality.

### Test Files Directory

The `test_files/` directory contains carefully crafted AsciiDoc files that cover all plugin scenarios:

- Files with correct content type attributes
- Files with empty or missing content type attributes  
- Files with deprecated content type formats
- Files with detectable filename prefixes (`assembly_`, `proc_`, `con_`, `ref_`, `snip_`)
- Files requiring interactive user prompts
- Edge cases like commented-out attributes

**Complete documentation**: See [`test_files/README.md`](../test_files/README.md) for detailed descriptions of each test file and expected plugin behaviors.

### Backup and Restore System

Since manual testing modifies test files, a backup system ensures you can always return to a clean state:

**Key components:**
- `test_files_backup/` - Clean backup of all test files
- `restore_test_files.sh` - One-command script to restore clean state
- `test_files/README.md` - Complete reference guide

**Usage workflow:**
```sh
# 1. Run manual tests (files get modified by plugins)
adt ContentType test_files/

# 2. Restore clean state with one command  
./restore_test_files.sh

# 3. Ready for next test run
```

**Benefits:**
- ✅ No need to manually reset 14+ test files after each test
- ✅ Guaranteed pristine state for consistent testing
- ✅ Complete documentation of expected plugin behaviors
- ✅ Efficient development and debugging workflow

This system is especially valuable when developing or debugging the ContentType plugin, which modifies file content based on various detection and conversion rules.

### Writing New Tests

**For CLI changes:**

- Add tests to `tests/test_cli.py`
- Use proper mocking to avoid side effects
- Test both success and error cases

**For plugin changes:**

- Create/update `tests/test_<PluginName>.py`
- Add fixtures to `tests/fixtures/<PluginName>/`:
  - `.adoc` files for test input
  - `.expected` files for expected output (in same directory)
- Test core functionality and edge cases

**Testing Best Practices:**

- Use `unittest.mock.patch` for external dependencies
- Create temporary files for file processing tests
- Test both valid inputs and error conditions
- Use descriptive test method names and docstrings
- Use context managers (`with patch()`) for complex mocking

### Continuous Integration

All PRs must pass the test suite:

- Tests run automatically on GitHub Actions
- 20/20 tests must pass for PR approval
- Missing test fixtures show warnings but don't fail tests

## Fixture Management

> **Note:** Fixture updates are automated via GitHub Actions. The local `fetch-fixtures.sh` script is archived and no longer required for routine use.

For manual fixture updates (rarely needed):

```sh
./archive/fetch-fixtures.sh
```

- **Recommended:** Use the automated workflow, which runs daily and creates PRs if fixtures change
- Downloads latest `.adoc` test files from `asciidoctor-dita-vale`
- Preserves existing `.expected` files during updates

## CI Integration

- `.github/workflows/ci.yml` runs all tests and downloads fixtures if needed
- All pull requests must pass CI before merging

## Review and Merge

- Open a pull request for your changes
- Request review from maintainers  
- Address feedback, ensure CI passes, and merge when approved

## Publishing a New Release to PyPI

> **Note:** Only project maintainers can publish new releases to PyPI. Contributors with forks can help with development but cannot create official releases.

### Automated Release Process (Recommended)

The project now includes a fully automated release workflow via the `make release` command:

**Prerequisites:**
- GitHub CLI (`gh`) installed and authenticated
- `GITHUB_TOKEN` environment variable set
- `PYPI_API_TOKEN` environment variable set
- Clean working directory on main/master branch

**Usage:**

```sh
# Automated patch version bump (e.g., 0.1.9b2 → 0.2.0)
make release

# Specify a custom version
make release VERSION=1.2.3

# Force without confirmations (for CI/CD)
make release FORCE=1 VERSION=1.2.3
```

**What the automated process does:**

1. **🧪 Runs all tests** - Executes comprehensive quality checks (format, lint, test)
2. **🧹 Cleans** - Removes old build artifacts
3. **📈 Bumps version** - Auto-increments patch or uses specified version
4. **📝 Generates changelog** - Creates changelog entry if script exists
5. **📦 Builds** - Creates distribution packages
6. **💾 Commits** - Commits version and changelog changes
7. **🏷️ Tags & Pushes** - Creates version tag and pushes to remote
8. **📤 Publishes** - Uploads to PyPI
9. **🎉 GitHub Release** - Creates GitHub release with changelog
10. **✅ Success** - Shows summary with PyPI and GitHub links

**The entire process is atomic** - if any step fails, the release stops to prevent partial releases.

### Manual Release Process (Legacy)

For reference, the legacy manual process is documented in `archive/CONTRIBUTING_legacy.md`. The automated process above is now the recommended approach.

## Toolkit Components Overview

- **`asciidoc_toolkit.py`**: CLI entry point, discovers and runs plugins
- **`plugins/`**: Individual plugin scripts for transformations/validations
- **`file_utils.py`**: Shared file/argument utilities
- **`tests/`**: Automated tests and fixtures
- **`requirements.txt`**: Python dependencies for development
- **`README.md`**: End-user setup, usage, and project overview

## Why contribute?

- Modern Python and robust testing practices
- Improve publishing workflows for AsciiDoc and DITA
- Active review and maintenance

## Pre-commit Hooks for Code Quality

This project uses [pre-commit](https://pre-commit.com/) to automate code formatting, linting, and basic checks before every commit.

### Setup Instructions

1. **Install pre-commit (one-time setup):**

   ```sh
   python3 -m pip install pre-commit
   ```

2. **Install the hooks into your local Git config (one-time per clone):**

   ```sh
   pre-commit install
   ```

3. **(Optional) Run all hooks on all files:**

   ```sh
   pre-commit run --all-files
   ```

### What gets checked automatically?

- **Black**: Formats Python code to a consistent style
- **isort**: Sorts and organizes Python imports
- **Ruff**: Fast Python linter for code quality and style
- **markdownlint**: Lints and enforces style in Markdown files
- **Basic checks**: Trailing whitespace, end-of-file fixing, YAML/TOML syntax validation
- **Safety checks**: Large file prevention, merge conflict detection, debug statement detection

If any check fails, the commit will be blocked until the issue is fixed. Black and isort will auto-format your code; just re-stage the changes and commit again.

See `.pre-commit-config.yaml` for details.

## Changelog Management

The project uses automated changelog generation as part of the `make release` process. Changelog entries are generated from commit messages and GitHub release information.

**Manual changelog generation** (for development/testing):

```sh
# Generate changelog entry for latest version
make changelog

# Generate changelog for specific version
make changelog-version VERSION=1.2.3
```

For more advanced changelog management, see the legacy documentation in `archive/CONTRIBUTING_legacy.md`.
