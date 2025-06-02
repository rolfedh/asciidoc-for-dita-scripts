"""
fix_entity_references.py - Replace unsupported HTML character entity references in .adoc files with AsciiDoc attribute references.

This script scans AsciiDoc (.adoc) files for unsupported HTML character entity references (e.g., &copy;, &ldquo;, &lsaquo;, etc.) and replaces them with the appropriate built-in AsciiDoc attribute references (e.g., {copy}, {ldquo}, {lsaquo}, etc.), according to the Asciidoctor documentation.

Features:
- Supports batch or single-file processing via CLI options.
- Preserves original line endings for each line.
- Ignores symlinks and only processes regular .adoc files.
- Supported XML entities in DITA 1.3 (&amp;, &lt;, &gt;, &apos;, &quot;) are left unchanged.
- All other mapped HTML entities are replaced; unmapped entities trigger a warning and are left unchanged.
- Uses shared utilities from file_utils.py for file discovery, validation, argument parsing, and batch processing.

Usage:
------
# Replace entities in all .adoc files in the current directory:
$ python fix_entity_references.py

# Recursively replace entities in all .adoc files in the current directory and subdirectories:
$ python fix_entity_references.py -r

# Replace entities in a specific .adoc file only:
$ python fix_entity_references.py -f path/to/file.adoc

Options:
--------
-r, --recursive   Search subdirectories recursively for .adoc files.
-f, --file FILE   Scan only the specified .adoc file.

For maintainers:
----------------
- Extend the entity_to_asciidoc mapping as new AsciiDoc attributes are added.
- Use the shared utilities in file_utils.py for consistency and maintainability across scripts.
"""

from file_utils import read_text_preserve_endings, write_text_preserve_endings, common_arg_parser, process_adoc_files
import re

# Supported XML entities in DITA 1.3
supported = {"amp", "lt", "gt", "apos", "quot"}

# Mapping of common HTML entities to AsciiDoc attribute references
entity_to_asciidoc = {
    # XML entities are supported in DITA and left unchanged
    # "amp": "{amp}",        # & (ampersand)
    # "lt": "{lt}",          # < (less-than)
    # "gt": "{gt}",          # > (greater-than)
    # "apos": "{apos}",      # ' (apostrophe)
    # "quot": "{quot}",      # " (quotation mark)
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
    """
    Replace unsupported HTML character entity references in a line with AsciiDoc attribute references.
    Leaves supported XML entities unchanged. Prints a warning for unmapped entities.
    """
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
    """
    Read a file, replace unsupported entities, and write back, preserving original line endings.
    """
    lines = read_text_preserve_endings(filepath)
    new_lines = [(replace_entities(text), ending) for text, ending in lines]
    write_text_preserve_endings(filepath, new_lines)
    print(f"Processed {filepath} (preserved per-line endings)")

def main():
    """
    Parse arguments and process .adoc files as specified by the user.
    """
    parser = common_arg_parser("Replace unsupported HTML character entity references in .adoc files with AsciiDoc attributes.")
    args = parser.parse_args()
    process_adoc_files(args, process_file)

if __name__ == "__main__":
    main()