# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Note**: This changelog is automatically generated from GitHub releases and PR labels.
> See [GitHub Releases](https://github.com/rolfedh/asciidoc-dita-toolkit/releases) for detailed release notes.

## [Unreleased]

## [2.0.10] - 2025-07-22

- Troubleshoot pypi issues (#179)
- Troubleshoot changelog gen issues (#180)
- Update README: Clarify Python Prerequisites and Container Option, Add adt-docker Script (#181)
- Comment out overused triggers and redundant Dockerfile paths in container build workflow (#182)
- Docs reorg (#183)
- Add ValeFlagger plugin specification and implementation details (#184)
- Build ValeFlagger from spec (#186)
- Fix Makefile syntax error in publish target (#187)

## [2.0.10] - 2025-07-22

- Troubleshoot pypi issues (#179)
- Troubleshoot changelog gen issues (#180)
- Update README: Clarify Python Prerequisites and Container Option, Add adt-docker Script (#181)
- Comment out overused triggers and redundant Dockerfile paths in container build workflow (#182)
- Docs reorg (#183)
- Add ValeFlagger plugin specification and implementation details (#184)
- Build ValeFlagger from spec (#186)
- Fix Makefile syntax error in publish target (#187)

### 🚨 MAJOR RELEASE: Unified Package v2.0.0

- **NEW**: Complete unified package under familiar name `asciidoc-dita-toolkit`
- **CLI**: Convenient short command `adt` while keeping descriptive package name
- **COMPLETE**: Includes both core framework and all plugins in one installation
- **SIMPLIFIED**: No more split packages or missing module issues
- **INSTALL**: `pip install asciidoc-dita-toolkit` gives you everything you need

### Package and Installation
- Fixed package discovery to include both `adt_core` and `asciidoc_dita_toolkit` modules
- Updated all entry points and CLI scripts for unified package
- Enhanced version reporting and CLI help text
- Comprehensive testing in both development and user environments

### Documentation
- Updated README.md with correct installation instructions and package information
- Updated all CLI examples to use convenient `adt` command
- Created comprehensive v2.0.0 information guide
- Updated PyPI badge and links to reference correct package name

### Testing and Quality
- Enhanced testing system with colocated expected files
- Modernized fixture-based testing infrastructure
- Verified all 196 tests pass in unified package
- Added comprehensive packaging and installation testing

## [0.1.6] - 2025-06-29

- Comprehensive documentation update and deduplication
- Enhanced README with accurate CLI usage examples
- Improved contributor guidelines and project structure docs

## [0.1.5] - 2025-06-29

- Development workflow improvements with Makefile automation
- Added comprehensive security guidelines
- Enhanced testing and CI infrastructure

## [0.1.4] - 2025-06-29

- Complete test suite with 20 tests covering all functionality
- Enhanced CLI testing and plugin validation
- Improved test organization and reliability

## [0.1.3] - 2025-06-29

- CLI and toolkit improvements with better error handling
- Enhanced plugin discovery system
- Improved user experience and help messages

## [0.1.2] - 2025-06-29

- Plugin standardization with consistent interfaces
- Enhanced error handling and logging
- Improved plugin architecture and documentation

## [0.1.1] - 2025-06-29

- Core infrastructure cleanup and improvements
- Enhanced file utilities with proper type hints
- Standardized code formatting and organization

## [0.1.0] - 2025-06-16

- Initial release of AsciiDoc DITA Toolkit
- Unified CLI interface with plugin auto-discovery
- EntityReference and ContentType plugins
- Zero runtime dependencies, Python 3.7+ support
