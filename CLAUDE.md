# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

The AsciiDoc DITA Toolkit is a Python-based CLI tool that processes AsciiDoc files for DITA publishing workflows through a plugin-based architecture.

### Core Architecture
- **adt_core**: Main application framework with CLI entry point and ModuleSequencer
- **Plugin System**: Modular plugins via Python entry points for different content processing tasks
- **Configuration**: JSON-based configuration with directory-specific overrides
- **Module Sequencer**: Handles plugin discovery, dependency resolution, and execution ordering

### Key Components
- **CLI Entry Point**: `asciidoc_dita_toolkit.adt_core.cli:main` provides `adt` command
- **Plugin Discovery**: Uses Python entry points (`adt.modules`) for automatic plugin registration
- **ModuleSequencer**: Central orchestrator at `asciidoc_dita_toolkit/adt_core/module_sequencer.py`
- **Plugin Base**: All plugins inherit from ADTModule base class with standardized interface

### Plugin Architecture
Each plugin processes specific AsciiDoc content patterns:
- **ContentType**: Validates/adds content type metadata
- **EntityReference**: Processes HTML entity references
- **DirectoryConfig**: Manages directory-specific configurations
- **ExampleBlock**: Handles example block formatting
- **UserJourney**: Interactive workflow for content analysis
- **ValeFlagger**: Integration with Vale linting tool

## Development Commands

### Environment Setup
```bash
# Create virtual environment and install dev dependencies
make setup

# Manual setup
make venv
source .venv/bin/activate
make install-dev
```

### Testing
```bash
# Run all tests
make test
pytest tests/ -v

# Run with coverage
make test-coverage

# Run specific plugin tests
pytest tests/test_ContentType.py -v
pytest tests/test_user_journey.py -v
```

### Code Quality
```bash
# Format code
make format
python3 -m black .

# Lint code (comprehensive)
make lint

# Quick critical error check
python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Building and Publishing
```bash
# Build package
make build

# Automated release (maintainers only)
make publish

# Create GitHub release
make github-release
```

### Container Development
```bash
# Build containers
make container-build        # Development
make container-build-prod   # Production

# Test in container
make container-test

# Interactive container shell
make container-shell
```

## Configuration System

### Main Configuration
- **adt-user-config.json**: User-level configuration file
- **Directory configs**: Override settings per directory/project
- **Plugin-specific**: Each plugin can have custom configuration schema

### Configuration Hierarchy
1. System defaults
2. User config (adt-user-config.json)
3. Directory-specific configs
4. Command-line arguments

## Plugin Development

### Plugin Structure
All plugins must:
- Inherit from `ADTModule` base class
- Implement required methods: `run()`, `get_description()`, etc.
- Register via entry points in pyproject.toml
- Follow the established plugin patterns in `asciidoc_dita_toolkit/modules/`

### Testing Plugins
- Test fixtures in `tests/fixtures/[PluginName]/`
- Expected output files with `.expected` extension
- Vale integration for content validation

## Key Files and Patterns

### Entry Points
- `adt`: Main CLI command
- `valeflag`: Vale integration tool
- Plugin registration via `[project.entry-points."adt.modules"]`

### Module Organization
- **asciidoc_dita_toolkit/adt_core/**: Core framework
- **asciidoc_dita_toolkit/modules/**: Plugin implementations
- **asciidoc_dita_toolkit/plugins/**: Special plugins (like vale_flagger)
- **tests/**: Comprehensive test suite with fixtures

### Development Patterns
- Use ModuleSequencer for plugin orchestration
- Follow existing plugin patterns for consistency
- Test fixtures should include both positive and negative cases
- Configuration should be validated and provide helpful error messages