"""
Plugin for the AsciiDoc DITA toolkit: fix_content_type

This plugin adds a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename.
"""

__description__ = "Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."

import os
import re


class Highlighter:
    """Simple text highlighter for console output."""
    
    def __init__(self, text):
        self.text = text
    
    def warn(self):
        return f'\033[0;31m{self.text}\033[0m'
    
    def bold(self):
        return f'\033[1m{self.text}\033[0m'
    
    def highlight(self):
        return f'\033[0;36m{self.text}\033[0m'


def get_content_type_from_filename(filename):
    """
    Determine the content type based on file prefix.
    Returns the content type label or None if no match.
    """
    if filename.startswith(("assembly_", "assembly-")):
        return "ASSEMBLY"
    elif filename.startswith(("con_", "con-")):
        return "CONCEPT"
    elif filename.startswith(("proc_", "proc-")):
        return "PROCEDURE"
    elif filename.startswith(("ref_", "ref-")):
        return "REFERENCE"
    return None


def add_content_type_label(filepath, label):
    """
    Add a content type label to the file if it doesn't already exist.
    """
    try:
        with open(filepath, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            
            # Check if label already exists
            label_exists = any(
                re.search(r'^:_(?:mod-docs-content|content|module)-type:[ \t]+[^ \t]', line.strip())
                for line in lines
            )
            
            if label_exists:
                print(f"Skipping {filepath}, label already present")
                return
            
            print(Highlighter(f"Editing: Adding content type to {filepath}").bold())
            
            # Write the new label at the beginning
            f.seek(0, 0)
            f.write(f":_mod-docs-content-type: {label}\n")
            
            # Write back the original content
            for line in lines:
                f.write(line)
                
    except FileNotFoundError:
        print(Highlighter(f"Error: File not found: {filepath}").warn())
    except Exception as e:
        print(Highlighter(f"Error: {e}").warn())


def main(args):
    """Main function for the ContentType plugin."""
    from ..file_utils import process_adoc_files
    
    def label_file(filepath):
        filename = os.path.basename(filepath)
        label = get_content_type_from_filename(filename)
        if label:
            add_content_type_label(filepath, label)
    
    process_adoc_files(args, label_file)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser(
        "ContentType",
        help="Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."
    )
    parser.add_argument('-d', '--directory', type=str, default='.', 
                       help='Root directory to search (default: current directory)')
    parser.add_argument('-r', '--recursive', action='store_true', 
                       help='Search subdirectories recursively')
    parser.add_argument('-f', '--file', type=str, 
                       help='Scan only the specified .adoc file')
    parser.set_defaults(func=main)
