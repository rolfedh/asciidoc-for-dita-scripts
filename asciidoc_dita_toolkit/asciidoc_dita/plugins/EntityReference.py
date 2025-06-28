"""
Plugin for the AsciiDoc DITA toolkit: EntityReference

This plugin replaces unsupported HTML character entity references in .adoc files with AsciiDoc attribute references.

See: 
- https://github.com/jhradilek/asciidoctor-dita-vale/blob/main/styles/AsciiDocDITA/EntityReference.yml
- https://github.com/jhradilek/asciidoctor-dita-vale/tree/main/fixtures/EntityReference
"""
__description__ = "Replace unsupported HTML character entity references in .adoc files with AsciiDoc attribute references."

import re
from ..file_utils import read_text_preserve_endings, write_text_preserve_endings, process_adoc_files

# Supported XML entities in DITA 1.3 (these should not be replaced)
SUPPORTED_ENTITIES = {"amp", "lt", "gt", "apos", "quot"}

# Mapping of common HTML entities to AsciiDoc attribute references
ENTITY_TO_ASCIIDOC = {
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
    def repl(match):
        entity = match.group(1)
        if entity in SUPPORTED_ENTITIES:
            return match.group(0)
        elif entity in ENTITY_TO_ASCIIDOC:
            return ENTITY_TO_ASCIIDOC[entity]
        else:
            print(f"Warning: No AsciiDoc attribute for &{entity};")
            return match.group(0)
    return entity_pattern.sub(repl, line)

def process_file(filepath):
    try:
        lines = read_text_preserve_endings(filepath)
        new_lines = [(replace_entities(text), ending) for text, ending in lines]
        write_text_preserve_endings(filepath, new_lines)
        print(f"Processed {filepath} (preserved per-line endings)")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main(args):
    process_adoc_files(args, process_file)

def register_subcommand(subparsers):
    parser = subparsers.add_parser(
        "EntityReference",
        help="Replace unsupported HTML character entity references in .adoc files with AsciiDoc attribute references."
    )
    parser.add_argument('-d', '--directory', type=str, default='.', 
                       help='Root directory to search (default: current directory)')
    parser.add_argument('-r', '--recursive', action='store_true', 
                       help='Search subdirectories recursively')
    parser.add_argument('-f', '--file', type=str, 
                       help='Scan only the specified .adoc file')
    parser.set_defaults(func=main)
