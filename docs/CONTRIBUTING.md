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

## Beta Testing Files

The project includes comprehensive test files and examples in `asciidoc_dita_toolkit/beta_testing_files/` that are automatically included in both PyPI packages and Docker images.

### Working with Test Files

**Access test files during development:**
```sh
# Find test files location
find-beta-files

# Or navigate directly
cd asciidoc_dita_toolkit/beta_testing_files/
```

**Test your changes:**
```sh
# Use test files to validate plugin behavior
asciidoc-dita-toolkit EntityReference -f asciidoc_dita_toolkit/beta_testing_files/EntityReference/sample.adoc

# Compare with expected output
diff asciidoc_dita_toolkit/beta_testing_files/EntityReference/sample.adoc \
     asciidoc_dita_toolkit/beta_testing_files/EntityReference/expected.adoc
```

### Contributing Test Files

When adding new plugins or improving existing ones:

1. **Add test files** to the appropriate plugin directory:
   ```
   asciidoc_dita_toolkit/beta_testing_files/
   ├── YourPlugin/
   │   ├── sample.adoc           # Input file demonstrating the issue
   │   ├── expected.adoc         # Expected output after transformation
   │   ├── complex_example.adoc  # More complex scenarios
   │   └── edge_cases.adoc       # Edge cases and unusual patterns
   ```

2. **Include both input and expected output** files to enable validation

3. **Document special scenarios** in comments within the test files

4. **Test your additions** before submitting:
   ```sh
   # Test the plugin on your new test files
   asciidoc-dita-toolkit YourPlugin -f asciidoc_dita_toolkit/beta_testing_files/YourPlugin/sample.adoc

   # Verify expected behavior
   diff asciidoc_dita_toolkit/beta_testing_files/YourPlugin/sample.adoc \
        asciidoc_dita_toolkit/beta_testing_files/YourPlugin/expected.adoc
   ```

> **📋 Detailed Guide**: For comprehensive information on using beta testing files, see [BETA_TESTING.md](BETA_TESTING.md).

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
# Clean build artifacts from previous builds (important!)
make clean

# Build distribution packages
make build

# Publish to PyPI (MAINTAINERS ONLY - requires PYPI_API_TOKEN)
make publish
```

**Important**: Always run `make clean` before building to remove any obsolete build artifacts from previous versions. This prevents packaging outdated files that could cause version conflicts.

### Container Development

The project supports containerized development and distribution with automated builds:

```sh
# Build development container (includes dev tools)
make container-build

# Build production container (optimized)
make container-build-prod

# Run tests in container
make container-test

# Start interactive container shell for debugging
make container-shell

# Validate all container configurations
make container-validate

# Push containers to registry (maintainers only)
make container-push
make container-push-prod

# Clean up local container images
make container-clean
```

**Container Features:**

- **Development image** (`rolfedh/asciidoc-dita-toolkit:latest`): Includes dev dependencies and tools
- **Production image** (`rolfedh/asciidoc-dita-toolkit-prod:latest`): Optimized multi-stage build
- **Automated CI/CD**: GitHub Actions builds and publishes containers on releases
- **Multi-platform**: Supports linux/amd64 and linux/arm64 architectures
- **Registry publishing**: Pushes to both Docker Hub and GitHub Container Registry

**Manual container usage:**

```sh
# Test your changes in a clean container environment
./scripts/container.sh build
./scripts/container.sh test
./scripts/container.sh shell
```

See `docs/CONTAINER_DISTRIBUTION.md` for complete container documentation.

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

> **Note:** Fixture updates are now automated via GitHub Actions using `.github/workflows/fetch-fixtures.yml`. The local `fetch-fixtures.sh` script is archived and no longer required for routine use.

To manually update fixtures (rarely needed), you may run the archived script:

```sh
./archive/fetch-fixtures.sh
```

- **Recommended:** Rely on the automated workflow, which runs daily and creates a pull request if fixtures change.
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

> **Note:** Only project maintainers can publish new releases to PyPI. Contributors with forks can help with development but cannot create official releases.

**Recommended Approach - Automated Release (Maintainers Only):**

Use the new `make release` command for a complete automated workflow:

```sh
# Automated patch version bump and release
make release

