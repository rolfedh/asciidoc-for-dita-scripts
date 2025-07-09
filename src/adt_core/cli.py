"""
Command-line interface for adt_core.

This module provides backward compatibility with the old asciidoc-dita-toolkit
while integrating with the new module system.
"""

import argparse
import importlib
import importlib.metadata
import os
import sys
from pathlib import Path

from .module_sequencer import ModuleSequencer


def get_version():
    """Get the version of adt-core package."""
    try:
        return importlib.metadata.version("adt-core")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def get_legacy_plugins():
    """Get available legacy plugins from the old system."""
    plugins = {}
    
    # Try to import the old plugin system
    try:
        # Get the path to the old plugins directory
        package_root = Path(__file__).parent.parent.parent
        legacy_plugins_path = package_root / "asciidoc_dita_toolkit" / "asciidoc_dita" / "plugins"
        
        if legacy_plugins_path.exists():
            # Add the legacy path to sys.path temporarily
            if str(package_root) not in sys.path:
                sys.path.insert(0, str(package_root))
            
            # Import available plugins
            from asciidoc_dita_toolkit.asciidoc_dita.plugin_manager import is_plugin_enabled
            
            for plugin_file in legacy_plugins_path.glob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue
                    
                plugin_name = plugin_file.stem
                
                # Skip if not enabled
                if not is_plugin_enabled(plugin_name):
                    continue
                    
                try:
                    module = importlib.import_module(
                        f"asciidoc_dita_toolkit.asciidoc_dita.plugins.{plugin_name}"
                    )
                    
                    # Check if it has the required functions
                    if hasattr(module, "register_subcommand") and hasattr(module, "main"):
                        description = getattr(module, "__description__", plugin_name)
                        plugins[plugin_name] = {
                            "module": module,
                            "description": description
                        }
                except Exception as e:
                    print(f"Warning: Could not load plugin {plugin_name}: {e}", file=sys.stderr)
    
    except Exception as e:
        print(f"Warning: Could not load legacy plugins: {e}", file=sys.stderr)
    
    return plugins


def get_new_modules():
    """Get available modules from the new module system."""
    modules = {}
    
    try:
        sequencer = ModuleSequencer()
        sequencer.discover_modules()
        
        for name, module in sequencer.available_modules.items():
            modules[name] = {
                "module": module,
                "description": f"New module system: {name} v{module.version}"
            }
    except Exception as e:
        print(f"Warning: Could not load new modules: {e}", file=sys.stderr)
    
    return modules


def get_new_modules_with_warnings_control(suppress_warnings: bool = True):
    """Get available modules from the new module system with warning control."""
    modules = {}
    
    try:
        sequencer = ModuleSequencer()
        sequencer.set_suppress_legacy_warnings(suppress_warnings)
        sequencer.discover_modules()
        
        for name, module in sequencer.available_modules.items():
            modules[name] = {
                "module": module,
                "description": f"New module system: {name} v{module.version}"
            }
    except Exception as e:
        print(f"Warning: Could not load new modules: {e}", file=sys.stderr)
    
    return modules


def print_plugin_list():
    """Print a list of all available plugins and modules."""
    print("Available plugins and modules:")
    
    # Get legacy plugins
    legacy_plugins = get_legacy_plugins()
    if legacy_plugins:
        print("\nLegacy plugins:")
        for name, info in legacy_plugins.items():
            print(f"  {name:20} {info['description']}")
    
    # Get new modules
    new_modules = get_new_modules()
    if new_modules:
        print("\nNew modules:")
        for name, info in new_modules.items():
            print(f"  {name:20} {info['description']}")
    
    if not legacy_plugins and not new_modules:
        print("  No plugins or modules available")


def print_plugin_list_with_warnings_control(suppress_warnings: bool = True):
    """Print a list of all available plugins and modules with warning control."""
    print("Available plugins and modules:")
    
    # Get legacy plugins
    legacy_plugins = get_legacy_plugins()
    if legacy_plugins:
        print("\nLegacy plugins:")
        for name, info in legacy_plugins.items():
            print(f"  {name:20} {info['description']}")
    
    # Get new modules
    new_modules = get_new_modules_with_warnings_control(suppress_warnings)
    if new_modules:
        print("\nNew modules:")
        for name, info in new_modules.items():
            print(f"  {name:20} {info['description']}")
    
    if not legacy_plugins and not new_modules:
        print("  No plugins or modules available")


