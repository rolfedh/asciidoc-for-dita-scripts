# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-06-13

### Fixed
- Module import errors in CLI interface and plugin loading
- GitHub Actions CI workflow - added pytest installation via dev dependencies
- Package discovery configuration in pyproject.toml for proper editable installs
- PYTHONPATH configuration in test suite for subprocess execution
- isort configuration to use correct package name for import sorting

### Changed
- Refactored test suite to use BaseCliTestCase for shared functionality
- Improved import formatting and code style consistency
- Updated CI workflow to install full development dependencies

## [1.0.0] - 2025-06-13

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

### Removed
- Legacy `toolkit.py` CLI interface
- Individual plugin entry points
- `run-plugin` subcommand
- Deprecated test artifacts

### Fixed
- Import path issues in CLI interface
- Plugin registration and discovery
- Error handling and exit codes
- Test compatibility with new architecture

### Technical Notes
- Requires Python 3.7+
- Zero runtime dependencies (lightweight installation)
- Comprehensive test coverage with subprocess-based CLI testing
- Following jhradilek's wrapper-based CLI recommendations
