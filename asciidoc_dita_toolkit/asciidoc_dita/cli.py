"""
CLI Module for AsciiDoc DITA Toolkit

This module provides the main CLI interface for the toolkit with subcommands
for each plugin and common operations. It serves as a wrapper that delegates
to the appropriate functions in the toolkit.
"""

import argparse
import importlib
import os
import sys
from pathlib import Path

from . import __version__

try:
    from importlib.metadata import metadata
    _package_metadata = metadata("asciidoc-dita-toolkit")
    _description = _package_metadata["Summary"]
except ImportError:
    try:
        from importlib_metadata import metadata
        _package_metadata = metadata("asciidoc-dita-toolkit")
        _description = _package_metadata["Summary"]
    except ImportError:
        _description = "AsciiDoc DITA Toolkit - A unified CLI for AsciiDoc DITA processing"


def discover_plugins():
    """Discover all available plugins in the plugins directory."""
    plugins = []
    plugins_dir = Path(__file__).parent / "plugins"

    if plugins_dir.exists():
        for file_path in plugins_dir.glob("*.py"):
            if file_path.name != "__init__.py":
                plugins.append(file_path.stem)

    return sorted(plugins)


def print_plugin_list():
    """Print a list of all available plugins with their descriptions."""
    plugins = discover_plugins()

    if not plugins:
        print("No plugins found.")
        return

    print("Available plugins:")
    print("=" * 50)
    for modname in plugins:
        try:
            module = importlib.import_module(f"asciidoc_dita_toolkit.asciidoc_dita.plugins.{modname}")
            description = getattr(module, "__doc__", "No description available").strip()
            # Take only the first line of docstring for brief description
            brief_desc = (
                description.split("\n")[0]
                if description
                else "No description available"
            )
            print(f"  {modname:<20} - {brief_desc}")
        except Exception as e:
            print(f"  {modname:<20} - Error loading plugin: {e}")


def create_parser():
    """Create and configure the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="asciidoc-dita",
        description=_description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  asciidoc-dita --list-plugins          # List all available plugins
  asciidoc-dita EntityReference -r      # Run EntityReference plugin recursively
  asciidoc-dita ContentType -d /path    # Run ContentType plugin on directory

For plugin-specific help:
  asciidoc-dita <plugin-name> --help
""",
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--list-plugins",
        action="store_true",
        help="List all available plugins and their descriptions",
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available plugins", metavar="<plugin>"
    )

    # Discover and register all plugins as subcommands
    plugins = discover_plugins()
    for modname in plugins:
        try:
            module = importlib.import_module(f"asciidoc_dita_toolkit.asciidoc_dita.plugins.{modname}")
            if hasattr(module, "register_subcommand"):
                module.register_subcommand(subparsers)
        except Exception as e:
            print(f"Warning: Error loading plugin '{modname}': {e}", file=sys.stderr)

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.list_plugins:
        print_plugin_list()
        return

    # If a subcommand was specified and has a func attribute, call it
    if hasattr(args, "func"):
        try:
            exit_code = args.func(args)
            sys.exit(exit_code or 0)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
