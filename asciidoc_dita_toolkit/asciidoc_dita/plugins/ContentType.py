"""
Plugin for the AsciiDoc DITA toolkit: ContentType

This plugin adds a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename.
"""

__description__ = "Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."

import os
import re
import sys

from ..file_utils import common_arg_parser, process_adoc_files, read_text_preserve_endings, write_text_preserve_endings


class Highlighter:
    """Simple text highlighter for console output."""

    def __init__(self, text):
        self.text = text

    def warn(self):
        return f"\033[0;31m{self.text}\033[0m"

    def bold(self):
        return f"\033[1m{self.text}\033[0m"

    def highlight(self):
        return f"\033[0;36m{self.text}\033[0m"

    def success(self):
        return f"\033[0;32m{self.text}\033[0m"


def get_content_type_from_filename(filename):
    """
    Determine content type based on filename prefix.

    Args:
        filename: Name of the file (without path)

    Returns:
        Content type string or None if no pattern matches
    """
    prefixes = {
        ("assembly_", "assembly-"): "ASSEMBLY",
        ("con_", "con-"): "CONCEPT",
        ("proc_", "proc-"): "PROCEDURE",
        ("ref_", "ref-"): "REFERENCE",
        ("snip_", "snip-"): "SNIPPET",
    }

    for prefix_group, content_type in prefixes.items():
        if any(filename.startswith(prefix) for prefix in prefix_group):
            return content_type
    return None


def detect_existing_content_type(lines):
    """
    Detect existing content type attributes in file.

    Args:
        lines: List of (text, ending) tuples from file

    Returns:
        tuple: (content_type, line_index, attribute_type) or (None, None, None)
        attribute_type: 'current', 'deprecated_content', 'deprecated_module'
    """
    for i, (text, _) in enumerate(lines):
        stripped = text.strip()
        
        # Current format
        if stripped.startswith(":_mod-docs-content-type:"):
            value = stripped.split(":", 2)[-1].strip()
            return (value, i, 'current')
        
        # Deprecated formats
        if stripped.startswith(":_content-type:"):
            value = stripped.split(":", 2)[-1].strip()
            return (value, i, 'deprecated_content')
            
        if stripped.startswith(":_module-type:"):
            value = stripped.split(":", 2)[-1].strip()
            return (value, i, 'deprecated_module')
    
    return (None, None, None)


def prompt_user_for_content_type():
    """
    Prompt user to select content type interactively.

    Returns:
        Selected content type string or None if skipped
    """
    options = [
        "ASSEMBLY",
        "CONCEPT", 
        "PROCEDURE",
        "REFERENCE",
        "SNIPPET",
        "TBD"
    ]
    
    print("\nNo content type detected. Please select:")
    for i, option in enumerate(options, 1):
        print(f"[{i}] {option}")
    print("[7] Skip this file")
    
    while True:
        try:
            choice = input("Choice (1-7): ").strip()
            if choice == "7":
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= 6:
                return options[choice_num - 1]
            else:
                print("Please enter a number between 1 and 7.")
        except (ValueError, KeyboardInterrupt):
            print("\nOperation cancelled.")
            sys.exit(0)
        except EOFError:
            print("\nOperation cancelled.")
            sys.exit(0)


def process_content_type_file(filepath):
    """
    Process a single file for content type attributes.

    Args:
        filepath: Path to the .adoc file to process
    """
    filename = os.path.basename(filepath)
    print(f"\nChecking {Highlighter(filename).bold()}...")
    
    try:
        lines = read_text_preserve_endings(filepath)
        content_type, line_index, attr_type = detect_existing_content_type(lines)
        
        # Handle existing content types
        if content_type:
            if attr_type == 'current':
                if content_type:
                    print(f"  ✓ Content type already set: {Highlighter(content_type).success()}")
                else:
                    print(f"  ⚠️  Empty content type attribute found")
                    content_type = prompt_user_for_content_type()
                    if content_type:
                        # Replace empty attribute
                        lines[line_index] = (f":_mod-docs-content-type: {content_type}", lines[line_index][1])
                        write_text_preserve_endings(filepath, lines)
                        print(f"  ✓ Updated to: {Highlighter(content_type).success()}")
                print("=" * 40)
                return
                
            elif attr_type in ['deprecated_content', 'deprecated_module']:
                old_attr = ":_content-type:" if attr_type == 'deprecated_content' else ":_module-type:"
                print(f"  ⚠️  Deprecated attribute detected: {Highlighter(f'{old_attr} {content_type}').warn()}")
                
                if content_type:
                    # Replace deprecated attribute
                    lines[line_index] = (f":_mod-docs-content-type: {content_type}", lines[line_index][1])
                    write_text_preserve_endings(filepath, lines)
                    print(f"  ✓ Converted to: {Highlighter(f':_mod-docs-content-type: {content_type}').success()}")
                else:
                    print(f"  ⚠️  Empty deprecated attribute found")
                    content_type = prompt_user_for_content_type()
                    if content_type:
                        lines[line_index] = (f":_mod-docs-content-type: {content_type}", lines[line_index][1])
                        write_text_preserve_endings(filepath, lines)
                        print(f"  ✓ Updated to: {Highlighter(content_type).success()}")
                print("=" * 40)
                return
        
        # Try filename-based detection
        filename_content_type = get_content_type_from_filename(filename)
        if filename_content_type:
            print(f"  💡 Detected from filename: {Highlighter(filename_content_type).highlight()}")
            # Add content type at the beginning
            lines.insert(0, (f":_mod-docs-content-type: {filename_content_type}", "\n"))
            write_text_preserve_endings(filepath, lines)
            print(f"  ✓ Added content type: {Highlighter(filename_content_type).success()}")
            print("=" * 40)
            return
        
        # No detection possible, prompt user
        content_type = prompt_user_for_content_type()
        if content_type:
            lines.insert(0, (f":_mod-docs-content-type: {content_type}", "\n"))
            write_text_preserve_endings(filepath, lines)
            print(f"  ✓ Added content type: {Highlighter(content_type).success()}")
        else:
            print(f"  → Skipped")
        print("=" * 40)

    except FileNotFoundError:
        print(f"  ❌ Error: File not found: {filepath}")
        print("=" * 40)
    except Exception as e:
        print(f"  ❌ Error: {e}")
        print("=" * 40)


def main(args):
    """Main function for the ContentType plugin."""
    process_adoc_files(args, process_content_type_file)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser("ContentType", help=__description__)
    common_arg_parser(parser)
    parser.set_defaults(func=main)
