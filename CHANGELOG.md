# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Enhanced Testing System**: Modernized fixture-based testing infrastructure
  - Updated testing system to locate `.expected` files alongside `.adoc` files in fixture directories
  - Added `get_same_dir_fixture_pairs()` function for improved fixture discovery
  - Enhanced `fetch-fixtures.sh` script to preserve `.expected` files during fixture updates
  - Created comprehensive `.expected` files for all 113 test fixtures across all plugin directories
  - Improved test reliability and maintainability

- **PR #6**: Comprehensive documentation update
  - Updated all markdown files to reflect current project state
  - Improved package structure documentation
  - Enhanced README with accurate CLI usage examples
  - Added development workflow documentation

### Changed

- **PR #6**: Documentation accuracy improvements
  - Fixed package structure references in docs/asciidoc-dita-toolkit.md
  - Updated CLI command examples throughout documentation
  - Improved contributor guidelines and testing instructions

## [0.1.4] - 2025-01-XX

### Added

- **PR #5**: Development workflow and documentation improvements
  - Enhanced Makefile with automation targets (test, lint, format, clean, publish)
  - Added comprehensive SECURITY.md with vulnerability reporting guidelines
  - Expanded docs/CONTRIBUTING.md with detailed testing and development guide
  - Added version pinning in requirements-dev.txt for reproducible builds
  - Added CLI testing via installed console script in test suite

### Changed

- **PR #5**: Improved development experience
  - Enhanced dependency management with specific version constraints
  - Improved test automation and CI integration
  - Better documentation for new contributors and maintainers

## [0.1.3] - 2025-01-XX

### Added

- **PR #4**: Comprehensive testing infrastructure
  - Complete test suite with 20 tests covering all functionality
  - Enhanced test_cli.py with robust subprocess-based CLI testing
  - Improved test_EntityReference.py with comprehensive fixture testing
  - Added asciidoc_testkit.py with shared testing utilities and mocking
  - Full test coverage for plugin discovery, CLI interface, and error handling

### Changed

- **PR #4**: Testing methodology improvements
  - Migrated to fixture-based testing for better reliability
  - Added comprehensive mocking for file operations
  - Improved test organization and documentation

### Fixed

- **PR #4**: Test reliability and coverage gaps
  - Fixed CLI testing to use installed console script
  - Resolved test isolation issues
  - Enhanced error handling test coverage

## [0.1.2] - 2025-01-XX

### Added

- **PR #3**: CLI and toolkit improvements
  - Enhanced plugin discovery system with better error handling
  - Improved CLI help messages and user experience
  - Added comprehensive plugin registration validation

### Changed

- **PR #3**: Core functionality improvements
  - Updated toolkit.py with better plugin management
  - Improved pyproject.toml configuration for package discovery
  - Enhanced entry point configuration for CLI reliability

### Fixed

- **PR #3**: CLI and plugin system reliability
  - Fixed plugin discovery and registration issues
  - Resolved entry point configuration problems
  - Improved error messages and debugging information

## [0.1.1] - 2025-01-XX

### Added

- **PR #2**: Plugin standardization and improvement
  - Standardized plugin interfaces across EntityReference and ContentType
  - Added consistent error handling and logging across plugins
  - Improved plugin documentation and docstrings

### Changed

- **PR #2**: Plugin architecture improvements
  - Unified naming conventions and code style across plugins
  - Enhanced plugin configuration and parameter handling
  - Improved plugin testing interfaces

### Fixed

- **PR #2**: Plugin reliability and consistency
  - Fixed inconsistencies between plugin interfaces
  - Resolved plugin-specific bugs and edge cases
  - Improved error handling in plugin execution

## [0.1.0] - 2025-01-XX

### Added

- **PR #1**: Core infrastructure cleanup and improvements
  - Enhanced file_utils.py with comprehensive utility functions
  - Added proper docstrings and type hints throughout codebase
  - Implemented consistent error handling patterns

### Changed

- **PR #1**: Code quality and maintainability improvements
  - Removed dead code and unused imports
  - Standardized code formatting and style
  - Improved module organization and structure

### Fixed

- **PR #1**: Core functionality and reliability
  - Fixed file handling edge cases
  - Resolved import and dependency issues
  - Improved error messages and debugging

## [0.1.3] - 2025-06-16 (Legacy)

### Changed

- Incremented version for new release (see pyproject.toml).
- Fixed all documentation and CLI usage instructions to use the correct module path: `asciidoc_dita_toolkit.asciidoc_dita.toolkit`.
- Updated all plugin and utility imports to use relative imports for package compatibility.

## [0.1.2] - 2025-06-16 (Legacy)

### Changed

- Incremented version for new release.

## [1.0.1] - 2025-06-13 (Legacy)

### Added

- Unified CLI interface with `asciidoc-dita` command
- Plugin auto-discovery system
- EntityReference plugin for HTML entity conversion
- ContentType plugin for content type labels
- Comprehensive CLI test suite
- Beginner-friendly CONTRIBUTING.md guide
- Development tools (Makefile, pre-commit hooks)
- PyPI packaging configuration

### Changed

- **BREAKING**: Transformed from modular package to unified CLI
- **BREAKING**: Removed individual plugin commands (`asciidoc-dita-*`)
- **BREAKING**: Removed legacy `toolkit.py` interface
- Simplified plugin interfaces (removed `run_cli()` requirement)
- Updated documentation to focus on CLI usage
- Refactored test suite to use BaseCliTestCase for shared functionality
- Improved import formatting and code style consistency
- Updated CI workflow to install full development dependencies
- Consolidated metadata management (version and description now single-sourced from pyproject.toml)

### Removed

- Legacy `toolkit.py` CLI interface
- Individual plugin entry points
- `run-plugin` subcommand
- Deprecated test artifacts
- Duplicate version strings and descriptions across multiple files

### Fixed

- Module import errors in CLI interface and plugin loading
- GitHub Actions CI workflow - added pytest installation via dev dependencies
- Package discovery configuration in pyproject.toml for proper editable installs
- PYTHONPATH configuration in test suite for subprocess execution
- isort configuration to use correct package name for import sorting
- Import path issues in CLI interface
- Plugin registration and discovery
- Error handling and exit codes
- Test compatibility with new architecture
- File truncation bug in ContentType plugin preventing content corruption

### Technical Notes

- Requires Python 3.7+
- Zero runtime dependencies (lightweight installation)
- Comprehensive test coverage with subprocess-based CLI testing
- Following jhradilek's wrapper-based CLI recommendations
- Dynamic metadata import system with fallbacks for older Python versions
