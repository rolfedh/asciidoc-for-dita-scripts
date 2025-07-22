"""
ValeFlagger Plugin for AsciiDoc DITA Toolkit.

This module integrates Vale linter with AsciiDoc files for DITA compatibility checking.
"""

import sys
from typing import Dict, Any

from .cli import main as cli_main

__description__ = "Check AsciiDoc files for DITA compatibility issues using Vale linter"


class ValeFlaggerModule:
    """ValeFlagger plugin module following ADT plugin architecture."""

    def __init__(self):
        self.name = "ValeFlagger"
        self.description = __description__

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

        if context.get("verbose"):
            args.append("--verbose")

        # Always run in dry-run mode when called as a plugin
        # to avoid modifying files without explicit user consent
        args.append("--dry-run")

        # Execute CLI
        try:
            exit_code = cli_main(args)
            return {
                "success": exit_code == 0,
                "exit_code": exit_code,
                "modified_files": [],  # Dry run doesn't modify files
                "message": "ValeFlagger completed successfully" if exit_code == 0 else "ValeFlagger found issues"
            }
        except Exception as e:
            return {
                "success": False,
                "exit_code": 1,
                "error": str(e),
                "message": f"ValeFlagger failed: {e}"
            }

    def cleanup(self):
        """Cleanup resources (no-op for ValeFlagger)."""
        pass


def main(args):
    """Main entry point for legacy CLI integration."""
    # Convert args to CLI format
    cli_args = []

    if hasattr(args, 'file') and args.file:
        cli_args.extend(["--path", args.file])
    elif hasattr(args, 'directory') and args.directory:
        cli_args.extend(["--path", args.directory])

    if hasattr(args, 'verbose') and args.verbose:
        cli_args.append("--verbose")

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
