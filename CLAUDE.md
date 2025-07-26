# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

The AsciiDoc DITA Toolkit is a Python-based CLI tool that processes AsciiDoc files for DITA publishing workflows through a modular architecture.

### Core Architecture
- **adt_core**: Main application framework with CLI entry point and ModuleSequencer
- **Module System**: Modular architecture via Python entry points for different content processing tasks
- **Configuration**: JSON-based configuration with directory-specific overrides
- **Module Sequencer**: Handles module discovery, dependency resolution, and execution ordering

### Key Components
- **CLI Entry Point**: `asciidoc_dita_toolkit.adt_core.cli:main` provides `adt` command with automatic tab completion
- **Module Discovery**: Uses Python entry points (`adt.modules`) for automatic module registration
- **ModuleSequencer**: Central orchestrator at `asciidoc_dita_toolkit/adt_core/module_sequencer.py`
- **Module Base**: All modules inherit from ADTModule base class with standardized interface
- **Tab Completion**: Intelligent bash completion for modules, options, and file paths

### Module Architecture
Each module processes specific AsciiDoc content patterns:
- **ArchiveUnusedFiles**: Archives files not referenced in the documentation
- **ContentType**: Validates/adds content type metadata
- **ContextAnalyzer**: Analyzes context IDs and references
- **ContextMigrator**: Migrates context-dependent IDs
- **CrossReference**: Validates and fixes cross-references  
- **DirectoryConfig**: Manages directory-specific configurations
- **EntityReference**: Processes HTML entity references
- **ExampleBlock**: Handles example block formatting
- **UserJourney**: Interactive workflow orchestration for multi-module processing
- **ValeFlagger**: Integration with Vale linting tool for DITA compatibility

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

# Install tab completion
make install-completion

# Run specific module tests
pytest tests/test_ContentType.py -v
pytest tests/test_user_journey.py -v
pytest tests/test_cross_reference.py -v
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
- **Module-specific**: Each module can have custom configuration schema

### Configuration Hierarchy
1. System defaults
2. User config (adt-user-config.json)
3. Directory-specific configs
4. Command-line arguments

## Module Development

### Module Structure
All modules must:
- Inherit from `ADTModule` base class
- Implement required methods: `initialize()`, `execute()`, `cleanup()`
- Register via entry points in pyproject.toml under `[project.entry-points."adt.modules"]`
- Follow the established module patterns in `asciidoc_dita_toolkit/modules/`

### Testing Modules
- Test fixtures in `tests/fixtures/[ModuleName]/`
- Expected output files with `.expected` extension
- Vale integration for content validation
- Module-specific test files: `tests/test_[module_name].py`

## Key Files and Patterns

### Entry Points
- `adt`: Main CLI command with tab completion
- `adt-completion`: Tab completion helper
- `valeflag`: Vale integration tool
- Module registration via `[project.entry-points."adt.modules"]`

### Module Organization
- **asciidoc_dita_toolkit/adt_core/**: Core framework and CLI
- **asciidoc_dita_toolkit/modules/**: Module implementations
- **asciidoc_dita_toolkit/plugins/**: Legacy/special implementations (vale_flagger)
- **scripts/**: Installation and completion scripts
- **tests/**: Comprehensive test suite with fixtures

### Development Patterns
- Use ModuleSequencer for module orchestration and dependency management
- Follow established module patterns for consistency
- Test fixtures should include both positive and negative cases
- Configuration should be validated and provide helpful error messages
- All modules support common CLI options: `-f`, `-r`, `-d`, `-v`

## Tab Completion System

### Automatic Setup
- Tab completion automatically installs when users first run `adt`
- Installs to `~/.local/share/bash-completion/completions/adt`
- Provides intelligent completion for modules, options, and file paths

### Completion Features
- **Module completion**: `adt <TAB>` shows all available modules
- **Context-aware options**: Different completions per module
- **File filtering**: Only shows relevant file types (.adoc, .yaml, etc.)
- **Dynamic discovery**: Uses same module system as CLI
- **Journey integration**: Completes existing workflow names

### Manual Installation
```bash
# Install completion for development
make install-completion

# Direct script execution
./scripts/install-completion.sh
```

### Implementation
- **Bash script**: `scripts/adt-completion.bash`
- **Python helper**: `asciidoc_dita_toolkit.adt_core.completion`
- **CLI integration**: Automatic setup in `cli.py:main()`
- **Entry point**: `adt-completion` command for dynamic data