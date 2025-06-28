"""
Plugin for the AsciiDoc DITA toolkit: fix_content_type

This plugin adds a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename.
"""

__description__ = "Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."

import os
import re
from ..file_utils import process_adoc_files, common_arg_parser

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

def label_file(filepath):
    file = os.path.basename(filepath)
    label = None

    if file.startswith("assembly_") or file.startswith("assembly-"):
        label = "ASSEMBLY"
    elif file.startswith("con_") or file.startswith("con-"):
        label = "CONCEPT"
    elif file.startswith("proc_") or file.startswith("proc-"):
        label = "PROCEDURE"
    elif file.startswith("ref_")  or file.startswith("ref-"):
        label = "REFERENCE"
    elif file.startswith("snip_") or file.startswith("snip-"):
        label = "SNIPPET"
    if label:
        editor(filepath, label)

def main(args):
    process_adoc_files(args, label_file)

def register_subcommand(subparsers):
    parser = subparsers.add_parser("ContentType", help=__description__)

    # Use unified argument parser options
    common_arg_parser(parser)
    parser.set_defaults(func=main)
