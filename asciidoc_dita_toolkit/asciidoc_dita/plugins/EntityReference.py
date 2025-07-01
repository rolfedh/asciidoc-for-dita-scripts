"""
Plugin for the AsciiDoc DITA toolkit: EntityReference

This plugin replaces unsupported HTML character entity references in .adoc files with AsciiDoc attribute references.

See: 
- https://github.com/jhradilek/asciidoctor-dita-vale/blob/main/styles/AsciiDocDITA/EntityReference.yml
- https://github.com/jhradilek/asciidoctor-dita-vale/tree/main/fixtures/EntityReference
"""

__description__ = "Replace unsupported HTML character entity references in .adoc files with AsciiDoc attribute references."

import re

from ..file_utils import (common_arg_parser, process_adoc_files,
                          read_text_preserve_endings,
                          write_text_preserve_endings)

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
    "bull": "{bull}",  # • (bullet)
    "copy": "{copy}",  # © (copyright sign)
    "deg": "{deg}",  # ° (degree sign)
    "Dagger": "{Dagger}",  # ‡ (double dagger)
    "dagger": "{dagger}",  # † (dagger)
    "hellip": "{hellip}",  # … (ellipsis)
    "laquo": "{laquo}",  # « (left-pointing double angle quotation mark)
    "ldquo": "{ldquo}",  # “ (left double quotation mark)
    "lsquo": "{lsquo}",  # ‘ (left single quotation mark)
    "lsaquo": "{lsaquo}",  # ‹ (single left-pointing angle quotation mark)
    "mdash": "{mdash}",  # — (em dash)
    "middot": "{middot}",  # · (middle dot)
    "ndash": "{ndash}",  # – (en dash)
    "num": "{num}",  # # (number sign)
    "para": "{para}",  # ¶ (pilcrow/paragraph sign)
    "plus": "{plus}",  # + (plus sign)
    "pound": "{pound}",  # £ (pound sign)
    "quot": "{quot}",  # " (quotation mark)
    "raquo": "{raquo}",  # » (right-pointing double angle quotation mark)
    "rdquo": "{rdquo}",  # " (right double quotation mark)
    "reg": "{reg}",  # ® (registered sign)
    "rsquo": "{rsquo}",  # ’ (right single quotation mark)
    "rsaquo": "{rsaquo}",  # › (single right-pointing angle quotation mark)
    "sect": "{sect}",  # § (section sign)
    "sbquo": "{sbquo}",  # ‚ (single low-9 quotation mark)
    "bdquo": "{bdquo}",  # „ (double low-9 quotation mark)
    "trade": "{trade}",  # ™ (trademark sign)
}

ENTITY_PATTERN = re.compile(r"&([a-zA-Z0-9]+);")


def replace_entities(line):
    """
    Replace HTML entity references with AsciiDoc attribute references.

    Args:
        line: Input line to process

    Returns:
        Line with entity references replaced
    """

    def repl(match):
        entity = match.group(1)
        if entity in SUPPORTED_ENTITIES:
            return match.group(0)
        elif entity in ENTITY_TO_ASCIIDOC:
            return ENTITY_TO_ASCIIDOC[entity]
        else:
            print(f"Warning: No AsciiDoc attribute for &{entity};")
            return match.group(0)

    return ENTITY_PATTERN.sub(repl, line)


def process_file(filepath):
    """
    Process a single .adoc file, replacing entity references.
    Skip entities within comments (single-line // and block comments ////).

    Args:
        filepath: Path to the file to process
    """
    try:
        lines = read_text_preserve_endings(filepath)
        new_lines = []
        in_block_comment = False

        for text, ending in lines:
            stripped = text.strip()

            # Check for block comment delimiters
            if stripped == "////":
                in_block_comment = not in_block_comment
                new_lines.append((text, ending))
                continue

            # Skip processing if we're in a block comment or it's a single-line comment
            if in_block_comment or stripped.startswith("//"):
                new_lines.append((text, ending))
            else:
                new_lines.append((replace_entities(text), ending))

        write_text_preserve_endings(filepath, new_lines)
        print(f"Processed {filepath} (preserved per-line endings)")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")


def main(args):
    """Main function for the EntityReference plugin."""
    process_adoc_files(args, process_file)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser("EntityReference", help=__description__)
    common_arg_parser(parser)
    parser.set_defaults(func=main)
