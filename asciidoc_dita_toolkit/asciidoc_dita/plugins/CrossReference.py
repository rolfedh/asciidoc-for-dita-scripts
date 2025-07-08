"""
Plugin for the AsciiDoc DITA toolkit: CrossReference

Validate and fix cross-references in AsciiDoc files.
This plugin ensures that cross-references follow proper AsciiDoc syntax
and are compatible with DITA output requirements.

See: 
- https://github.com/jhradilek/asciidoctor-dita-vale/blob/main/styles/AsciiDocDITA/CrossReference.yml
- https://github.com/jhradilek/asciidoctor-dita-vale/tree/main/fixtures/CrossReference
"""

__description__ = "Validate and fix cross-references in AsciiDoc files"

import re
from ..file_utils import (common_arg_parser, process_adoc_files,
                          read_text_preserve_endings,
                          write_text_preserve_endings)

# Pattern to match cross-references
XREF_PATTERN = re.compile(r'xref:([^[\]]+)(?:\[([^\]]*)\])?')
INTERNAL_XREF_PATTERN = re.compile(r'<<([^,>]+)(?:,([^>]*))?>>')

# Valid file extensions for cross-references
VALID_EXTENSIONS = {'.adoc', '.asciidoc'}

# Valid ID pattern (letters, numbers, hyphens, underscores, dots)
VALID_ID_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')


def validate_cross_reference(ref_target, ref_text=None):
    """
    Validate a cross-reference.
    
    Args:
        ref_target: The target of the cross-reference
        ref_text: Optional text for the cross-reference
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Empty target
    if not ref_target.strip():
        return False, "Empty cross-reference target"
    
    # Check if it's a file reference
    if '/' in ref_target or ref_target.endswith('.adoc'):
        # File reference - check for valid path structure
        if ref_target.endswith('.adoc'):
            # Valid file reference
            return True, None
        else:
            # Could be a path without extension
            return True, None
    
    # Internal reference - check ID format
    if '#' in ref_target:
        # Split anchor from file
        parts = ref_target.split('#')
        if len(parts) == 2:
            file_part, anchor_part = parts
            if file_part and not file_part.endswith('.adoc'):
                return False, f"File reference should end with .adoc: {file_part}"
            if not VALID_ID_PATTERN.match(anchor_part):
                return False, f"Invalid anchor ID format: {anchor_part}"
        return True, None
    
    # Simple ID reference
    if VALID_ID_PATTERN.match(ref_target):
        return True, None
    
    return False, f"Invalid cross-reference format: {ref_target}"


def transform_line(line):
    """
    Validate cross-references in a line.
    
    Args:
        line: Input line to process
        
    Returns:
        Transformed line (currently just validates and warns)
    """
    # Find xref: style references
    for match in XREF_PATTERN.finditer(line):
        ref_target = match.group(1)
        ref_text = match.group(2) if match.group(2) else None
        
        is_valid, error_msg = validate_cross_reference(ref_target, ref_text)
        if not is_valid:
            print(f"Warning: {error_msg} in: {line.strip()}")
    
    # Find << >> style references
    for match in INTERNAL_XREF_PATTERN.finditer(line):
        ref_target = match.group(1)
        ref_text = match.group(2) if match.group(2) else None
        
        is_valid, error_msg = validate_cross_reference(ref_target, ref_text)
        if not is_valid:
            print(f"Warning: {error_msg} in: {line.strip()}")
    
    # For now, just return the line as-is (validation only)
    # Future enhancement: could fix common issues
    return line


def process_file(filepath):
    """
    Process a single .adoc file, validating cross-references.
    
    Args:
        filepath: Path to the file to process
    """
    try:
        lines = read_text_preserve_endings(filepath)
        new_lines = []
        
        in_comment_block = False
        
        for text, ending in lines:
            stripped = text.strip()
            
            # Track comment blocks
            if stripped == "////":
                in_comment_block = not in_comment_block
                new_lines.append((text, ending))
                continue
            
            # Skip processing if in comment block or single-line comment
            if in_comment_block or stripped.startswith("//"):
                new_lines.append((text, ending))
                continue
            
            # Process the line
            transformed_text = transform_line(text)
            new_lines.append((transformed_text, ending))

        write_text_preserve_endings(filepath, new_lines)
        print(f"Processed {filepath} (preserved per-line endings)")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")


def main(args):
    """Main function for the CrossReference plugin."""
    process_adoc_files(args, process_file)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser("CrossReference", help=__description__)
    common_arg_parser(parser)
    parser.set_defaults(func=main)
