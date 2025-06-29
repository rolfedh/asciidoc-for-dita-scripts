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

### Building and Publishing

```sh
# Build distribution packages
make build

# Publish to PyPI (requires PYPI_API_TOKEN)
make publish

# Clean build artifacts
make clean
```

### Installation

```sh
# Install package in development mode
make install

# Install with all development dependencies
make install-dev
```

Run `make help` to see all available commands.

## Branch Protection Rules

We've enabled branch protections on the `main` branch to help maintain a clean and stable codebase:

- **Pull requests are now required**: All changes must come through a PR—no direct commits to `main`.
- **PRs do not require approval**: No reviews are required before merging. However, there should be no outstanding change requests.
- **Status checks must pass**: Any required checks (like CI tests) must succeed before a PR can be merged.
- **Linear history enforced**: We'll be using rebase or squash merges to avoid merge commits in `main`.
- **No bypassing**: These rules apply to everyone, including admins.

If you have any questions or run into issues with these protections, please reach out to the maintainers.

## Adding Plugins

- Add new plugins to `asciidoc_dita_toolkit/plugins/` (e.g., `MyPlugin.py`).
- Each plugin must have a `register_subcommand` function and a clear `__description__`.
- Follow the structure and docstring conventions used in `EntityReference.py`.
- Plugins are automatically discovered as CLI subcommands.

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
- Expected files (`.expected`) are stored alongside input files (`.adoc`) in fixture directories

## Fixture Management

The `fetch-fixtures.sh` script downloads test fixtures from the upstream repository while preserving any locally created `.expected` files:

```sh
./fetch-fixtures.sh
```

- Downloads latest `.adoc` test files from `asciidoctor-dita-vale`
- Preserves existing `.expected` files during updates
- Creates backup and restore process for safety

## CI Integration

- Ensure `.github/workflows/ci.yml` runs all tests and downloads fixtures if needed.
- All pull requests must pass CI before merging.

## Review and Merge

- Open a pull request for your changes.
- Request review from maintainers.
- Address feedback, ensure CI passes, and merge when approved.

## Publishing a New Release to PyPI

To have the GitHub Actions workflow build and upload the package to PyPI using the `PYPI_API_TOKEN` secret:

1. **Update the version** in `pyproject.toml`.
2. **Commit and push** your changes:

   ```sh
   git add pyproject.toml
   git commit -m "Bump version to <new-version>"
   git push
   ```

3. **Tag the release and push the tag:**

   ```sh
   git tag v<new-version>  # Example: v0.1.3
   git push origin v<new-version>
   ```

4. GitHub Actions will build and upload the package to PyPI automatically.

## Troubleshooting if the tagging gets ahead of the version

   ```sh
   git tag -d v0.1.3
   git tag v0.1.3
   git push --force origin v0.1.3
   ```

**Manual publishing (alternative):**

1. Build the package:

   ```sh
   python3 -m pip install --upgrade build twine
   python3 -m build
   ```

2. Upload to PyPI:

   ```sh
   python3 -m twine upload dist/*
   ```

See the main README for more details.

## Toolkit Components Overview

- **`asciidoc_toolkit.py`**: CLI entry point, discovers and runs plugins.
- **`plugins/`**: Individual plugin scripts for transformations/validations.
- **`file_utils.py`**: Shared file/argument utilities.
- **`tests/`**: Automated tests and fixtures.
- **`requirements.txt`**: Python dependencies for development.
- **`README.md`**: End-user setup, usage, and project overview.

## Why contribute?

- Modern Python and robust testing practices
- Improve publishing workflows for AsciiDoc and DITA
- Active review and maintenance

## Pre-commit Hooks for Code Quality

This project uses [pre-commit](https://pre-commit.com/) to automate code formatting, linting, and basic checks before every commit. This ensures code quality and consistency across all contributors.

### Setup Instructions

1. **Install pre-commit (one-time setup):**

   ```sh
   python3 -m pip install pre-commit
   ```

2. **Install the hooks into your local Git config (one-time per clone):**

   ```sh
   pre-commit install
   ```

   This will automatically run the configured checks every time you commit.

3. **(Optional) Run all hooks on all files:**

   ```sh
   pre-commit run --all-files
   ```

### What gets checked automatically?

- **Black**: Formats Python code to a consistent style ([psf/black](https://github.com/psf/black))
- **isort**: Sorts and organizes Python imports ([PyCQA/isort](https://github.com/PyCQA/isort))
- **Ruff**: Fast Python linter for code quality and style ([charliermarsh/ruff](https://github.com/charliermarsh/ruff))
- **markdownlint**: Lints and enforces style in Markdown files ([igorshubovych/markdownlint-cli](https://github.com/igorshubovych/markdownlint-cli))
- **Trailing whitespace**: Removes trailing whitespace from all files
- **End-of-file fixer**: Ensures files end with a single newline
- **YAML syntax check**: Validates YAML file syntax
- **TOML syntax check**: Validates TOML file syntax
- **Large file check**: Prevents accidentally committing large files
- **Merge conflict check**: Prevents committing unresolved merge conflict markers
- **Debug statement check**: Prevents committing Python debug statements (e.g., `pdb.set_trace()`)
- **Docstring placement check**: Ensures Python docstrings are placed before code

If any check fails, the commit will be blocked until the issue is fixed. Black and isort will auto-format your code; just re-stage the changes and commit again.

See `.pre-commit-config.yaml` for details.
