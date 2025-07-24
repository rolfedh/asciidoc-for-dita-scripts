"""
ValeFlagger Plugin for AsciiDoc DITA Toolkit.

This module integrates Vale linter with AsciiDoc files for DITA compatibility checking.
"""

import sys
from typing import Dict, Any

from ...adt_core.module_sequencer import ADTModule
from .cli import main as cli_main
from .vale_flagger import ValeFlagger

__description__ = "Flag DITA compatibility issues found by Vale"


class ValeFlaggerModule(ADTModule):
    """ValeFlagger plugin module following ADT plugin architecture."""

    @property
    def name(self) -> str:
        """Module name identifier."""
        return "ValeFlagger"

    @property
    def version(self) -> str:
        """Module version."""
        return "0.1.0"

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the ValeFlagger module with configuration."""
        self._initialized = True
        # Initialize any additional configuration if needed

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ValeFlagger processing on files in the given context."""
        try:
            # Extract files to process from context
            files = context.get('files', [])
            if not files:
                return {
                    "status": "warning",
                    "message": "No files provided for ValeFlagger processing"
                }

            # Create a ValeFlagger instance
            vale_flagger = ValeFlagger()

            # Process the files
            total_modified = 0
            for file_path in files:
                result = vale_flagger.process_file(file_path, dry_run=False)
                if result.get("status") == "success":
                    total_modified += len(result.get("modified_files", []))

            return {
                "status": "success",
                "exit_code": 0,
                "modified_files_count": total_modified,
                "message": f"ValeFlagger processed {len(files)} files, modified {total_modified}"
            }

        except Exception as e:
            return {
                "status": "error",
                "exit_code": 1,
                "error": str(e),
                "message": f"ValeFlagger execution failed: {e}"
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
