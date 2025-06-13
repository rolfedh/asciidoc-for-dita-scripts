"""
Plugin for the AsciiDoc DITA toolkit: ContentType

This plugin adds a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename.
"""

__description__ = "Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."
__version__ = "1.0.0"

import os
import re
import sys

class highlighter(object):
    def __init__(self, text):
       self.text = text
    def warn(self):
        return('\033[0;31m' + self.text + '\033[0m')
    def bold(self):
        return('\033[1m' + self.text + '\033[0m')
    def highlight(self):                                                                                                                                                                                    
        return('\033[0;36m' + self.text + '\033[0m')

def editor(filepath, label):
    # If the label does not exist, the editor adds it.
    try:
        with open(filepath, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            label_exists = False

            for line_content in lines:
                if re.search('^:_(?:mod-docs-content|content|module)-type:[ \t]+[^ \t]', line_content.strip()):
                    label_exists = True
                    break

            if label_exists:
                print(f"Skipping {filepath}, label already present")
            else:
                print(highlighter(f"Editing: Adding content type to {filepath}").bold())
                f.seek(0, 0)
                f.write(f":_mod-docs-content-type: {label}" + "\n")

                # Adds content back
                for line in lines:
                    f.write(line)

        # Handle errors gracefully
    except FileNotFoundError:
        print(highlighter(f"Error: File not found: {filepath}").warn())
    except Exception as e:
        print(highlighter(f"Error: {e}").warn())

def main(args):
    """
    Main entry point for the ContentType plugin.
    
    Args:
        args: Parsed command line arguments containing directory option
        
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    try:
        target_directory = getattr(args, 'directory', '.')
        
        # Validate directory
        if not os.path.exists(target_directory):
            print(f"Error: Directory '{target_directory}' does not exist", file=sys.stderr)
            return 1
        
        if not os.path.isdir(target_directory):
            print(f"Error: '{target_directory}' is not a directory", file=sys.stderr)
            return 1
        
        # Process directory
        files_processed = tree_walker(target_directory)
        
        if files_processed == 0:
            print(f"No matching AsciiDoc files found in '{target_directory}'", file=sys.stderr)
            return 0  # This is not an error condition
            
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
        int: Number of files processed
    """
    files_processed = 0

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

            elif file.startswith("ref_")  or file.startswith("ref-"):
                label = "REFERENCE"

            if label:
                editor(filepath, label)
                files_processed += 1
            else:
                pass
    
    return files_processed


def run_cli():
    """
    Standalone CLI runner for this plugin.
    Can be used when running the plugin directly.
    """
    import argparse
    parser = argparse.ArgumentParser(
        description=__description__,
        prog="ContentType"
    )
    parser.add_argument('-d', '--directory', type=str, default='.', help='Location in filesystem to modify asciidoc files.')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    sys.exit(main(args))


def register_subcommand(subparsers):
    """Register this plugin as a subcommand in the main CLI."""
    parser = subparsers.add_parser(
        "ContentType",
        help="Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."
    )
    parser.add_argument('-d', '--directory', type=str, default='.', help='Location in filesystem to modify asciidoc files.')
    parser.add_argument('--version', action='version', version=f'ContentType {__version__}')
    parser.set_defaults(func=main)


if __name__ == "__main__":
    run_cli()
