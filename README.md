# AsciiDoc DITA Toolkit

A unified command-line toolkit for reviewing and fixing AsciiDoc content in DITA-based publishing workflows. Built with a flexible plugin system based on rules from the [asciidoctor-dita-vale](https://github.com/jhradilek/asciidoctor-dita-vale) project.

## What is this?

The AsciiDoc DITA Toolkit is a wrapper-based CLI tool for technical writers and editors. It helps you:
- Find and fix common issues in `.adoc` files before publishing
- Apply automated checks and transformations using a modular plugin system
- Run individual plugins as standalone tools or through a unified interface

## Installation

### Option 1: PyPI (Recommended)

```sh
pip install asciidoc-dita-toolkit
```

### Option 2: Development Installation

```sh
git clone https://github.com/yourusername/asciidoc-dita-toolkit.git
cd asciidoc-dita-toolkit
pip install -e .
```

## Usage

### Unified CLI Interface

After installation, use the main `asciidoc-dita` command:

```sh
# List all available plugins
asciidoc-dita --list-plugins

# Run a specific plugin
asciidoc-dita <plugin-name> [options]

# Get help for a specific plugin
asciidoc-dita <plugin-name> --help

# Alternative syntax for running plugins
asciidoc-dita run-plugin <plugin-name> [options]
```

### Individual Plugin Commands

Each plugin is also available as a standalone command:

```sh
# Run individual plugin commands directly
asciidoc-dita-entity-reference [options]
asciidoc-dita-content-type [options]
```

### Examples

**Fix HTML entity references in a specific file:**
```sh
asciidoc-dita EntityReference -f path/to/file.adoc
```

**Process all .adoc files recursively:**
```sh
asciidoc-dita EntityReference -r
```

**Add content type labels based on filename:**
```sh
asciidoc-dita ContentType -d /path/to/docs
```

**Use the legacy toolkit interface:**
```sh
asciidoc-dita-toolkit --list-plugins
asciidoc-dita-toolkit EntityReference -f file.adoc
```

## Available Plugins

The toolkit currently includes these plugins:

| Plugin | Description | Command |
|--------|-------------|---------|
| **EntityReference** | Replace unsupported HTML character entity references with AsciiDoc attribute references | `asciidoc-dita EntityReference` |
| **ContentType** | Add `:_mod-docs-content-type:` labels based on filename patterns | `asciidoc-dita ContentType` |

Use `asciidoc-dita --list-plugins` to see all available plugins with descriptions.

## Implementation Summary

The `asciidoc-dita-toolkit` has been successfully transformed into a wrapper-based CLI system with standalone scripts, following jhradilek's recommendations:

### ✅ Completed Implementation

1. **Unified CLI Interface** - `asciidoc-dita` command with subcommands
2. **Individual Plugin Commands** - `asciidoc-dita-*` commands for each plugin  
3. **Plugin Auto-Discovery** - Automatic registration of plugins as subcommands
4. **CLI Entry Points** - Proper packaging with multiple entry points in `pyproject.toml`
5. **Standardized Plugin Interface** - All plugins implement `main()`, `run_cli()`, and `register_subcommand()`
6. **Comprehensive Testing** - CLI-based tests using subprocess calls
7. **Error Handling** - Proper exit codes and error messages
8. **Documentation** - Updated README and CONTRIBUTING guides

### 📁 Project Structure

```
asciidoc-dita-toolkit/
├── asciidoc_dita_toolkit/asciidoc_dita/
│   ├── cli.py              # Main unified CLI interface
│   ├── toolkit.py          # Legacy CLI (maintained for compatibility) 
│   ├── file_utils.py       # Shared utilities
│   └── plugins/            # Auto-discovered plugins
│       ├── EntityReference.py
│       └── ContentType.py
├── tests/test_cli.py       # CLI-based tests
├── docs/CONTRIBUTING.md    # Plugin development guide
└── pyproject.toml         # CLI entry points and packaging
```

### 🚀 CLI Entry Points

| Command | Purpose | Entry Point |
|---------|---------|-------------|
| `asciidoc-dita` | Main unified CLI | `asciidoc_dita.cli:main` |
| `asciidoc-dita-toolkit` | Legacy CLI | `asciidoc_dita.toolkit:main` |
| `asciidoc-dita-entity-reference` | EntityReference plugin | `asciidoc_dita.plugins.EntityReference:run_cli` |
| `asciidoc-dita-content-type` | ContentType plugin | `asciidoc_dita.plugins.ContentType:run_cli` |

### ✨ Key Features

- **Plugin System**: Easy to add new plugins - just drop them in `plugins/` directory
- **Multiple Interfaces**: Use unified CLI, individual commands, or import as a library
- **Backward Compatible**: Legacy CLI still works for existing users
- **Standards Compliant**: Follows Python packaging best practices
- **Well Tested**: Comprehensive test suite with 100% CLI test coverage

This implementation successfully makes it easy to run, extend, and maintain individual plugins while providing a unified, user-friendly interface.

## Plugin Development

Want to create your own plugins? Each plugin needs:

1. A `main(args)` function that accepts parsed command-line arguments
2. A `register_subcommand(subparsers)` function for CLI integration
3. A `run_cli()` function for standalone execution
4. Standard error handling and validation

See existing plugins in `asciidoc_dita/plugins/` for examples.

## Troubleshooting

- **Python Version**: Requires Python 3.7 or newer
- **Plugin Errors**: Use `asciidoc-dita --list-plugins` to check for plugin loading issues
- **File Permissions**: Ensure you have read/write access to target files and directories

For development setup and advanced usage, see [CONTRIBUTING.md](docs/CONTRIBUTING.md).

## Related resources

- **[`asciidoctor-dita-vale`](https://github.com/jhradilek/asciidoctor-dita-vale)**: Vale style rules and test fixtures for validating AsciiDoc content.

## Contributing

Want to add new plugins or help improve the toolkit? See [CONTRIBUTING.md](docs/CONTRIBUTING.md).