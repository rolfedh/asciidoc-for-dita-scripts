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





def get_modules_for_help():
    """Get formatted module list for help display."""
    try:
        modules = get_new_modules_for_help()
        if not modules:
            return "    No modules available"
        
        # Format modules for help display
        lines = []
        for name, info in sorted(modules.items()):
            desc = info['description']
            # Truncate long descriptions for clean help display
            if len(desc) > 50:
                desc = desc[:47] + "..."
            lines.append(f"    {name:<17} {desc}")
        return "\n".join(lines)
    except Exception:
        return "    No modules available"


def print_custom_help():
    """Print custom help message with dynamically generated module list."""
    modules_section = get_modules_for_help()
    
    help_text = f"""Usage: adt <module> [options]
       adt --list-modules
       adt --version
       adt --help

ADT - AsciiDoc DITA Toolkit

MODULES:
  Run one module at a time to process your AsciiDoc files:

{modules_section}

TARGET FILES:
  -f, --file FILE       Process a specific file
  -r, --recursive       Process all .adoc files recursively
  -d, --directory DIR   Specify root directory (default: current)

VERBOSITY:
  -v, --verbose         Enable verbose output

OTHER OPTIONS:
  -h, --help            Show this help message and exit
  --list-modules        List detailed module information
  --version             Show version information

EXAMPLES:
  adt ContentType -r                    # Process all .adoc files recursively
  adt CrossReference -f myfile.adoc     # Process specific file
  adt EntityReference -d docs/          # Process files in docs/ directory

For module-specific help: adt <module> -h

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


def print_version_with_modules():
    """Print version information including module versions."""
    # Print main tool version
    version = get_version()
    print(f"adt {version}")
    print("AsciiDoc DITA Toolkit - unified package for technical documentation workflows")
    print("https://github.com/rolfedh/asciidoc-dita-toolkit")
    print()

    # Get module information from the new system
    new_modules = get_new_modules_for_help()

    # Sort modules by name
    all_modules = []

    # Add new modules
    for name, info in new_modules.items():
        desc = info['description']
        version_str = getattr(info['plugin'], 'version', 'unknown')
        all_modules.append((name, version_str, desc))

    if all_modules:
        print("AVAILABLE MODULES:")
        # Sort by module name
        all_modules.sort(key=lambda x: x[0])

        # Calculate dynamic column widths
        name_width = max(len(name) for name, _, _ in all_modules) + 2
        version_width = max(len(version_str) for _, version_str, _ in all_modules) + 2

        # Print each module with dynamic widths
        for name, version_str, desc in all_modules:
            print(f"  {name:<{name_width}} v{version_str:<{version_width}} {desc}")
    else:
        print("No modules available")


def get_new_modules_for_help():
    """Get available modules from the new module system with all warnings suppressed for help display."""
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
                # Try to get description from plugin's module first, then plugin instance
                description = None

                # Try to get the module that contains this plugin class
                try:
                    plugin_module = sys.modules.get(plugin.__class__.__module__)
                    if plugin_module:
                        description = getattr(plugin_module, '__description__', None)
                except:
                    pass

                # Fallback to plugin instance description or generic description
                if not description:
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


def get_new_modules():
    """Get available modules from the new module system."""
    plugins = {}

    try:
        sequencer = ModuleSequencer()
        sequencer.discover_modules()

        for name, plugin in sequencer.available_modules.items():
            # Try to get description from plugin's module first, then plugin instance
            description = None

            # Try to get the module that contains this plugin class
            try:
                plugin_module = sys.modules.get(plugin.__class__.__module__)
                if plugin_module:
                    description = getattr(plugin_module, '__description__', None)
            except:
                pass

            # Fallback to plugin instance description or generic description
            if not description:
                description = getattr(
                    plugin, 'description', f"New plugin system: {name} v{plugin.version}"
                )
            plugins[name] = {"plugin": plugin, "description": description}
    except Exception as e:
        print(f"Warning: Could not load new plugins: {e}", file=sys.stderr)

    return plugins


def get_new_modules_with_warnings_control(suppress_warnings: bool = True):
    """Get available modules from the new module system with warning control."""
    plugins = {}

    try:
        sequencer = ModuleSequencer()
        sequencer.set_suppress_legacy_warnings(suppress_warnings)
        sequencer.discover_modules()

        for name, plugin in sequencer.available_modules.items():
            # Try to get description from plugin's module first, then plugin instance
            description = None

            # Try to get the module that contains this plugin class
            try:
                plugin_module = sys.modules.get(plugin.__class__.__module__)
                if plugin_module:
                    description = getattr(plugin_module, '__description__', None)
            except:
                pass

            # Fallback to plugin instance description or generic description
            if not description:
                description = getattr(
                    plugin, 'description', f"New plugin system: {name} v{plugin.version}"
                )
            plugins[name] = {"plugin": plugin, "description": description}
    except Exception as e:
        print(f"Warning: Could not load new plugins: {e}", file=sys.stderr)

    return plugins


def print_module_list():
    """Print a list of all available modules."""
    print("Available modules:")

    # Get modules from new system
    new_modules = get_new_modules()
    if new_modules:
        print("\nModules:")
        for name, info in new_modules.items():
            print(f"  {name:20} {info['description']}")
    else:
        print("  No modules available")


def print_detailed_module_list(suppress_warnings: bool = True):
    """Print a detailed, well-formatted list of all available modules."""
    print("AVAILABLE MODULES:\n")

    # Get modules with warnings completely suppressed for help display
    new_modules = get_new_modules_for_help()

    # Organize modules
    all_modules = {}

    # Add new modules
    for name, info in new_modules.items():
        all_modules[name] = {"description": info['description'], "type": "module"}

    if not all_modules:
        print("  No modules available")
        return

    # Print modules with clear descriptions
    for name in sorted(all_modules.keys()):
        desc = all_modules[name]['description']
        print(f"  {name:<16} {desc}")

    print(f"\nUSAGE EXAMPLES:")
    print(
        f"  adt ContentType -r                    # Process all .adoc files recursively"
    )
    print(f"  adt CrossReference -f myfile.adoc     # Process specific file")
    print(f"  adt EntityReference -d docs/          # Process files in docs/ directory")
    print(f"\nOPTIONS FOR EACH MODULE:")
    print(f"  -f, --file FILE       Process a specific file")
    print(f"  -r, --recursive       Process all .adoc files recursively")
    print(f"  -d, --directory DIR   Specify root directory (default: current)")
    print(f"  -v, --verbose         Enable verbose output")
    print(f"\nFor module-specific help: adt <module> -h")


def print_module_list_with_warnings_control(suppress_warnings: bool = True):
    """Print a list of all available modules with warning control."""
    print("Available modules:")

    # Get modules from new system
    new_modules = get_new_modules_with_warnings_control(suppress_warnings)
    if new_modules:
        print("\nModules:")
        for name, info in new_modules.items():
            print(f"  {name:20} {info['description']}")
    else:
        print("  No modules available")


def create_new_module_subcommand(subparsers, name, module_info):
    """Create a subcommand for a new module."""
    description = module_info["description"]
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
    def run_new_module(args):
        try:
            # Initialize module
            module = module_info["plugin"]
            config = {"verbose": args.verbose}
            module.initialize(config)

            # Execute module
            context = {
                "file": args.file,
                "recursive": args.recursive,
                "directory": args.directory,
                "verbose": args.verbose,
            }
            result = module.execute(context)

            if args.verbose:
                print(f"Module result: {result}")

            # Cleanup
            module.cleanup()

        except SystemExit as e:
            handle_system_exit(name, "module", e)
        except Exception as e:
            print(f"Error running module {name}: {e}", file=sys.stderr)
            sys.exit(1)

    parser.set_defaults(func=run_new_module)


def create_user_journey_subcommands(subparsers):
    """Create UserJourney workflow management subcommands."""
    try:
        # Import UserJourney module
        from asciidoc_dita_toolkit.modules.user_journey import UserJourneyModule

        # Initialize UserJourney module
        user_journey_module = UserJourneyModule()
        init_result = user_journey_module.initialize()

        if init_result.get("status") != "success":
            raise ImportError(f"Failed to initialize UserJourney: {init_result.get('message')}")

        # Create the journey command group
        journey_parser = subparsers.add_parser(
            'journey',
            help='Workflow orchestration commands for multi-module document processing'
        )

        # Create subcommands for journey
        journey_subparsers = journey_parser.add_subparsers(
            dest='journey_command',
            required=True,
            metavar='<action>',
            help='Available workflow actions'
        )

        # journey start
        start_parser = journey_subparsers.add_parser(
            'start',
            help='Create and start a new workflow'
        )
        start_parser.add_argument(
            '--name', '-n',
            required=True,
            help='Unique name for the workflow'
        )
        start_parser.add_argument(
            '--directory', '-d',
            required=True,
            help='Directory containing .adoc files to process'
        )

        # journey resume
        resume_parser = journey_subparsers.add_parser(
            'resume',
            help='Resume an existing workflow'
        )
        resume_parser.add_argument(
            '--name', '-n',
            required=True,
            help='Name of the workflow to resume'
        )

        # journey continue
        continue_parser = journey_subparsers.add_parser(
            'continue',
            help='Execute the next module in a workflow'
        )
        continue_parser.add_argument(
            '--name', '-n',
            required=True,
            help='Name of the workflow to continue'
        )

        # journey status
        status_parser = journey_subparsers.add_parser(
            'status',
            help='Show workflow status and progress'
        )
        status_parser.add_argument(
            '--name', '-n',
            help='Name of specific workflow to show (omit to show all)'
        )

        # journey list
        list_parser = journey_subparsers.add_parser(
            'list',
            help='List all available workflows'
        )

        # journey cleanup
        cleanup_parser = journey_subparsers.add_parser(
            'cleanup',
            help='Delete workflows'
        )
        cleanup_group = cleanup_parser.add_mutually_exclusive_group(required=True)
        cleanup_group.add_argument(
            '--name', '-n',
            help='Name of specific workflow to delete'
        )
        cleanup_group.add_argument(
            '--completed',
            action='store_true',
            help='Delete all completed workflows'
        )
        cleanup_group.add_argument(
            '--all',
            action='store_true',
            help='Delete all workflows (use with caution!)'
        )

        # Set the function to handle all journey commands
        def run_user_journey_command(args):
            try:
                exit_code = user_journey_module.process_cli_command(args)
                sys.exit(exit_code)

            except SystemExit:
                raise  # Re-raise SystemExit to preserve exit codes
            except Exception as e:
                print(f"❌ UserJourney command failed: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
                sys.exit(1)

        # Set the handler function for all journey subcommands
        for subparser in [start_parser, resume_parser, continue_parser, status_parser, list_parser, cleanup_parser]:
            subparser.set_defaults(func=run_user_journey_command)

    except ImportError as e:
        # UserJourney module not available - add a placeholder that shows a helpful message
        def journey_not_available(args):
            print("❌ UserJourney module not available", file=sys.stderr)
            print(f"   Import error: {e}", file=sys.stderr)
            print("   Make sure the package is properly installed and up-to-date", file=sys.stderr)
            sys.exit(1)

        # Create a basic journey command that shows the error
        journey_parser = subparsers.add_parser(
            'journey',
            help='Workflow orchestration (currently unavailable)'
        )
        journey_parser.set_defaults(func=journey_not_available)


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
        "--list-modules",
        action="store_true",
        help="List all available modules with detailed descriptions",
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
        dest="command", required=False, metavar="<module>"
    )

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
    if args and ("-h" in args or "--help" in args or "--list-modules" in args):
        new_modules = get_new_modules_for_help()
    else:
        new_modules = get_new_modules_with_warnings_control(suppress_warnings)

    for name, info in new_modules.items():
        # Add module subcommand
        create_new_module_subcommand(subparsers, name, info)

    # Add UserJourney CLI commands
    create_user_journey_subcommands(subparsers)

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
        print_version_with_modules()
        sys.exit(0)

    if parsed_args.list_modules:
        suppress_warnings = (
            parsed_args.suppress_warnings and not parsed_args.show_warnings
        )
        print_detailed_module_list(suppress_warnings)
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
