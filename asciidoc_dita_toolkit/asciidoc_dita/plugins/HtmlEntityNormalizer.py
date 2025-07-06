"""
Plugin for the AsciiDoc DITA toolkit: HtmlEntityNormalizer

This plugin ensures consistent HTML entity escaping in AsciiDoc content to prevent
XSS vulnerabilities, malformed HTML, and rendering issues.

Based on HTML entity handling issues found in various AsciiDoc processors,
this plugin normalizes entity usage to ensure safe and consistent output.

Features:
- Converts problematic raw characters to proper HTML entities
- Normalizes inconsistent entity usage
- Preserves existing valid entities
- Handles special cases for AsciiDoc/DITA compatibility
"""

__description__ = "Normalize HTML entity usage in AsciiDoc content for security and consistency."

import re

from ..file_utils import (common_arg_parser, process_adoc_files,
                          read_text_preserve_endings,
                          write_text_preserve_endings)

# Characters that should be converted to HTML entities for safety
UNSAFE_CHARS = {
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;',
    '"': '&quot;',
    "'": '&#39;',
}

# Pattern to match existing HTML entities (to avoid double-encoding)
ENTITY_PATTERN = re.compile(r'&[a-zA-Z0-9#]+;')

# Pattern to match AsciiDoc attribute references (to avoid converting them)
ASCIIDOC_ATTR_PATTERN = re.compile(r'\{[^}]+\}')

# Pattern to match AsciiDoc macros and special syntax
ASCIIDOC_MACRO_PATTERN = re.compile(r'(link:|image:|include:|ifdef:|ifndef:|endif::|ifeval:|pass:)')

# Pattern to match code spans and other literal content
LITERAL_CONTENT_PATTERNS = [
    re.compile(r'`[^`]*`'),  # Inline code
    re.compile(r'\+[^+]*\+'),  # Literal text
    re.compile(r'##[^#]*##'),  # Unquoted text
]


def is_inside_literal_content(text, position):
    """
    Check if a position in text is inside literal content that should not be processed.
    
    Args:
        text: The text to check
        position: The position to check
        
    Returns:
        True if position is inside literal content, False otherwise
    """
    for pattern in LITERAL_CONTENT_PATTERNS:
        for match in pattern.finditer(text):
            if match.start() <= position < match.end():
                return True
    return False


def normalize_entities_in_line(line):
    """
    Normalize HTML entities in a line of AsciiDoc content.
    
    This function:
    1. Preserves existing valid HTML entities
    2. Preserves AsciiDoc attribute references
    3. Converts unsafe raw characters to HTML entities
    4. Avoids processing literal content
    
    Args:
        line: Input line to process
        
    Returns:
        Line with normalized HTML entities
    """
    # Don't process lines that are primarily AsciiDoc macros
    if ASCIIDOC_MACRO_PATTERN.search(line):
        return line
    
    # Create a list to track which characters to skip (existing entities and attributes)
    skip_positions = set()
    
    # Mark positions of existing HTML entities
    for match in ENTITY_PATTERN.finditer(line):
        skip_positions.update(range(match.start(), match.end()))
    
    # Mark positions of AsciiDoc attribute references
    for match in ASCIIDOC_ATTR_PATTERN.finditer(line):
        skip_positions.update(range(match.start(), match.end()))
    
    # Mark positions of literal content
    for pattern in LITERAL_CONTENT_PATTERNS:
        for match in pattern.finditer(line):
            skip_positions.update(range(match.start(), match.end()))
    
    # Process the line character by character
    result = []
    i = 0
    while i < len(line):
        char = line[i]
        
        # Skip if this position is marked for skipping
        if i in skip_positions:
            result.append(char)
            i += 1
            continue
        
        # Convert unsafe characters to entities
        if char in UNSAFE_CHARS:
            # Special handling for ampersand to avoid double-encoding
            if char == '&':
                # Look ahead to see if this might be part of an entity
                remaining = line[i:]
                if not re.match(r'&[a-zA-Z0-9#]+;', remaining):
                    result.append(UNSAFE_CHARS[char])
                else:
                    result.append(char)
            else:
                result.append(UNSAFE_CHARS[char])
        else:
            result.append(char)
        
        i += 1
    
    return ''.join(result)


def process_file(filepath):
    """
    Process a single .adoc file, normalizing HTML entities.
    Skip processing within comments, code blocks, and literal blocks.
    
    Args:
        filepath: Path to the file to process
    """
    try:
        lines = read_text_preserve_endings(filepath)
        new_lines = []
        in_block_comment = False
        in_code_block = False
        in_literal_block = False
        in_passthrough_block = False
        changes_made = False
        
        for text, ending in lines:
            original_text = text
            stripped = text.strip()
            
            # Check for block comment delimiters
            if stripped == "////":
                in_block_comment = not in_block_comment
                new_lines.append((text, ending))
                continue
            
            # Check for code block delimiters
            if stripped.startswith("----"):
                in_code_block = not in_code_block
                new_lines.append((text, ending))
                continue
            
            # Check for literal block delimiters
            if stripped.startswith("...."):
                in_literal_block = not in_literal_block
                new_lines.append((text, ending))
                continue
            
            # Check for passthrough block delimiters
            if stripped.startswith("++++"):
                in_passthrough_block = not in_passthrough_block
                new_lines.append((text, ending))
                continue
            
            # Skip processing if we're in a block comment, code block, 
            # literal block, passthrough block, or it's a single-line comment
            if (in_block_comment or in_code_block or in_literal_block or 
                in_passthrough_block or stripped.startswith("//")):
                new_lines.append((text, ending))
            else:
                processed_text = normalize_entities_in_line(text)
                if processed_text != original_text:
                    changes_made = True
                new_lines.append((processed_text, ending))
        
        if changes_made:
            write_text_preserve_endings(filepath, new_lines)
            print(f"Processed {filepath} (normalized HTML entities)")
        else:
            print(f"No changes needed for {filepath}")
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")


def main(args):
    """Main function for the HtmlEntityNormalizer plugin."""
    process_adoc_files(args, process_file)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser("HtmlEntityNormalizer", help=__description__)
    common_arg_parser(parser)
    parser.set_defaults(func=main)