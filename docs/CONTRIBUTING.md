# Contributing to AsciiDoc DITA Toolkit

Thank you for your interest in contributing! This guide is for developers and maintainers working with the wrapper-based CLI system.

## Project Structure

The toolkit uses a wrapper-based architecture with standalone scripts:

- **`asciidoc_dita_toolkit/asciidoc_dita/`**: Main Python package
  - `cli.py`: Unified CLI interface with subcommands
  - `toolkit.py`: Legacy CLI entry point (maintained for compatibility)
  - `file_utils.py`: Shared file and argument utilities
  - `plugins/`: Plugin directory with auto-discovery
    - `EntityReference.py`: HTML entity reference fixer
    - `ContentType.py`: Content type label adder
    - `__init__.py`: Plugin initialization
- **`tests/`**: Automated tests and test fixtures
- **`docs/`**: Project documentation
- **`pyproject.toml`**: Packaging, metadata, and CLI entry points

## CLI Entry Points

The toolkit provides multiple entry points:

| Command | Description | Target |
|---------|-------------|--------|
| `asciidoc-dita` | Main unified CLI | `asciidoc_dita.cli:main` |
| `asciidoc-dita-toolkit` | Legacy CLI | `asciidoc_dita.toolkit:main` |
| `asciidoc-dita-entity-reference` | EntityReference plugin | `asciidoc_dita.plugins.EntityReference:run_cli` |
| `asciidoc-dita-content-type` | ContentType plugin | `asciidoc_dita.plugins.ContentType:run_cli` |

## Getting Started

1. **Fork and clone the repository**
   ```sh
   git clone https://github.com/<your-org>/asciidoc-dita-toolkit.git
   cd asciidoc-dita-toolkit
   ```

2. **Set up a virtual environment (recommended)**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate  # On Linux/macOS
   # or .venv\Scripts\activate  # On Windows
   ```

3. **Install in editable mode for development**
   ```sh
   pip install -e .
   ```

4. **Verify the installation**
   ```sh
   asciidoc-dita --list-plugins
   asciidoc-dita --help
   ```

## Creating New Plugins

Each plugin must implement three key functions for CLI compatibility:

### 1. Plugin Structure

```python
"""
Plugin for the AsciiDoc DITA toolkit: MyPlugin

Brief description of what the plugin does.
"""

__description__ = "Brief description for CLI help"
__version__ = "1.0.0"

import sys
import argparse

def main(args):
    """
    Main entry point for the plugin.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    try:
        # Your plugin logic here
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

def run_cli():
    """Standalone CLI runner for this plugin."""
    parser = argparse.ArgumentParser(
        description=__description__,
        prog="MyPlugin"
    )
    # Add your arguments here
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    sys.exit(main(args))

def register_subcommand(subparsers):
    """Register this plugin as a subcommand in the main CLI."""
    parser = subparsers.add_parser(
        "MyPlugin",
        help=__description__
    )
    # Add your arguments here
    parser.add_argument('--version', action='version', version=f'MyPlugin {__version__}')
    parser.set_defaults(func=main)

if __name__ == "__main__":
    run_cli()
```

### 2. Adding CLI Entry Points

To make your plugin available as a standalone command, add it to `pyproject.toml`:

```toml
[project.scripts]
# Add this line for your plugin
asciidoc-dita-my-plugin = "asciidoc_dita.plugins.MyPlugin:run_cli"
```

### 3. Plugin Auto-Discovery

Plugins are automatically discovered by the main CLI. Just place your plugin file in `asciidoc_dita/plugins/` and it will be available as a subcommand.

## Writing and Running Tests
- Add or update test files in `tests/` (prefix with `test_`, e.g., `test_MyPlugin.py`).
- Use `unittest` and the shared testkit (`asciidoc_testkit.py`).
- Place test fixtures in `tests/fixtures/<PluginName>/`.
- Run all tests:
  ```sh
  python3 -m unittest discover -s tests
  ```

## CI Integration
- Ensure `.github/workflows/ci.yml` runs all tests and downloads fixtures if needed.
- All pull requests must pass CI before merging.

## Review and Merge
- Open a pull request for your changes.
- Request review from maintainers.
- Address feedback, ensure CI passes, and merge when approved.

## Toolkit Components Overview

* **`asciidoc_toolkit.py`**: CLI entry point, discovers and runs plugins.
* **`plugins/`**: Individual plugin scripts for transformations/validations.
* **`file_utils.py`**: Shared file/argument utilities.
* **`tests/`**: Automated tests and fixtures.
* **`requirements.txt`**: Python dependencies for development.
* **`README.md`**: End-user setup, usage, and project overview.

## Why contribute?

- Modern Python and robust testing practices
- Improve publishing workflows for AsciiDoc and DITA
- Active review and maintenance

