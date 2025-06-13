# AsciiDoc DITA Toolkit

A unified command-line toolkit for reviewing and fixing AsciiDoc content in DITA-based publishing workflows. Built with a flexible plugin system based on rules from the [asciidoctor-dita-vale](https://github.com/jhradilek/asciidoctor-dita-vale) project.

## What is this?

The AsciiDoc DITA Toolkit is a streamlined CLI tool for technical writers and editors. It helps you:
- Find and fix common issues in `.adoc` files before publishing
- Apply automated checks and transformations using a modular plugin system
- Run plugins through a single, unified interface

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

## Available Plugins

The toolkit currently includes these plugins:

| Plugin | Description | Command |
|--------|-------------|---------|
| **EntityReference** | Replace unsupported HTML character entity references with AsciiDoc attribute references | `asciidoc-dita EntityReference` |
| **ContentType** | Add `:_mod-docs-content-type:` labels based on filename patterns | `asciidoc-dita ContentType` |

Use `asciidoc-dita --list-plugins` to see all available plugins with descriptions.

## Implementation Summary

The `asciidoc-dita-toolkit` provides a clean, unified CLI interface following modern best practices:

### ✅ Current Architecture

1. **Single CLI Entry Point** - `asciidoc-dita` command with plugin subcommands
2. **Plugin Auto-Discovery** - Automatic registration of plugins as subcommands  
3. **Standardized Plugin Interface** - All plugins implement `main()` and `register_subcommand()`
4. **Comprehensive Testing** - CLI-based tests using subprocess calls
5. **Error Handling** - Proper exit codes and error messages
6. **Clean Documentation** - Focused on the unified CLI interface

### 📁 Project Structure

```
asciidoc-dita-toolkit/
├── asciidoc_dita_toolkit/asciidoc_dita/
│   ├── cli.py              # Main unified CLI interface
│   ├── file_utils.py       # Shared utilities
│   └── plugins/            # Auto-discovered plugins
│       ├── EntityReference.py
│       └── ContentType.py
├── tests/test_cli.py       # CLI-based tests
├── docs/CONTRIBUTING.md    # Plugin development guide
└── pyproject.toml         # Single CLI entry point and packaging
```

### 🚀 CLI Usage

| Command | Purpose |
|---------|---------|
| `asciidoc-dita --list-plugins` | List available plugins |
| `asciidoc-dita EntityReference [options]` | Run EntityReference plugin |
| `asciidoc-dita ContentType [options]` | Run ContentType plugin |

### ✨ Key Features

- **Simplified Interface**: Single entry point with intuitive plugin subcommands
- **Plugin System**: Easy to add new plugins - just drop them in `plugins/` directory
- **Library Usage**: Plugins can still be imported and used programmatically
- **Standards Compliant**: Follows Python packaging best practices
- **Well Tested**: Comprehensive test suite with complete CLI coverage

This streamlined implementation makes it easy to run, extend, and maintain plugins through a clean, unified interface.

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