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

import os
import re
import argparse

# Supported XML entities in DITA 1.3
supported = {"amp", "lt", "gt", "apos", "quot"}

# Mapping of common HTML entities to AsciiDoc attribute references
entity_to_asciidoc = {
    "copy": "{copy}",      # ©
    "reg": "{reg}",        # ®
    "trade": "{trade}",    # ™
    "mdash": "{mdash}",    # —
    "ndash": "{ndash}",    # –
    "hellip": "{hellip}",  # …
    "lsquo": "{lsquo}",    # ‘
    "rsquo": "{rsquo}",    # ’
    "ldquo": "{ldquo}",    # “
    "rdquo": "{rdquo}",    # ”
    "deg": "{deg}",        # °
    "plus": "{plus}",      # +
    "brvbar": "{brvbar}",  # ¦
    "sect": "{sect}",      # §
    "para": "{para}",      # ¶
    "middot": "{middot}",  # ·
    "bull": "{bull}",      # •
    "laquo": "{laquo}",    # «
    "raquo": "{raquo}",    # »
    "lsquo": "{lsquo}",    # ‘
    "rsquo": "{rsquo}",    # ’
    "sbquo": "{sbquo}",    # ‚
    "bdquo": "{bdquo}",    # „
    "dagger": "{dagger}",  # †
    "Dagger": "{Dagger}",  # ‡
    # Add more as needed from the Asciidoctor docs
}

entity_pattern = re.compile(r"&([a-zA-Z0-9]+);")

# Regex to split lines and preserve their original line endings
line_splitter = re.compile(rb'(.*?)(\r\n|\r|\n|$)')

def replace_entities(line):
    # Replace all occurrences, even if adjacent to markup or underscores
    def repl(match):
        entity = match.group(1)
        if entity in supported:
            return match.group(0)
        elif entity in entity_to_asciidoc:
            return entity_to_asciidoc[entity]
        else:
            print(f"Warning: No AsciiDoc attribute for &{entity};")
            return match.group(0)
    # Use re.sub with overlapped matches if needed
    return entity_pattern.sub(repl, line)

def process_file(filepath):
    # Read file as bytes to preserve all line endings
    with open(filepath, 'rb') as f:
        content = f.read()
    # Split into lines, preserving line endings
    lines = []
    for match in line_splitter.finditer(content):
        text = match.group(1).decode('utf-8')
        ending = match.group(2).decode('utf-8') if match.group(2) else ''
        replaced = replace_entities(text)
        lines.append(replaced + ending)
        if not ending:
            break
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        f.writelines(lines)
    print(f"Processed {filepath} (preserved per-line endings)")

def find_adoc_files(root, recursive):
    adoc_files = []
    if recursive:
        for dirpath, dirnames, filenames in os.walk(root):
            for filename in filenames:
                if filename.endswith('.adoc'):
                    fullpath = os.path.join(dirpath, filename)
                    if not os.path.islink(fullpath):
                        adoc_files.append(fullpath)
    else:
        for filename in os.listdir(root):
            if filename.endswith('.adoc'):
                fullpath = os.path.join(root, filename)
                if not os.path.islink(fullpath):
                    adoc_files.append(fullpath)
    return adoc_files

def main():
    parser = argparse.ArgumentParser(description="Replace unsupported HTML character entity references in .adoc files with AsciiDoc attributes.")
    parser.add_argument('-r', '--recursive', action='store_true', help='Search subdirectories recursively')
    parser.add_argument('-f', '--file', type=str, help='Scan only the specified .adoc file')
    args = parser.parse_args()

    if args.file:
        if os.path.isfile(args.file) and args.file.endswith('.adoc') and not os.path.islink(args.file):
            process_file(args.file)
        else:
            print(f"Error: {args.file} is not a valid .adoc file or is a symlink.")
    else:
        adoc_files = find_adoc_files('.', args.recursive)
        for filepath in adoc_files:
            process_file(filepath)

if __name__ == "__main__":
    main()