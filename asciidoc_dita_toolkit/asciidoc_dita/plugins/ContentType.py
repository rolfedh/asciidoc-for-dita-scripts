"""
Plugin for the AsciiDoc DITA toolkit: ContentType

This plugin adds a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename.
"""

__description__ = "Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."

import os
import re
from ..file_utils import process_adoc_files, common_arg_parser


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
    Determine content type based on filename prefix.
    
    Args:
        filename: Name of the file (without path)
        
    Returns:
        Content type string or None if no pattern matches
    """
    prefixes = {
        ('assembly_', 'assembly-'): 'ASSEMBLY',
        ('con_', 'con-'): 'CONCEPT',
        ('proc_', 'proc-'): 'PROCEDURE',
        ('ref_', 'ref-'): 'REFERENCE',
        ('snip_', 'snip-'): 'SNIPPET'
    }
    
    for prefix_group, content_type in prefixes.items():
        if any(filename.startswith(prefix) for prefix in prefix_group):
            return content_type
    
    return None


def add_content_type_label(filepath, label):
    """
    Add a content type label to the beginning of an .adoc file if it doesn't already exist.
    
    Args:
        filepath: Path to the .adoc file
        label: Content type label to add
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
            else:
                print(Highlighter(f"Editing: Adding content type to {filepath}").bold())
                f.seek(0, 0)
                f.write(f":_mod-docs-content-type: {label}\n")
                
                # Add content back
                for line in lines:
                    f.write(line)
                    
    except FileNotFoundError:
        print(Highlighter(f"Error: File not found: {filepath}").warn())
    except Exception as e:
        print(Highlighter(f"Error: {e}").warn())


def label_file(filepath):
    """
    Determine content type based on filename and add the appropriate label.
    
    Args:
        filepath: Path to the .adoc file to process
    """
    filename = os.path.basename(filepath)
    label = get_content_type_from_filename(filename)
    if label:
        add_content_type_label(filepath, label)


def main(args):
    """Main function for the ContentType plugin."""
    process_adoc_files(args, label_file)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser("ContentType", help=__description__)
    common_arg_parser(parser)
    parser.set_defaults(func=main)
