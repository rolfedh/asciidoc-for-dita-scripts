# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Note**: This changelog is automatically generated from GitHub releases and PR labels.
> See [GitHub Releases](https://github.com/rolfedh/asciidoc-dita-toolkit/releases) for detailed release notes.

## [Unreleased]

## [2.0.10] - 2025-07-22

- Initial commit
- Add a requirements file and created a basic Python script to convert README.md rules to an html file.
- Created fix EntityReference script
- Added user documentation to the script
- Refactor AsciiDoc entity replacement script to use shared utilities and improve maintainability
- Add comprehensive documentation and clarify logic in fix_entity_references.py
- Migrate fix_entity_references.py to plugin system and update for CLI integration
- Add reusable AsciiDoc testkit and improve test fixture warnings
- Initial draft of the README content
- Update README.md
- Rename project to asciidoc-dita-toolkit and update all references
- Add GitHub Actions CI for automated testing
- Improve README: Add explicit command examples for setup and usage
- Added plugins/fix_content_type.py
- Renames fix_content_type.py to FixContentType.py for consistency
- Update get_fixture_pairs to handle missing directories
- Add and consolidate GitHub Actions CI workflow with fixture directory setup
- Improved the README.md file to include more detailed instructions on how to use the project, including examples and troubleshooting tips.
- Updated filenames and content to use EntityReference
- Refactor tests for unittest discovery, update CI and README with test instructions
- Update test fixtures
- Renamed FixContentType to ContentType.
- ContentType plugin check now matches the Vale plugin regular expression check
- Add expected files for EntityReference
- Create contributor guide
- Improved worflow for contributors
- Improve CONTRIBUTING.md
- Updated ContentType to check for files types based on prefix that ends with a dash as well as underscore. Accepted file name prefixes are now:
- Fixed a few syntax errors to that I could run the tool.
- Initialize Python package structure for asciidoc-dita-toolkit
- Updated pyproject.toml
- Restructure documentation for user personas: end-user README and developer CONTRIBUTING guide
- Cleaned up the repository and made the package executable.
- Add archive unused files utility
- Add GitHub Copilot settings to workspace configuration
- Bump version to 0.1.2 and add changelog for release notes
- Add GitHub Actions workflow for publishing Python package to PyPI
- Bump version to 0.1.3 and update changelog for release notes
- Revert version to 0.1.2 in pyproject.toml
- Add publishing instructions for PyPI to CONTRIBUTING.md
- Fix command usage in README.md for plugin execution
- Fix import statement for file_utils in process_adoc_files function
- Update changelog for version 0.1.3 and increment version in pyproject.toml
- Add upgrade instructions to README.md and clarify publishing steps in CONTRIBUTING.md
- Update README.md for simplified command usage and fix script path in pyproject.toml
- Bump version to 0.1.4 in pyproject.toml
- Add initial project structure with configuration and test files
- Update README.md with resource links and bump version to 0.1.5 in pyproject.toml
- Remove obsolete workspace configuration file
- Add workspace configuration file for project structure
- Unify file search behavior across plugins by adding directory and recursive options to argument parsers (#36)
- Add script to fetch and organize test fixtures for local testing. Also add the upstream test fixtures. (#34)
- Add pre-commit hooks for code quality and update contributor instructions (#32)
- Update CONTRIBUTING.md to include branch protection rules and guidelines (#33)
- Add comprehensive agentic code review prompts for AI-assisted reviews (#41)
- Removed unused code and simplified option parsing. (#38)
- Clean up core infrastructure and remove dead code (#42)
- Standardize plugins with consistent patterns and best practices (#43)
- Improve CLI entry point and toolkit structure (#44)
- Add comprehensive test coverage for CLI and plugins (#45)
- Workflow: Enhance development workflow and documentation (#46)
- Documentation update (#47)
- Enhance testing system (#48)
- Automate changelog management with GitHub Actions (#49)
- Fix EntityReference plugin and update expected files to comply with DITA 1.3 rule (#50)
- Add Plugin Development Pattern documentation (#51)
- Ci: Add daily workflow to fetch and PR test fixtures from asciidoctor-dita-vale (#52)
- Archive fetch-fixtures.sh and update docs to reference automated GitHub Actions workflow (#53)
- Publish 0.1.7 (#56)
- Add Docker support with multi-stage builds (#55)
- ContentType Plugin UI Design Ideas (#54)
- Update README and CONTRIBUTING for containerized development support (#59)
- Remove command output from from test runs. (#58)
- Add beta testing and release process guides (#62)
- Docs/beta-documentation (#63)
- Update beta testing guide (#64)
- WIP Fix #57: Resolve requirements-dev.txt dependency constraints (#60)
- Update BETA_TESTING.md with v0.1.8b2 guide (#67)
- Ci: disable container builds on pull requests (#69)
- Update issue templates (#70)
- Update issue templates (#71)
- Update beta testing docs for 0.1.9b2 (#72)
- Update BETA_TESTING.md (#73)
- Update BETA_TESTING.md (#74)
- Update BETA_TESTING.md (#75)
- Update BETA_TESTING.md (#80)
- Add DirectoryConfig plugin for scoped AsciiDoc processing (#83)
- Implement all code quality improvements from issue #87 (#88)
- Fix ContentType plugin and update test suite (#90)
- Implement modularization as per issue #92
- Update file_utils.py for modularization and improve backward compatibility documentation
- Update DirectoryConfig tests for modular architecture
- Improve directory path matching in DirectoryConfig
- Implement modularization as per issue #92
- Update file_utils.py for modularization and improve backward compatibility documentation
- Address Copilot AI code review feedback and remove dead code
- Enhance common_arg_parser function with type hints and improve documentation
- Enhance modular files with type hints, improved docstrings, and code cleanup
- Correct environment variable naming for plugin enablement
- Add plugin filtering to support enabling/disabling plugins
- Refactor plugin import to improve module-level import structure
- Refactor DirectoryConfig with improved path handling and architecture
- Remove DirectoryConfig refactoring summary document
- Clean up DirectoryConfig.py
- Refactor ContentType plugin with improved modularity and testability
- Remove unused imports from content type detector and UI interface
- Refactor test content formatting for content type detection test
- Refactor content type detection and processing modules
- Checkpoint before follow-up message
- Improve content type selection UI with better suggestions and feedback
- Change logging level from info to debug in content type detection
- Add ContentType plugin output catalog documentation
- Add design docs for ContentType plugin output catalog and interface
- Improve content type selection UI with clearer prompts and controls
- Update content type analysis design with TBD handling and error cases
- Add quiet mode and auto-processing options to content type plugin design
- Add minimalist UI, quiet mode, and flexible content type detection
- Improve UI type detection using isinstance() for robust checking
- Refactor UI classes: Rename TestUI to MockUI and update references
- Add nightly release workflow with automatic version bumping and PyPI publish
- Add context migration toolkit with analysis, migration, and xref plugins
- Checkpoint before follow-up message
- Improve cross-reference processing with two-pass ID mapping strategy
- Add centralized regex patterns module with comprehensive tests
- Improve xref and link parsing with more robust regex handling
- Improve ID migration with global collision resolution and safer backups
- Moved docs to folders
- Add comprehensive spec feedback for ADT module configuration system
- Add comprehensive ADT module configuration design specification
- Create comprehensive ADT module configuration system personas guide
- Replace setup.py with pyproject.toml for module configuration
- Refactor module sequencing with comprehensive ModuleSequencer implementation
- Update module configuration documentation with version details
- Add comments to clarify module configuration and dependency structure
- Checkpoint before follow-up message
- Implement ADT module system with sequencing and configuration management
- Implement legacy plugin integration and CLI for adt-core package
- Refactor modules to use new workflow utils and improve file processing
- Add implementation instructions and architectural recommendations for ADTModule migration
- Add Cursor AI implementation instructions for ADTModule architecture migration
- Implement ADTModule migration for EntityReference with warning control
- Add documentation and tests for Phase 3 ADTModule migration validation
- Migrate ContentType plugin to ADTModule with full backward compatibility
- Migrate ContextAnalyzer, ContextMigrator, CrossReference to ADTModule
- Rename TestModule to MockModule in test module sequencer
- Set fixed random seed for deterministic test file generation
- Fix packaging to include full ADT toolkit and improve installation
- Update packaging recommendations to ship complete ADT toolkit and improve entry point configuration
- Enhance packaging recommendations to unify ADT toolkit and improve installation instructions
- Refined the content for cursor.com
- Remove src directory and update project configuration
- Remove test-pypi-install/ directory from tracking
- Add test-pypi-install/ to .gitignore
- Update package directory structure in pyproject.toml to reflect new src layout
- Remove package-dir configuration for adt_core in pyproject.toml
- Update version bump script to reflect new src directory structure
- Update CHANGELOG, README, and migration documentation for unified package v2.0.0; enhance Makefile and CLI for improved usability
- Bump version to 2.0.2 and update .gitignore
- Improve virtual environment patterns in .gitignore
- Implement ExampleBlock plugin with comprehensive detection logic
- Improve ExampleBlock plugin user experience
- Update integration test for ExampleBlock module addition
- Enhance CLI description and update test configuration for ExampleBlock module
- Resolve CI test failure for init_order expectations
- Address Copilot AI feedback and enhance code quality
- Add GitHub Pages CI workflow and Jekyll configuration
- Reorganize test files - move valuable tests to tests/ directory
- Add README for archived test scripts
- Organize debug and demo scripts - clean up root directory
- Move development markdown files to docs/ directory
- Complete cruft cleanup: final organization
- Fix recurring integration test failure with robust dependency ordering check
- Clean up test output: suppress non-functional warnings
- Fix performance baseline tests
- Fix CI test runner: switch from unittest to pytest
- Add pytest to development requirements
- Address code review feedback: improve performance tests and add debug logging
- Configure Black for developer-friendly quote handling
- Fix #133: Improve adt -h output with clear usage patterns
- Fix #133: Improve CLI help with professional formatting and code quality
- Bump version to 2.0.4 in pyproject.toml and __init__.py
- Fix #136: Add GitHub issues link to CLI help output for user feedback reporting
- Remove redundant dev-setup target and format code with Black
- Streamline dev-setup script and improve flake8 configuration
- Fix terminal crash issue with SystemExit handling
- Extract SystemExit handling to shared utility function
- Enhancement: Add plugin versions to --version output
- Fix #144: Migrate pytest dependencies to unittest
- Clean up pytest compatibility code from test files
- Fix #132: Create common path calculation utility
- Improve code structure and readability in cli.py
- Update terminology from 'module' to 'plugin' in cli.py and module_sequencer.py
- Standardize on pytest as primary testing framework
- Add ADT Plugin Creation Template for Claude Sonnet 4 including config instructions
- Remove outdated user guide and documentation files; consolidate into a new comprehensive README and plugin documentation
- Add comprehensive documentation and example scripts for AsciiDoc DITA Toolkit
- Revert "Add comprehensive documentation and example scripts for AsciiDoc DITA…"
- Restructure documentation: index.md for technical writers, README.md for developers/maintainers. Improved content and clarified audience.
- Remove outdated user guide README.md to streamline documentation structure
- Upgrade documentation to modern Jekyll theme with professional styling (#156)
- Fix GitHub Pages workflow and Jekyll configuration (#157)
- Disable Docker workflow automatic triggers due to auth issues (#159)
- Fix Jekyll theme deployment - remove conflicting github-pages gem (#160)
- Add missing Jekyll plugins for Just the Docs theme (#161)
- Migrate from Docker Hub to GitHub Container Registry (fixes #158) (#162)
- Reorganize documentation: move historical files to archive
- Address Copilot AI code review feedback
- Bump version to 2.0.5 in pyproject.toml and __init__.py
- Refactor README.md: Update shield badges and streamline content for clarity
- Remove legacy plugins from known list as all have been migrated to ADTModule
- Add comprehensive documentation for ModuleSequencer, covering architecture, configuration, dependency management, and best practices.
- Enhance ModuleSequencer documentation: Add sections on dual plugin architecture and clarify orchestration vs legacy execution
- Enhance GitHub release automation: Update `make github-release` to create tags if they don't exist and improve publish target to include changelog update
- Revert "Enhance GitHub release automation: Update `make github-release` to cr…"
- Add UserJourney plugin design and restructure module dependencies (#172)
- Enhance publish target: Update to include changelog generation and ad… (#176)
- Fix version bumping paths and add tests for target correctness (#177)
- Bump version to 2.0.7 and update dependencies in Makefile for build and twine (#178)
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
