"""
Command-line interface for adt_core.

This module provides backward compatibility with the old asciidoc-dita-toolkit
while integrating with the new plugin system.
"""

import argparse
import importlib
import importlib.metadata
import os
import sys
from pathlib import Path

from .module_sequencer import ModuleSequencer


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def handle_system_exit(component_name: str, component_type: str, exit_exception: SystemExit) -> None:
    """
    Handle SystemExit exceptions from plugins gracefully.
    
    Args:
        component_name: Name of the plugin that exited
        component_type: Type of component (always 'plugin')
        exit_exception: The SystemExit exception that was caught
    """
    if exit_exception.code != 0:
        print(f"Error: {component_type.capitalize()} {component_name} exited with code {exit_exception.code}", file=sys.stderr)
    sys.exit(exit_exception.code)


# =============================================================================
# PLUGIN DESCRIPTIONS
# =============================================================================

# Centralized plugin descriptions used across help functions
# This avoids duplication and ensures consistency
PLUGIN_DESCRIPTIONS = {
    "ContentType": "Add/update content type attributes in AsciiDoc files",
    "ContextAnalyzer": "Analyze context IDs and cross-references",
    "ContextMigrator": "Migrate context-dependent IDs to context-free format",
    "CrossReference": "Validate and fix cross-references between files",
    "DirectoryConfig": "Manage directory-specific plugin configurations",
    "EntityReference": "Convert HTML entities to AsciiDoc equivalents",
    "ExampleBlock": "Detect and process example blocks in documentation",
}


def print_custom_help():
    """Print custom help message with clear usage patterns."""
    help_text = """Usage: adt <plugin> [options]
       adt --list-plugins
       adt --version
       adt --help

ADT - AsciiDoc DITA Toolkit

PLUGINS:
  Run one plugin at a time to process your AsciiDoc files:

    ContentType       Add/update content type attributes
    ContextAnalyzer   Analyze context IDs and references
    ContextMigrator   Migrate context-dependent IDs
    CrossReference    Validate and fix cross-references
    DirectoryConfig   Manage directory-specific configurations
    EntityReference   Convert HTML entities to AsciiDoc
    ExampleBlock      Detect and process example blocks

TARGET FILES:
  -f, --file FILE       Process a specific file
  -r, --recursive       Process all .adoc files recursively
  -d, --directory DIR   Specify root directory (default: current)

VERBOSITY:
  -v, --verbose         Enable verbose output

OTHER OPTIONS:
  -h, --help            Show this help message and exit
  --list-plugins        List detailed plugin information
  --version             Show version information

EXAMPLES:
  adt ContentType -r                    # Process all .adoc files recursively
  adt CrossReference -f myfile.adoc     # Process specific file
  adt EntityReference -d docs/          # Process files in docs/ directory

For plugin-specific help: adt <plugin> -h

Report bugs or request features: https://github.com/rolfedh/asciidoc-dita-toolkit/issues
"""
    print(help_text)


def get_version():
    """Get the version of adt package."""
    try:
        return importlib.metadata.version("asciidoc-dita-toolkit")
    except importlib.metadata.PackageNotFoundError:
        # Fallback to plugin version for development/uninstalled package
        try:
            from . import __version__

            return __version__
        except ImportError:
            return "unknown"


def print_version_with_plugins():
    """Print version information including plugin versions."""
    # Print main tool version
    version = get_version()
    print(f"adt {version}")
    print("AsciiDoc DITA Toolkit - unified package for technical documentation workflows")
    print("https://github.com/rolfedh/asciidoc-dita-toolkit")
    print()
    
    # Get plugin information
    legacy_plugins = get_legacy_plugins()
    new_plugins = get_new_plugins_for_help()
    
    # Combine and sort all plugins with version info
    all_plugins = []
    
    # Add new plugins first (they have proper version info)
    for name, info in new_plugins.items():
        desc = PLUGIN_DESCRIPTIONS.get(name, info['description'])
        version_str = getattr(info['plugin'], 'version', 'unknown')
        all_plugins.append((name, version_str, desc))
    
    # Add legacy plugins only if they don't exist in new plugins
    for name, info in legacy_plugins.items():
        if name not in new_plugins:
            desc = PLUGIN_DESCRIPTIONS.get(name, info['description'])
            # Try to get version from plugin, fallback to 'legacy'
            version_str = getattr(info.get('plugin'), '__version__', 'legacy')
            all_plugins.append((name, version_str, desc))
    
    if all_plugins:
        print("AVAILABLE PLUGINS:")
        # Sort by plugin name
        all_plugins.sort(key=lambda x: x[0])
        
        # Calculate dynamic column widths
        name_width = max(len(name) for name, _, _ in all_plugins) + 2
        version_width = max(len(version_str) for _, version_str, _ in all_plugins) + 2
        
        # Print each plugin with dynamic widths
        for name, version_str, desc in all_plugins:
            print(f"  {name:<{name_width}} v{version_str:<{version_width}} {desc}")
    else:
        print("No plugins available")


