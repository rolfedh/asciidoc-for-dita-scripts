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
    "ExampleBlock": "Detect and process example blocks in documentation"
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

For plugin-specific help: adt <plugin> -h"""
    
    print(help_text)


def get_version():
    """Get the version of adt package."""
    try:
        return importlib.metadata.version("asciidoc-dita-toolkit")
    except importlib.metadata.PackageNotFoundError:
        # Fallback to module version for development/uninstalled package
        try:
            from . import __version__
            return __version__
        except ImportError:
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
                    # Suppress warnings during help operations by only logging to debug level
                    pass
    
    except Exception as e:
        # Suppress warnings during help operations by only logging to debug level  
        pass
    
    return plugins


def get_new_modules_for_help():
    """Get available modules from the new module system with all warnings suppressed for help display."""
    modules = {}
    
    try:
        # Temporarily suppress all logging to avoid module discovery warnings during help
        import logging
        original_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.ERROR)
        
        try:
            sequencer = ModuleSequencer()
            sequencer.set_suppress_legacy_warnings(True)
            sequencer.discover_modules()
            
            for name, module in sequencer.available_modules.items():
                # Use module's description property if available, otherwise use generic description
                description = getattr(module, 'description', f"New module system: {name} v{module.version}")
                modules[name] = {
                    "module": module,
                    "description": description
                }
        finally:
            # Restore original logging level
            logging.getLogger().setLevel(original_level)
            
    except Exception as e:
        # Silently fail during help operations
        pass
    
    return modules


def get_new_modules():
    """Get available modules from the new module system."""
    modules = {}
    
    try:
        sequencer = ModuleSequencer()
        sequencer.discover_modules()
        
        for name, module in sequencer.available_modules.items():
            # Use module's description property if available, otherwise use generic description
            description = getattr(module, 'description', f"New module system: {name} v{module.version}")
            modules[name] = {
                "module": module,
                "description": description
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
            # Use module's description property if available, otherwise use generic description
            description = getattr(module, 'description', f"New module system: {name} v{module.version}")
            modules[name] = {
                "module": module,
                "description": description
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


def print_detailed_plugin_list(suppress_warnings: bool = True):
    """Print a detailed, well-formatted list of all available plugins and modules."""
    print("AVAILABLE PLUGINS:\n")
    
    # Get legacy plugins (warnings already suppressed in function)
    legacy_plugins = get_legacy_plugins()
    
    # Get new modules with warnings completely suppressed for help display
    new_modules = get_new_modules_for_help()
    
    # Combine and sort all plugins
    all_plugins = {}
    
    # Add legacy plugins
    for name, info in legacy_plugins.items():
        all_plugins[name] = {
            "description": info['description'], 
            "type": "legacy"
        }
    
    # Add new modules (avoid duplicates)
    for name, info in new_modules.items():
        if name not in all_plugins:
            all_plugins[name] = {
                "description": info['description'],
                "type": "module"
            }
    
    if not all_plugins:
        print("  No plugins available")
        return
    
    # Print plugins with clear descriptions
    for name in sorted(all_plugins.keys()):
        desc = PLUGIN_DESCRIPTIONS.get(name, all_plugins[name]['description'])
        print(f"  {name:<16} {desc}")
    
    print(f"\nUSAGE EXAMPLES:")
    print(f"  adt ContentType -r                    # Process all .adoc files recursively")
    print(f"  adt CrossReference -f myfile.adoc     # Process specific file") 
    print(f"  adt EntityReference -d docs/          # Process files in docs/ directory")
    print(f"\nOPTIONS FOR EACH PLUGIN:")
    print(f"  -f, --file FILE       Process a specific file")
    print(f"  -r, --recursive       Process all .adoc files recursively")  
    print(f"  -d, --directory DIR   Specify root directory (default: current)")
    print(f"  -v, --verbose         Enable verbose output")
    print(f"\nFor plugin-specific help: adt <plugin> -h")


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
    description = PLUGIN_DESCRIPTIONS.get(name, plugin_info["description"])
    parser = subparsers.add_parser(name, help=description)
    
    # Add common arguments that legacy plugins expect
    parser.add_argument(
        "-f", "--file", 
        help="Process a specific file"
    )
    parser.add_argument(
        "-r", "--recursive", 
        action="store_true",
        help="Process all .adoc files recursively in the current directory"
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
    description = PLUGIN_DESCRIPTIONS.get(name, module_info["description"])
    parser = subparsers.add_parser(name, help=description)
    
    # Add common arguments
    parser.add_argument(
        "-f", "--file", 
        help="Process a specific file"
    )
    parser.add_argument(
        "-r", "--recursive", 
        action="store_true",
        help="Process all .adoc files recursively in the current directory"
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


class CustomHelpAction(argparse.Action):
    """Custom help action that prints our formatted help."""
    
    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, help=None):
        super().__init__(option_strings, dest, nargs=0, default=default, help=help)
    
    def __call__(self, parser, namespace, values, option_string=None):
        print_custom_help()
        parser.exit()


def main(args=None):
    """Main entry point for the CLI."""
    
    parser = argparse.ArgumentParser(
        description="ADT - AsciiDoc DITA Toolkit",
        prog="adt",
        add_help=False  # We handle help ourselves
    )
    
    # Add custom help action
    parser.add_argument(
        "-h", "--help",
        action=CustomHelpAction,
        help="Show this help message and exit"
    )
    
    parser.add_argument(
        "--list-plugins",
        action="store_true",
        help="List all available plugins with detailed descriptions"
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
        help="Suppress warnings for legacy plugins during transition (default)"
    )
    parser.add_argument(
        "--show-warnings",
        action="store_true",
        help="Show warnings for legacy plugins (overrides --suppress-warnings)"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=False, metavar="<plugin>")
    
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
            suppress_warnings = temp_args.suppress_warnings and not temp_args.show_warnings
        except (argparse.ArgumentError, ValueError, SystemExit) as e:
            # Use default if parsing fails - this can happen with malformed arguments
            # SystemExit can occur when parse_known_args encounters --help in subcommands
            pass
    
    # For help operations, use the warning-suppressed version
    if args and ("-h" in args or "--help" in args or "--list-plugins" in args):
        new_modules = get_new_modules_for_help()
    else:
        new_modules = get_new_modules_with_warnings_control(suppress_warnings)
        
    for name, info in new_modules.items():
        # Only add if not already added by legacy plugins
        if name not in legacy_plugins:
            create_new_module_subcommand(subparsers, name, info)
    
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
        version = get_version()
        print(f"adt {version}")
        print("AsciiDoc DITA Toolkit - unified package for technical documentation workflows")
        print("https://github.com/rolfedh/asciidoc-dita-toolkit")
        sys.exit(0)
    
    if parsed_args.list_plugins:
        suppress_warnings = parsed_args.suppress_warnings and not parsed_args.show_warnings
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