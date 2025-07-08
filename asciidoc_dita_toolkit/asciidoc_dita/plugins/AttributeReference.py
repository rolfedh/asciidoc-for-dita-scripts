"""
Plugin for the AsciiDoc DITA toolkit: AttributeReference

Validate and fix attribute references in AsciiDoc files.
This plugin ensures that attribute references follow proper AsciiDoc syntax
and are compatible with DITA output requirements.

See: 
- https://github.com/jhradilek/asciidoctor-dita-vale/blob/main/styles/AsciiDocDITA/AttributeReference.yml
- https://github.com/jhradilek/asciidoctor-dita-vale/tree/main/fixtures/AttributeReference
"""

__description__ = "Validate and fix attribute references in AsciiDoc files"

import re
from ..file_utils import (common_arg_parser, process_adoc_files,
                          read_text_preserve_endings,
                          write_text_preserve_endings)

# Pattern to match attribute references
ATTRIBUTE_PATTERN = re.compile(r'\{([^}]+)\}')

# Counter patterns
COUNTER_PATTERN = re.compile(r'^counter2?:[a-zA-Z0-9_-]+(?::[a-zA-Z0-9_-]+)?$')

# Character replacement attributes that should be ignored (valid in AsciiDoc)
CHARACTER_REPLACEMENTS = {
    'blank', 'empty', 'sp', 'nbsp', 'zwsp', 'wj', 'apos', 'quot',
    'lsquo', 'rsquo', 'ldquo', 'rdquo', 'deg', 'plus', 'brvbar',
    'vbar', 'amp', 'lt', 'gt', 'startsb', 'endsb', 'caret',
    'asterisk', 'tilde', 'backslash', 'backtick', 'two-colons',
    'two-semicolons', 'cpp', 'pp'
}

# Valid attribute name pattern (letters, numbers, hyphens, underscores)
VALID_ATTR_NAME = re.compile(r'^[a-zA-Z0-9_-]+$')


def validate_attribute_reference(attr_content):
    """
    Validate an attribute reference.
    
    Args:
        attr_content: The content inside the braces (without the braces)
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Empty attribute reference
    if not attr_content.strip():
        return False, "Empty attribute reference"
    
    # Character replacement attributes are always valid
    if attr_content in CHARACTER_REPLACEMENTS:
        return True, None
    
    # Counter references
    if COUNTER_PATTERN.match(attr_content):
        return True, None
    
    # Custom attribute references
    if VALID_ATTR_NAME.match(attr_content):
        return True, None
    
    # Invalid format
    return False, f"Invalid attribute reference format: {attr_content}"


def transform_line(line):
    """
    Validate attribute references in a line.
    
    Args:
        line: Input line to process
        
    Returns:
        Transformed line (currently just validates and warns)
    """
    # Find all attribute references
    for match in ATTRIBUTE_PATTERN.finditer(line):
        attr_content = match.group(1)
        is_valid, error_msg = validate_attribute_reference(attr_content)
        
        if not is_valid:
            print(f"Warning: {error_msg} in: {line.strip()}")
    
    # For now, just return the line as-is (validation only)
    # Future enhancement: could fix common issues
    return line


def process_file(filepath):
    """
    Process a single .adoc file, validating attribute references.
    
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
    """Main function for the AttributeReference plugin."""
    process_adoc_files(args, process_file)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser("AttributeReference", help=__description__)
    common_arg_parser(parser)
    parser.set_defaults(func=main)