def get_legacy_plugins():
    """Get available legacy plugins from the old system."""
    plugins = {}

    # Try to import the old plugin system
    try:
        # Get the path to the old plugins directory
        package_root = Path(__file__).parent.parent.parent
        legacy_plugins_path = (
            package_root / "asciidoc_dita_toolkit" / "asciidoc_dita" / "plugins"
        )

        if legacy_plugins_path.exists():
            # Add the legacy path to sys.path temporarily
            if str(package_root) not in sys.path:
                sys.path.insert(0, str(package_root))

            # Import available plugins
            from asciidoc_dita_toolkit.asciidoc_dita.plugin_manager import (
                is_plugin_enabled,
            )

            for plugin_file in legacy_plugins_path.glob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue

                plugin_name = plugin_file.stem

                # Skip if not enabled
                if not is_plugin_enabled(plugin_name):
                    continue

                try:
                    plugin_module = importlib.import_module(
                        f"asciidoc_dita_toolkit.asciidoc_dita.plugins.{plugin_name}"
                    )

                    # Check if it has the required functions
                    if hasattr(plugin_module, "register_subcommand") and hasattr(
                        plugin_module, "main"
                    ):
                        description = getattr(plugin_module, "__description__", plugin_name)
                        plugins[plugin_name] = {
                            "plugin": plugin_module,
                            "description": description,
                        }
                except Exception as e:
                    # Suppress warnings during help operations by only logging to debug level
                    pass

    except Exception as e:
        # Suppress warnings during help operations by only logging to debug level
        pass

    return plugins


def get_new_plugins_for_help():
    """Get available plugins from the new plugin system with all warnings suppressed for help display."""
    plugins = {}

    try:
        # Temporarily suppress all logging to avoid plugin discovery warnings during help
        import logging

        original_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.ERROR)

        try:
            sequencer = ModuleSequencer()
            sequencer.set_suppress_legacy_warnings(True)
            sequencer.discover_modules()

            for name, plugin in sequencer.available_modules.items():
                # Use plugin's description property if available, otherwise use generic description
                description = getattr(
                    plugin,
                    'description',
                    f"New plugin system: {name} v{plugin.version}",
                )
                plugins[name] = {"plugin": plugin, "description": description}
        finally:
            # Restore original logging level
            logging.getLogger().setLevel(original_level)

    except Exception as e:
        # Silently fail during help operations
        pass

    return plugins


def get_new_plugins():
    """Get available plugins from the new plugin system."""
    plugins = {}

    try:
        sequencer = ModuleSequencer()
        sequencer.discover_modules()

        for name, plugin in sequencer.available_modules.items():
            # Use plugin's description property if available, otherwise use generic description
            description = getattr(
                plugin, 'description', f"New plugin system: {name} v{plugin.version}"
            )
            plugins[name] = {"plugin": plugin, "description": description}
    except Exception as e:
        print(f"Warning: Could not load new plugins: {e}", file=sys.stderr)

    return plugins


def get_new_plugins_with_warnings_control(suppress_warnings: bool = True):
    """Get available plugins from the new plugin system with warning control."""
    plugins = {}

    try:
        sequencer = ModuleSequencer()
        sequencer.set_suppress_legacy_warnings(suppress_warnings)
        sequencer.discover_modules()

        for name, plugin in sequencer.available_modules.items():
            # Use plugin's description property if available, otherwise use generic description
            description = getattr(
                plugin, 'description', f"New plugin system: {name} v{plugin.version}"
            )
            plugins[name] = {"plugin": plugin, "description": description}
    except Exception as e:
        print(f"Warning: Could not load new plugins: {e}", file=sys.stderr)

    return plugins