def create_legacy_subcommand(subparsers, name, plugin_info):
    """Create a subcommand for a legacy plugin."""
    parser = subparsers.add_parser(name, help=plugin_info["description"])
    
    # Add common arguments that legacy plugins expect
    parser.add_argument(
        "-f", "--file", 
        help="Process a specific file"
    )
    parser.add_argument(
        "-r", "--recursive", 
        action="store_true",
        help="Process all .adoc files recursively"
    )
    parser.add_argument(
        "-d", "--directory", 
        default=".",
        help="Specify the root directory to search (default: current directory)"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    
    # Set the function to call
    parser.set_defaults(func=lambda args: plugin_info["module"].main(args))


def create_new_module_subcommand(subparsers, name, module_info):
    """Create a subcommand for a new module."""
    parser = subparsers.add_parser(name, help=module_info["description"])
    
    # Add common arguments
    parser.add_argument(
        "-f", "--file", 
        help="Process a specific file"
    )
    parser.add_argument(
        "-r", "--recursive", 
        action="store_true",
        help="Process all .adoc files recursively"
    )
    parser.add_argument(
        "-d", "--directory", 
        default=".",
        help="Specify the root directory to search (default: current directory)"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    
    # Set the function to call
    def run_new_module(args):
        try:
            # Initialize module
            module = module_info["module"]
            config = {"verbose": args.verbose}
            module.initialize(config)
            
            # Execute module
            context = {
                "file": args.file,
                "recursive": args.recursive,
                "directory": args.directory,
                "verbose": args.verbose
            }
            result = module.execute(context)
            
            if args.verbose:
                print(f"Module result: {result}")
            
            # Cleanup
            module.cleanup()
            
        except Exception as e:
            print(f"Error running module {name}: {e}", file=sys.stderr)
            sys.exit(1)
    
    parser.set_defaults(func=run_new_module)


def main(args=None):
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="ADT Core - AsciiDoc DITA Toolkit (adt-core)",
        prog="adt-core"
    )
    
    parser.add_argument(
        "--list-plugins",
        action="store_true",
        help="List all available plugins and modules"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information"
    )
    parser.add_argument(
        "--suppress-warnings",
        action="store_true",
        default=True,
        help="Suppress warnings for legacy plugins during transition (default: True)"
    )
    parser.add_argument(
        "--show-warnings",
        action="store_true",
        help="Show warnings for legacy plugins (overrides --suppress-warnings)"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=False)
    
    # Load legacy plugins
    legacy_plugins = get_legacy_plugins()
    for name, info in legacy_plugins.items():
        create_legacy_subcommand(subparsers, name, info)
    
    # Load new modules with warning control
    suppress_warnings = True  # Default
    if args:
        # Pre-parse to get warning control flags
        temp_args = parser.parse_args(args)
        suppress_warnings = temp_args.suppress_warnings and not temp_args.show_warnings
    
    new_modules = get_new_modules_with_warnings_control(suppress_warnings)
    for name, info in new_modules.items():
        # Only add if not already added by legacy plugins
        if name not in legacy_plugins:
            create_new_module_subcommand(subparsers, name, info)
    
    # Parse arguments
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parser.parse_args(args)
    
    # Handle special flags
    if parsed_args.version:
        version = get_version()
        print(f"adt-core {version}")
        print("(formerly asciidoc-dita-toolkit)")
        sys.exit(0)
    
    if parsed_args.list_plugins:
        suppress_warnings = parsed_args.suppress_warnings and not parsed_args.show_warnings
        print_plugin_list_with_warnings_control(suppress_warnings)
        sys.exit(0)
    
    # Execute the selected command
    if hasattr(parsed_args, "func"):
        try:
            parsed_args.func(parsed_args)
        except Exception as e:
            print(f"Error executing command: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()