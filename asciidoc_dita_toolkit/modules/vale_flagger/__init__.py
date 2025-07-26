"""
ValeFlagger Module for AsciiDoc DITA Toolkit.

This module provides DITA compatibility issue detection using Vale linter.
It integrates with the ADT module system to provide consistent CLI access
and workflow orchestration capabilities.
"""

import sys
from typing import Dict, Any

from asciidoc_dita_toolkit.plugins.vale_flagger.cli import main as cli_main

__description__ = "Flag DITA compatibility issues found by Vale linter"
__version__ = "0.1.0"


class ValeFlaggerModule:
    """ValeFlagger module following ADT module architecture."""

    def __init__(self):
        self.name = "ValeFlagger"
        self.description = __description__
        self.version = __version__

    def initialize(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Initialize the module."""
        return {"status": "success", "message": "ValeFlagger initialized"}

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute ValeFlagger with the given context.

        Args:
            context: Execution context with file, directory, and options

        Returns:
            Dictionary with execution results
        """
        # Convert context to CLI arguments
        args = []

        if context.get("file"):
            args.extend(["--path", context["file"]])
        elif context.get("directory"):
            args.extend(["--path", context["directory"]])
        else:
            args.extend(["--path", "."])

        if context.get("verbose"):
            args.append("--verbose")

        # Run in dry-run mode by default for plugin integration
        if not context.get("execute_changes", False):
            args.append("--dry-run")

        # Add rule specifications if provided
        if context.get("enable_rules"):
            rules = context["enable_rules"]
            if isinstance(rules, list):
                rules = ",".join(rules)
            args.extend(["--enable-rules", rules])

        if context.get("disable_rules"):
            rules = context["disable_rules"]
            if isinstance(rules, list):
                rules = ",".join(rules)
            args.extend(["--disable-rules", rules])

        if context.get("config"):
            args.extend(["--config", context["config"]])

        # Execute CLI
        try:
            exit_code = cli_main(args)
            return {
                "status": "success" if exit_code == 0 else "warning",
                "exit_code": exit_code,
                "modified_files": [] if args and "--dry-run" in args else [],
                "message": "ValeFlagger completed successfully" if exit_code == 0 else "ValeFlagger found issues"
            }
        except Exception as e:
            return {
                "status": "error",
                "exit_code": 1,
                "error": str(e),
                "message": f"ValeFlagger failed: {e}"
            }

    def cleanup(self) -> Dict[str, Any]:
        """Cleanup resources (no-op for ValeFlagger)."""
        return {"status": "success", "message": "ValeFlagger cleanup completed"}


def main(args):
    """Main entry point for legacy CLI integration."""
    # Convert args to CLI format
    cli_args = []

    if hasattr(args, 'file') and args.file:
        cli_args.extend(["--path", args.file])
    elif hasattr(args, 'directory') and args.directory:
        cli_args.extend(["--path", args.directory])
    else:
        cli_args.extend(["--path", "."])

    if hasattr(args, 'verbose') and args.verbose:
        cli_args.append("--verbose")

    # Check for rule specifications
    if hasattr(args, 'enable_rules') and args.enable_rules:
        cli_args.extend(["--enable-rules", args.enable_rules])

    if hasattr(args, 'disable_rules') and args.disable_rules:
        cli_args.extend(["--disable-rules", args.disable_rules])

    if hasattr(args, 'config') and args.config:
        cli_args.extend(["--config", args.config])

    # Check if this is a dry run (default for plugin integration)
    if not hasattr(args, 'execute_changes') or not args.execute_changes:
        cli_args.append("--dry-run")

    return cli_main(cli_args)


def register_subcommand(subparsers):
    """Register ValeFlagger as a subcommand."""
    parser = subparsers.add_parser("ValeFlagger", help=__description__)

    # Add standard ADT plugin arguments
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

    # Add ValeFlagger-specific arguments
    parser.add_argument(
        "--enable-rules", "-e",
        help="Comma-separated list of rules to enable"
    )
    parser.add_argument(
        "--disable-rules",
        help="Comma-separated list of rules to disable"
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration file (YAML format)"
    )
    parser.add_argument(
        "--execute-changes",
        action="store_true",
        help="Actually modify files (default is dry-run mode)"
    )

    parser.set_defaults(func=main)