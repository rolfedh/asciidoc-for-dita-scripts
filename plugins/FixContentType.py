"""
Plugin for the AsciiDoc DITA toolkit: FixContentType

This plugin adds a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename.

See:
- https://github.com/jhradilek/asciidoctor-dita-vale/blob/main/styles/AsciiDocDITA/ContentType.yml
- https://github.com/jhradilek/asciidoctor-dita-vale/tree/main/fixtures/ContentType
"""

__description__ = "Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."

import os

ASSE = ":_mod-docs-content-type: ASSEMBLY"
CON  = ":_mod-docs-content-type: CONCEPT"
PROC = ":_mod-docs-content-type: PROCEDURE"
REF  = ":_mod-docs-content-type: REFERENCE"

def highlight(text, style="bold"):
    styles = {
        "warn": '\033[0;31m',
        "bold": '\033[1m',
        "highlight": '\033[0;36m',
        "end": '\033[0m',
    }
    return f"{styles.get(style, '')}{text}{styles['end']}"

def add_label_if_missing(filepath, label):
    """Add the label to the file if not already present."""
    try:
        with open(filepath, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            if any(label.strip() == line.strip() for line in lines):
                print(f"Skipping {filepath}, label '{label}' already present")
                return
            print(highlight(f"Editing: Adding {label} to {filepath}", "bold"))
            f.seek(0, 0)
            f.write(label + "\n")
            for line in lines:
                f.write(line)
    except FileNotFoundError:
        print(highlight(f"Error: File not found: {filepath}", "warn"))
    except Exception as e:
        print(highlight(f"Error: {e}", "warn"))

def process_directory(directory):
    """Walk the directory and add content type labels based on filename patterns."""
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
                add_label_if_missing(filepath, label)

def main(args):
    process_directory(args.directory)

def register_subcommand(subparsers):
    parser = subparsers.add_parser(
        "fix-content-type",
        help="Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."
    )
    parser.add_argument('-d', '--directory', type=str, default='.', help='Location in filesystem to modify asciidoc files.')
    parser.set_defaults(func=main)