# Or specify a custom version
make release VERSION=0.2.0
```

This will handle version bumping, changelog generation, commits, tagging, and pushing automatically. GitHub Actions will then build and upload the package to PyPI using the `PYPI_API_TOKEN` secret.

**Manual Approach (Maintainers Only):**

To manually have the GitHub Actions workflow build and upload the package to PyPI:

1. **Ensure your main branch is up to date:**

   ```sh
   git checkout main
   git pull origin main
   ```

2. **Create a release preparation branch:**

   ```sh
   git checkout -b release/v<new-version>  # Example: release/v0.1.8
   ```

3. **Update the version** in `pyproject.toml`.

4. **Commit your changes and push the branch:**

   ```sh
   git add pyproject.toml
   git commit -m "Bump version to <new-version>"
   git push origin release/v<new-version>
   ```

5. **Create and merge a Pull Request:**
   - Open a PR from `release/v<new-version>` to `main`
   - Title: "Release v\<new-version\>"
   - Once CI passes, merge the PR (this will update main with the version bump)

6. **Create and push the release tag from main:**

   ```sh
   git checkout main
   git pull origin main
   git tag v<new-version>  # Example: v0.1.8
   git push origin v<new-version>
   ```

7. GitHub Actions will build and upload the package to PyPI automatically when the tag is pushed.

**Important:** Due to branch protection rules on `main`, all changes (including version bumps) must go through a Pull Request. The tag must be created from the merged commit on `main` to ensure the PyPI release reflects the actual state of the main branch.

## Troubleshooting if the tagging gets ahead of the version

   ```sh
   git tag -d v0.1.3
   git tag v0.1.3
   git push --force origin v0.1.3
   ```

**Manual publishing (alternative):**

1. Clean previous build artifacts:

   ```sh
   # Remove any obsolete build files that could cause version conflicts
   rm -rf dist/ build/ *.egg-info/
   ```

2. Build the package:

   ```sh
   python3 -m pip install --upgrade build twine
   python3 -m build
   ```

3. Upload to PyPI:

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

## Changelog Management

The project uses automated changelog generation based on GitHub releases and PR labels to reduce maintenance overhead while ensuring consistency.

### Setup Requirements

**GitHub Repository Labels**: Create these labels in your GitHub repository for automatic categorization:

- `enhancement` - New features and improvements
- `bug` - Bug fixes  
- `documentation` - Documentation updates
- `dependencies` - Dependency updates
- `breaking` - Breaking changes
- `internal` - Internal/maintenance changes (won't appear in changelog)

**To create labels**: Go to GitHub repo → Issues → Labels → "New label" for each one above.

### How the Automation Works

**Automatic Generation** (when you create a release):

1. Create a GitHub release (manually or via GitHub CLI)
2. The workflow automatically runs via `.github/workflows/changelog.yml`
3. It generates changelog entries from:
   - Release notes and descriptions
   - PR titles with their labels for categorization
   - Semantic version information
4. Commits the updated `CHANGELOG.md` back to main branch

**Manual Generation** (for testing/development):

```sh
# Install GitHub CLI (one-time setup)
# Ubuntu/Debian: sudo apt install gh
# macOS: brew install gh
# Authenticate: gh auth login

# Generate changelog manually
make changelog-generate
# Or run script directly
./scripts/generate-changelog.sh [version]
```

### PR Labeling Guidelines

For better changelog generation, use descriptive PR titles and apply appropriate labels:

**PR Title Format:**

```text
feat: add new plugin for XYZ conversion
fix: resolve entity replacement edge case  
docs: update installation instructions
refactor: improve CLI error handling
```

**Label Usage:**

- `enhancement`: New features, improvements, performance enhancements
- `bug`: Bug fixes, error corrections, edge case handling
- `documentation`: README updates, guide improvements, API docs
- `dependencies`: Package updates, security patches
- `breaking`: API changes, removed features, compatibility breaks
- `internal`: Refactoring, code cleanup, test improvements (excluded from changelog)

### Release Workflow

**Automated Release Process (Recommended):**

Use the new Makefile `release` target for a fully automated release:

```sh
# Automated patch version bump (0.1.8 → 0.1.9)
make release

# Specify custom version
make release VERSION=0.2.0
```

**The `make release` command will:**

1. **Validate environment**: Check you're on main/master branch with clean working directory
2. **Run quality checks**: Execute `make check` (format, lint, test)
3. **Version management**: Auto-bump patch version or use your specified VERSION
4. **Update files**: Modify `pyproject.toml` and generate changelog entry
5. **Git operations**: Create release branch, commit changes, push branch
6. **Next steps**: Display instructions for creating PR and completing release

**Manual Release Process (Alternative):**

1. **Development**: Create PRs with descriptive titles and proper labels
2. **Pre-Release**: Ensure all tests pass and documentation is updated
3. **Release**: Create GitHub release - changelog updates automatically
4. **Verification**: Check generated changelog for accuracy

**Example Manual Release Creation:**

```sh
# Using GitHub CLI
gh release create v0.1.8 \
  --title "Release 0.1.8: Enhanced Plugin System" \
  --notes "This release adds new plugin capabilities and fixes several bugs."

# Using GitHub web interface
# Go to Releases → "Create a new release" → Fill in tag, title, and notes
```

### Manual Changelog Commands

Available Makefile commands for changelog management:

```sh
# Generate changelog entry for latest version
make changelog-generate

# Update changelog with current changes  
make changelog-update

# View all changelog-related commands
make help | grep changelog
```
