"""
Plugin for the AsciiDoc DITA toolkit: fix_content_type

This plugin adds a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename.
"""

__description__ = "Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."

import os

ASSE = ":_mod-docs-content-type: ASSEMBLY"
CON  = ":_mod-docs-content-type: CONCEPT"
PROC = ":_mod-docs-content-type: PROCEDURE"
REF  = ":_mod-docs-content-type: REFERENCE"

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
                if label.strip() == line_content.strip():
                    label_exists = True
                    break

            if label_exists:
                print(f"Skipping {filepath}, label '{label}' already present")
            else:
                print(highlighter(f"Editing: Adding {label} to {filepath}").bold())
                f.seek(0, 0)
                f.write(label + "\n")

                # Adds content back
                for line in lines:
                    f.write(line)

        # Handle errors gracefully
    except FileNotFoundError:
        print(highlighter(f"Error: File not found: {filepath}").warn())
    except Exception as e:
        print(highlighter(f"Error: {e}").warn())

def tree_walker(directory):

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith(".") or not file.endswith(".adoc"):
                continue
            filepath = os.path.join(root, file)
            label = None

            if file.startswith("assembly_"):
                label = ASSE        
            elif file.startswith("con_"):
                label = CON
            elif file.startswith("proc_"):
                label = PROC
            elif file.startswith("ref_"):
                label = REF

            if label:
                editor(filepath, label)
            else:
                pass

def main(args):
   target_directory = args.directory
   tree_walker(target_directory)

def register_subcommand(subparsers):
    parser = subparsers.add_parser(
        "fix-content-type",
        help="Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."
    )
    parser.add_argument('-d', '--directory', type=str, default='.', help='Location in filesystem to modify asciidoc files.')
    parser.set_defaults(func=main)