def print_plugin_list():
    """Print a list of all available plugins."""
    print("Available plugins:")

    # Get legacy plugins
    legacy_plugins = get_legacy_plugins()
    if legacy_plugins:
        print("\nLegacy plugins:")
        for name, info in legacy_plugins.items():
            print(f"  {name:20} {info['description']}")

    # Get new plugins
    new_plugins = get_new_plugins()
    if new_plugins:
        print("\nNew plugins:")
        for name, info in new_plugins.items():
            print(f"  {name:20} {info['description']}")

    if not legacy_plugins and not new_plugins:
        print("  No plugins available")


def print_detailed_plugin_list(suppress_warnings: bool = True):
    """Print a detailed, well-formatted list of all available plugins."""
    print("AVAILABLE PLUGINS:\n")

    # Get legacy plugins (warnings already suppressed in function)
    legacy_plugins = get_legacy_plugins()

    # Get new plugins with warnings completely suppressed for help display
    new_plugins = get_new_plugins_for_help()

    # Combine and sort all plugins
    all_plugins = {}

    # Add legacy plugins
    for name, info in legacy_plugins.items():
        all_plugins[name] = {"description": info['description'], "type": "legacy"}

    # Add new plugins (avoid duplicates)
    for name, info in new_plugins.items():
        if name not in all_plugins:
            all_plugins[name] = {"description": info['description'], "type": "plugin"}

    if not all_plugins:
        print("  No plugins available")
        return

    # Print plugins with clear descriptions
    for name in sorted(all_plugins.keys()):
        desc = PLUGIN_DESCRIPTIONS.get(name, all_plugins[name]['description'])
        print(f"  {name:<16} {desc}")

    print(f"\nUSAGE EXAMPLES:")
    print(
        f"  adt ContentType -r                    # Process all .adoc files recursively"
    )
    print(f"  adt CrossReference -f myfile.adoc     # Process specific file")
    print(f"  adt EntityReference -d docs/          # Process files in docs/ directory")
    print(f"\nOPTIONS FOR EACH PLUGIN:")
    print(f"  -f, --file FILE       Process a specific file")
    print(f"  -r, --recursive       Process all .adoc files recursively")
    print(f"  -d, --directory DIR   Specify root directory (default: current)")
    print(f"  -v, --verbose         Enable verbose output")
    print(f"\nFor plugin-specific help: adt <plugin> -h")


def print_plugin_list_with_warnings_control(suppress_warnings: bool = True):
    """Print a list of all available plugins with warning control."""
    print("Available plugins:")

    # Get legacy plugins
    legacy_plugins = get_legacy_plugins()
    if legacy_plugins:
        print("\nLegacy plugins:")
        for name, info in legacy_plugins.items():
            print(f"  {name:20} {info['description']}")

    # Get new plugins
    new_plugins = get_new_plugins_with_warnings_control(suppress_warnings)
    if new_plugins:
        print("\nNew plugins:")
        for name, info in new_plugins.items():
            print(f"  {name:20} {info['description']}")

    if not legacy_plugins and not new_plugins:
        print("  No plugins available")


