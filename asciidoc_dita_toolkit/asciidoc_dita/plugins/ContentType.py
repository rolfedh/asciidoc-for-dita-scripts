"""
Plugin for the AsciiDoc DITA toolkit: ContentType

This plugin adds a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename.
"""

__description__ = "Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."

# Import version from parent package
from .. import __version__

import os
import re
import sys


class highlighter(object):
    def __init__(self, text):
        self.text = text

    def warn(self):
        return "\033[0;31m" + self.text + "\033[0m"

    def bold(self):
        return "\033[1m" + self.text + "\033[0m"

    def highlight(self):
        return "\033[0;36m" + self.text + "\033[0m"


def editor(filepath, label):
    """
    Check if label exists and add it if missing.

    Returns:
        bool: True if file was modified, False if no changes needed
    """
    try:
        with open(filepath, "r+", encoding="utf-8") as f:
            lines = f.readlines()
            label_exists = False

            for line_content in lines:
                if re.search(
                    "^:_(?:mod-docs-content|content|module)-type:[ \t]+[^ \t]",
                    line_content.strip(),
                ):
                    label_exists = True
                    break

            if label_exists:
                print(f"Skipping {filepath}, label already present")
                return False
            else:
                print(highlighter(f"Editing: Adding content type to {filepath}").bold())
                f.seek(0, 0)
                f.write(f":_mod-docs-content-type: {label}" + "\n")

                # Adds content back
                for line in lines:
                    f.write(line)
                
                # Truncate the file to remove any trailing content from the original file
                f.truncate()
                return True

        # Handle errors gracefully
    except FileNotFoundError:
        print(highlighter(f"Error: File not found: {filepath}").warn())
        return False
    except Exception as e:
        print(highlighter(f"Error: {e}").warn())
        return False


def main(args):
    """
    Main entry point for the ContentType plugin.

    Args:
        args: Parsed command line arguments containing directory option

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    try:
        target_directory = getattr(args, "directory", ".")

        # Validate directory
        if not os.path.exists(target_directory):
            print(
                f"Error: Directory '{target_directory}' does not exist", file=sys.stderr
            )
            return 1

        if not os.path.isdir(target_directory):
            print(f"Error: '{target_directory}' is not a directory", file=sys.stderr)
            return 1

        # Process directory
        result = tree_walker(target_directory)
        files_examined = result["examined"]
        files_modified = result["modified"]
        files_skipped = result["skipped"]

        # Provide comprehensive reporting
        if files_examined == 0:
            print(
                f"No matching AsciiDoc files found in '{target_directory}'",
                file=sys.stderr,
            )
            return 0  # This is not an error condition

        print(f"\nSummary:")
        print(f"  Files examined: {files_examined}")
        print(f"  Files modified: {files_modified}")
        print(f"  Files skipped: {files_skipped}")
        print(
            f"  Files with no matching pattern: {files_examined - files_modified - files_skipped}"
        )

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error processing directory: {e}", file=sys.stderr)
        return 1


def tree_walker(directory):
    """
    Walk through directory and process AsciiDoc files.

    Returns:
        dict: Statistics about file processing
            - examined: Total matching files examined
            - modified: Files that were modified
            - skipped: Files that were skipped (already had labels)
    """
    files_examined = 0
    files_modified = 0
    files_skipped = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith(".") or not file.endswith(".adoc"):
                continue

            filepath = os.path.join(root, file)
            label = None

            if file.startswith("assembly_") or file.startswith("assembly-"):
                label = "ASSEMBLY"
            elif file.startswith("con_") or file.startswith("con-"):
                label = "CONCEPT"
            elif file.startswith("proc_") or file.startswith("proc-"):
                label = "PROCEDURE"
            elif file.startswith("ref_") or file.startswith("ref-"):
                label = "REFERENCE"

            files_examined += 1
            if label:
                was_modified = editor(filepath, label)
                if was_modified:
                    files_modified += 1
                else:
                    files_skipped += 1

    return {
        "examined": files_examined,
        "modified": files_modified,
        "skipped": files_skipped,
    }


def register_subcommand(subparsers):
    """Register this plugin as a subcommand in the main CLI."""
    parser = subparsers.add_parser(
        "ContentType",
        help="Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename.",
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=".",
        help="Location in filesystem to modify asciidoc files.",
    )
    parser.add_argument(
        "--version", action="version", version=f"ContentType {__version__}"
    )
    parser.set_defaults(func=main)
