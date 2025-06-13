"""
CLI Module for AsciiDoc DITA Toolkit

This module provides the main CLI interface for the toolkit with subcommands
for each plugin and common operations. It serves as a wrapper that delegates
to the appropriate functions in the toolkit.
"""
import argparse
import sys
from .toolkit import main as toolkit_main, discover_plugins, print_plugin_list
import importlib


def create_parser():
    """Create and configure the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="asciidoc-dita",
        description="AsciiDoc DITA Toolkit - A unified CLI for AsciiDoc DITA processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  asciidoc-dita --list-plugins          # List all available plugins
  asciidoc-dita EntityReference -r      # Run EntityReference plugin recursively
  asciidoc-dita ContentType -f file.adoc # Run ContentType plugin on specific file
  asciidoc-dita run-plugin EntityReference -r # Alternative syntax

For plugin-specific help:
  asciidoc-dita <plugin-name> --help
"""
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='%(prog)s 0.1.1'
    )
    parser.add_argument(
        '--list-plugins', 
        action='store_true', 
        help='List all available plugins and their descriptions'
    )
    
    subparsers = parser.add_subparsers(
        dest="command", 
        help='Available commands',
        metavar='<command>'
    )
    
    # Add a generic run-plugin subcommand
    run_plugin_parser = subparsers.add_parser(
        'run-plugin',
        help='Run a specific plugin by name'
    )
    run_plugin_parser.add_argument(
        'plugin_name',
        help='Name of the plugin to run'
    )
    run_plugin_parser.add_argument(
        'plugin_args',
        nargs=argparse.REMAINDER,
        help='Arguments to pass to the plugin'
    )
    run_plugin_parser.set_defaults(func=run_plugin_command)
    
    # Discover and register all plugins as subcommands
    plugins = discover_plugins()
    for modname in plugins:
        try:
            module = importlib.import_module(f"asciidoc_dita.plugins.{modname}")
            if hasattr(module, 'register_subcommand'):
                module.register_subcommand(subparsers)
        except Exception as e:
            print(f"Warning: Error loading plugin '{modname}': {e}", file=sys.stderr)
    
    return parser


def run_plugin_command(args):
    """Handle the run-plugin subcommand."""
    plugin_name = args.plugin_name
    plugin_args = args.plugin_args
    
    try:
        module = importlib.import_module(f"asciidoc_dita.plugins.{plugin_name}")
        if hasattr(module, 'main'):
            # Parse plugin-specific arguments
            plugin_parser = argparse.ArgumentParser(prog=f"asciidoc-dita run-plugin {plugin_name}")
            if hasattr(module, 'register_subcommand'):
                # Create a temporary subparser to get the plugin's arguments
                temp_subparsers = plugin_parser.add_subparsers()
                module.register_subcommand(temp_subparsers)
                
            plugin_parsed_args = plugin_parser.parse_args(plugin_args)
            exit_code = module.main(plugin_parsed_args)
            sys.exit(exit_code or 0)
        else:
            print(f"Error: Plugin '{plugin_name}' does not have a main function", file=sys.stderr)
            sys.exit(1)
    except ImportError:
        print(f"Error: Plugin '{plugin_name}' not found", file=sys.stderr)
        print("Use --list-plugins to see available plugins", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error running plugin '{plugin_name}': {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.list_plugins:
        print_plugin_list()
        return
    
    # If a subcommand was specified and has a func attribute, call it
    if hasattr(args, 'func'):
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
