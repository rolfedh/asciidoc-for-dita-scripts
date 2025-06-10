"""
asciidoc_toolkit.py - Unified CLI for AsciiDoc DITA scripts

This script provides a single entry point for running various AsciiDoc DITA checks and fixers as subcommands.
It dynamically discovers plugins in the 'plugins' directory. Each plugin must define a 'register_subcommand(subparsers)' function.
"""
import argparse
import importlib
import os
import sys

PLUGIN_DIR = os.path.join(os.path.dirname(__file__), 'plugins')

# Dynamically discover and import all plugin modules in the plugins directory
def discover_plugins():
    plugins = []
    if not os.path.isdir(PLUGIN_DIR):
        return plugins
    for fname in os.listdir(PLUGIN_DIR):
        if fname.endswith('.py') and not fname.startswith('_'):
            modname = fname[:-3]
            plugins.append(modname)
    return plugins

def print_plugin_list():
    print("Available plugins:")
    plugins = discover_plugins()
    for modname in plugins:
        try:
            module = importlib.import_module(f"asciidoc_dita.plugins.{modname}")
            desc = getattr(module, '__description__', None) or module.__doc__ or ''
            desc = desc.strip().split('\n')[0] if desc else ''
            print(f"  {modname:20} {desc}")
        except Exception as e:
            print(f"  {modname:20} (error loading plugin: {e})")

def main():
    parser = argparse.ArgumentParser(description="AsciiDoc DITA Toolkit")
    parser.add_argument('--list-plugins', action='store_true', help='List all available plugins and their descriptions')
    subparsers = parser.add_subparsers(dest="command", required=False)

    # Discover and register all plugins
    plugins = discover_plugins()
    plugin_modules = []
    for modname in plugins:
        try:
            module = importlib.import_module(f"asciidoc_dita.plugins.{modname}")
            module.register_subcommand(subparsers)
            plugin_modules.append(module)
        except Exception as e:
            print(f"Error loading plugin '{modname}': {e}", file=sys.stderr)

    args = parser.parse_args()
    if args.list_plugins:
        print_plugin_list()
        sys.exit(0)
    # Each plugin's register_subcommand sets a 'func' attribute
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
