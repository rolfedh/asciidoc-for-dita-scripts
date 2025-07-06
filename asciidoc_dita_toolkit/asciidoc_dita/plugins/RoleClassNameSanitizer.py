"""
Plugin for the AsciiDoc DITA toolkit: RoleClassNameSanitizer

This plugin sanitizes role-based class names by replacing problematic characters
that cause issues in CSS selectors and JavaScript operations.

Based on issue analysis from asciidoctor/asciidoctor#3767 where colons in
role names like [role="system:additional-resources"] cause:
- CSS selector problems requiring escaping
- JavaScript querySelector failures
- Poor developer experience

This plugin transforms:
- `[role="system:additional-resources"]` → `[role="system-additional-resources"]`
- `[role="module:concept"]` → `[role="module-concept"]`
- Multiple roles: `[role="system:warning, ui:button"]` → `[role="system-warning, ui-button"]`
"""

__description__ = "Sanitize role-based class names by replacing problematic characters (colons, etc.) with CSS/JS-friendly alternatives."

import re

from ..file_utils import (common_arg_parser, process_adoc_files,
                          read_text_preserve_endings,
                          write_text_preserve_endings)

# Pattern to match role attributes in AsciiDoc (both single and multiple quoted values)
ROLE_PATTERN_SINGLE = re.compile(r'\[role="([^"]+)"\]')
ROLE_PATTERN_MULTIPLE = re.compile(r'\[role="([^"]*)"(?:\s*,\s*"([^"]*)")*\]')

# Characters that cause problems in CSS/JavaScript and their replacements
PROBLEMATIC_CHARS = {
    ':': '-',  # Colon to hyphen (most common issue)
    '\\': '_',  # Backslash to underscore
    '/': '_',   # Forward slash to underscore
    '|': '_',   # Pipe to underscore
    '&': '_',   # Ampersand to underscore
    '%': '_',   # Percent to underscore
    '#': '_',   # Hash to underscore (though valid in CSS, can cause confusion)
    '?': '_',   # Question mark to underscore
    '*': '_',   # Asterisk to underscore
    '+': '_',   # Plus to underscore
    '=': '_',   # Equals to underscore
    '<': '_',   # Less than to underscore
    '>': '_',   # Greater than to underscore
    '"': '_',   # Double quote to underscore
    "'": '_',   # Single quote to underscore
    '`': '_',   # Backtick to underscore
    '~': '_',   # Tilde to underscore
    '^': '_',   # Caret to underscore
    '@': '_',   # At symbol to underscore
    '$': '_',   # Dollar sign to underscore
    '!': '_',   # Exclamation to underscore
    ' ': '_',   # Space to underscore
    '\t': '_',  # Tab to underscore
}


def sanitize_role_value(role_value):
    """
    Sanitize a role value by replacing problematic characters.
    
    Args:
        role_value: The role value to sanitize (e.g., "system:additional-resources")
        
    Returns:
        Sanitized role value safe for CSS/JavaScript
    """
    # Split by commas to handle multiple roles
    roles = [role.strip() for role in role_value.split(',')]
    sanitized_roles = []
    
    for role in roles:
        sanitized_role = role
        for char, replacement in PROBLEMATIC_CHARS.items():
            sanitized_role = sanitized_role.replace(char, replacement)
        
        # Clean up multiple consecutive underscores/hyphens
        sanitized_role = re.sub(r'[-_]{2,}', '-', sanitized_role)
        
        # Remove leading/trailing hyphens and underscores
        sanitized_role = sanitized_role.strip('-_')
        
        if sanitized_role:  # Only add non-empty roles
            sanitized_roles.append(sanitized_role)
    
    return ', '.join(sanitized_roles)


def sanitize_role_attributes(line):
    """
    Sanitize role attributes in a line of AsciiDoc content.
    Handles both single quoted values and multiple quoted values.
    
    Args:
        line: Input line to process
        
    Returns:
        Line with sanitized role attributes
    """
    # First handle the simple single-quoted case: [role="value"]
    def replace_single_role(match):
        role_value = match.group(1)
        sanitized_value = sanitize_role_value(role_value)
        
        # Only replace if actually changed
        if sanitized_value != role_value:
            return f'[role="{sanitized_value}"]'
        else:
            return match.group(0)
    
    # Handle multiple quoted values: [role="value1", "value2", ...]
    def replace_multiple_roles(match):
        # Extract all quoted values from the match
        full_match = match.group(0)
        # Find all quoted values in the role attribute
        quoted_values = re.findall(r'"([^"]*)"', full_match)
        
        if not quoted_values:
            return full_match
        
        # Sanitize each value
        sanitized_values = []
        changed = False
        for value in quoted_values:
            sanitized = sanitize_role_value(value)
            if sanitized != value:
                changed = True
            sanitized_values.append(sanitized)
        
        # Only replace if actually changed
        if changed:
            return f'[role="{", ".join(sanitized_values)}"]'
        else:
            return full_match
    
    # First try to handle multiple roles pattern
    if ', "' in line and '[role=' in line:
        line = re.sub(r'\[role="[^"]*"(?:\s*,\s*"[^"]*")+\]', replace_multiple_roles, line)
    
    # Then handle remaining single role patterns
    line = ROLE_PATTERN_SINGLE.sub(replace_single_role, line)
    
    return line


def process_file(filepath):
    """
    Process a single .adoc file, sanitizing role attributes.
    Skip processing within comments (single-line // and block comments ////), 
    code blocks, and literal blocks.
    
    Args:
        filepath: Path to the file to process
    """
    try:
        lines = read_text_preserve_endings(filepath)
        new_lines = []
        in_block_comment = False
        in_code_block = False
        in_literal_block = False
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
            
            # Skip processing if we're in a block comment, code block, 
            # literal block, or it's a single-line comment
            if (in_block_comment or in_code_block or in_literal_block or 
                stripped.startswith("//")):
                new_lines.append((text, ending))
            else:
                processed_text = sanitize_role_attributes(text)
                if processed_text != original_text:
                    changes_made = True
                new_lines.append((processed_text, ending))
        
        if changes_made:
            write_text_preserve_endings(filepath, new_lines)
            print(f"Processed {filepath} (sanitized role attributes)")
        else:
            print(f"No changes needed for {filepath}")
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")


def main(args):
    """Main function for the RoleClassNameSanitizer plugin."""
    process_adoc_files(args, process_file)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser("RoleClassNameSanitizer", help=__description__)
    common_arg_parser(parser)
    parser.set_defaults(func=main)