def create_legacy_subcommand(subparsers, name, plugin_info):
    """Create a subcommand for a legacy plugin."""
    description = PLUGIN_DESCRIPTIONS.get(name, plugin_info["description"])
    parser = subparsers.add_parser(name, help=description)

    # Add common arguments that legacy plugins expect
    parser.add_argument("-f", "--file", help="Process a specific file")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Process all .adoc files recursively in the current directory",
    )
    parser.add_argument(
        "-d",
        "--directory",
        default=".",
        help="Specify the root directory to search (default: current directory)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    # Set the function to call
    def run_legacy_plugin(args):
        try:
            plugin_info["plugin"].main(args)
        except SystemExit as e:
            handle_system_exit(name, "plugin", e)
        except Exception as e:
            print(f"Error running plugin {name}: {e}", file=sys.stderr)
            sys.exit(1)
    
    parser.set_defaults(func=run_legacy_plugin)


def create_new_plugin_subcommand(subparsers, name, plugin_info):
    """Create a subcommand for a new plugin."""
    description = PLUGIN_DESCRIPTIONS.get(name, plugin_info["description"])
    parser = subparsers.add_parser(name, help=description)

    # Add common arguments
    parser.add_argument("-f", "--file", help="Process a specific file")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Process all .adoc files recursively in the current directory",
    )
    parser.add_argument(
        "-d",
        "--directory",
        default=".",
        help="Specify the root directory to search (default: current directory)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    # Set the function to call
    def run_new_plugin(args):
        try:
            # Initialize plugin
            plugin = plugin_info["plugin"]
            config = {"verbose": args.verbose}
            plugin.initialize(config)

            # Execute plugin
            context = {
                "file": args.file,
                "recursive": args.recursive,
                "directory": args.directory,
                "verbose": args.verbose,
            }
            result = plugin.execute(context)

            if args.verbose:
                print(f"Plugin result: {result}")

            # Cleanup
            plugin.cleanup()

        except SystemExit as e:
            handle_system_exit(name, "plugin", e)
        except Exception as e:
            print(f"Error running plugin {name}: {e}", file=sys.stderr)
            sys.exit(1)

    parser.set_defaults(func=run_new_plugin)


class CustomHelpAction(argparse.Action):
    """Custom help action that prints our formatted help."""

    def __init__(
        self,
        option_strings,
        dest=argparse.SUPPRESS,
        default=argparse.SUPPRESS,
        help=None,
    ):
        super().__init__(option_strings, dest, nargs=0, default=default, help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        print_custom_help()
        parser.exit()


def main(args=None):
    """Main entry point for the CLI."""

    parser = argparse.ArgumentParser(
        description="ADT - AsciiDoc DITA Toolkit",
        prog="adt",
        add_help=False,  # We handle help ourselves
    )

    # Add custom help action
    parser.add_argument(
        "-h", "--help", action=CustomHelpAction, help="Show this help message and exit"
    )

    parser.add_argument(
        "--list-plugins",
        action="store_true",
        help="List all available plugins with detailed descriptions",
    )
    parser.add_argument(
        "--version", action="store_true", help="Show version information"
    )
    parser.add_argument(
        "--suppress-warnings",
        action="store_true",
        default=True,
        help="Suppress warnings for legacy plugins during transition (default)",
    )
    parser.add_argument(
        "--show-warnings",
        action="store_true",
        help="Show warnings for legacy plugins (overrides --suppress-warnings)",
    )

    subparsers = parser.add_subparsers(
        dest="command", required=False, metavar="<plugin>"
    )

    # Load legacy plugins (warnings suppressed)
    legacy_plugins = get_legacy_plugins()
    for name, info in legacy_plugins.items():
        create_legacy_subcommand(subparsers, name, info)

    # Load new modules with warning control
    suppress_warnings = True  # Default
    if args:
        try:
            # Pre-parse to get warning control flags
            temp_args, _ = parser.parse_known_args(args)
            suppress_warnings = (
                temp_args.suppress_warnings and not temp_args.show_warnings
            )
        except (argparse.ArgumentError, ValueError, SystemExit) as e:
            # Use default if parsing fails - this can happen with malformed arguments
            # SystemExit can occur when parse_known_args encounters --help in subcommands
            pass

    # For help operations, use the warning-suppressed version
    if args and ("-h" in args or "--help" in args or "--list-plugins" in args):
        new_plugins = get_new_plugins_for_help()
    else:
        new_plugins = get_new_plugins_with_warnings_control(suppress_warnings)

    for name, info in new_plugins.items():
        # Only add if not already added by legacy plugins
        if name not in legacy_plugins:
            create_new_plugin_subcommand(subparsers, name, info)

    # Parse arguments
    if args is None:
        args = sys.argv[1:]

    # Check for no arguments - show help
    if not args:
        print_custom_help()
        sys.exit(1)

    parsed_args = parser.parse_args(args)

    # Handle special flags
    if parsed_args.version:
        print_version_with_plugins()
        sys.exit(0)

    if parsed_args.list_plugins:
        suppress_warnings = (
            parsed_args.suppress_warnings and not parsed_args.show_warnings
        )
        print_detailed_plugin_list(suppress_warnings)
        sys.exit(0)

    # Execute the selected command
    if hasattr(parsed_args, "func"):
        try:
            parsed_args.func(parsed_args)
        except Exception as e:
            print(f"Error executing command: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Show help if no command provided
        print_custom_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
