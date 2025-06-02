"""
fix_entity_references.py - Replace unsupported HTML character entity references in .adoc files with AsciiDoc attribute references.

USAGE:
------
# Replace entities in all .adoc files in the current directory:
$ python fix_entity_references.py

# Recursively replace entities in all .adoc files in the current directory and subdirectories:
$ python fix_entity_references.py -r

# Replace entities in a specific .adoc file only:
$ python fix_entity_references.py -f path/to/file.adoc

OPTIONS:
--------
-r, --recursive   Search subdirectories recursively for .adoc files.
-f, --file FILE   Scan only the specified .adoc file.

DESCRIPTION:
------------
This script scans AsciiDoc (.adoc) files for unsupported HTML character entity references (such as &copy;, &ldquo;, &lsaquo;, etc.) and replaces them with the appropriate built-in AsciiDoc attribute references (such as {copy}, {ldquo}, {lsaquo}, etc.), according to the Asciidoctor documentation.

- Supported XML entities in DITA 1.3 (&amp;, &lt;, &gt;, &apos;, &quot;) are left unchanged.
- All other mapped HTML entities are replaced.
- If an entity is not mapped, a warning is printed and the entity is left unchanged.
- The script preserves the original line endings for each line.
"""

import argparse
from file_utils import find_adoc_files, read_text_preserve_endings, write_text_preserve_endings, common_arg_parser, process_adoc_files
import re

# Supported XML entities in DITA 1.3
supported = {"amp", "lt", "gt", "apos", "quot"}

# Mapping of common HTML entities to AsciiDoc attribute references
entity_to_asciidoc = {
    "amp": "{amp}",        # & (ampersand)
    "lt": "{lt}",          # < (less-than)
    "gt": "{gt}",          # > (greater-than)
    "apos": "{apos}",      # ' (apostrophe)
    "quot": "{quot}",      # " (quotation mark)
    "brvbar": "{brvbar}",  # ¦ (broken bar)
    "bull": "{bull}",      # • (bullet)
    "copy": "{copy}",      # © (copyright sign)
    "deg": "{deg}",        # ° (degree sign)
    "Dagger": "{Dagger}",  # ‡ (double dagger)
    "dagger": "{dagger}",  # † (dagger)
    "hellip": "{hellip}",  # … (ellipsis)
    "laquo": "{laquo}",    # « (left-pointing double angle quotation mark)
    "ldquo": "{ldquo}",    # “ (left double quotation mark)
    "lsquo": "{lsquo}",    # ‘ (left single quotation mark)
    "lsaquo": "{lsaquo}",  # ‹ (single left-pointing angle quotation mark)
    "mdash": "{mdash}",    # — (em dash)
    "middot": "{middot}",  # · (middle dot)
    "ndash": "{ndash}",    # – (en dash)
    "num": "{num}",        # # (number sign)
    "para": "{para}",      # ¶ (pilcrow/paragraph sign)
    "plus": "{plus}",      # + (plus sign)
    "pound": "{pound}",    # £ (pound sign)
    "quot": "{quot}",      # " (quotation mark)
    "raquo": "{raquo}",    # » (right-pointing double angle quotation mark)
    "reg": "{reg}",        # ® (registered sign)
    "rsquo": "{rsquo}",    # ’ (right single quotation mark)
    "rsaquo": "{rsaquo}",  # › (single right-pointing angle quotation mark)
    "sect": "{sect}",      # § (section sign)
    "sbquo": "{sbquo}",    # ‚ (single low-9 quotation mark)
    "bdquo": "{bdquo}",    # „ (double low-9 quotation mark)
    "trade": "{trade}",    # ™ (trademark sign)
}

entity_pattern = re.compile(r"&([a-zA-Z0-9]+);")

def replace_entities(line):
    def repl(match):
        entity = match.group(1)
        if entity in supported:
            return match.group(0)
        elif entity in entity_to_asciidoc:
            return entity_to_asciidoc[entity]
        else:
            print(f"Warning: No AsciiDoc attribute for &{entity};")
            return match.group(0)
    return entity_pattern.sub(repl, line)

def process_file(filepath):
    # Read file as text, preserving line endings
    lines = read_text_preserve_endings(filepath)
    new_lines = [(replace_entities(text), ending) for text, ending in lines]
    write_text_preserve_endings(filepath, new_lines)
    print(f"Processed {filepath} (preserved per-line endings)")

def main():
    parser = common_arg_parser("Replace unsupported HTML character entity references in .adoc files with AsciiDoc attributes.")
    args = parser.parse_args()

    if args.file:
        import os
        if os.path.isfile(args.file) and args.file.endswith('.adoc') and not os.path.islink(args.file):
            process_file(args.file)
        else:
            print(f"Error: {args.file} is not a valid .adoc file or is a symlink.")
    else:
        adoc_files = find_adoc_files('.', args.recursive)
        for filepath in adoc_files:
            process_file(filepath)
    process_adoc_files(args, process_file)

if __name__ == "__main__":
    main()