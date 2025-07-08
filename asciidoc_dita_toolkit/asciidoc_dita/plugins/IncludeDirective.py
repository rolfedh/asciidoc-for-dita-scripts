"""
Plugin for the AsciiDoc DITA toolkit: IncludeDirective

Validate and fix include directives in AsciiDoc files.
This plugin ensures that include directives follow proper AsciiDoc syntax
and are compatible with DITA output requirements.

See: 
- https://github.com/jhradilek/asciidoctor-dita-vale/blob/main/styles/AsciiDocDITA/IncludeDirective.yml
- https://github.com/jhradilek/asciidoctor-dita-vale/tree/main/fixtures/IncludeDirective
"""

__description__ = "Validate and fix include directives in AsciiDoc files"

import re
from ..file_utils import (common_arg_parser, process_adoc_files,
                          read_text_preserve_endings,
                          write_text_preserve_endings)

# Pattern to match include directives
INCLUDE_PATTERN = re.compile(r'^(\s*)(\\?)include::([^[\]]+)(?:\[([^\]]*)\])?$')

# Valid file extensions for includes
VALID_EXTENSIONS = {'.adoc', '.asciidoc', '.txt'}

# Valid include options
VALID_OPTIONS = {
    'leveloffset', 'tag', 'tags', 'lines', 'indent', 'encoding',
    'opts', 'lines'
}


def validate_include_directive(filepath, options=None):
    """
    Validate an include directive.
    
    Args:
        filepath: The file path in the include directive
        options: Optional parameters for the include directive
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Empty filepath
    if not filepath.strip():
        return False, "Empty include file path"
    
    # Basic path validation
    if filepath.startswith('/'):
        return False, "Absolute paths should be avoided in include directives"
    
    # Check for valid file extension
    has_valid_extension = any(filepath.endswith(ext) for ext in VALID_EXTENSIONS)
    if not has_valid_extension:
        return False, f"Include file should have a valid extension: {filepath}"
    
    # Validate options if present
    if options:
        # Parse options (key=value pairs separated by commas)
        option_pairs = [opt.strip() for opt in options.split(',')]
        for option_pair in option_pairs:
            if '=' in option_pair:
                key, value = option_pair.split('=', 1)
                key = key.strip()
                if key not in VALID_OPTIONS:
                    return False, f"Unknown include option: {key}"
            else:
                # Simple option without value
                if option_pair not in VALID_OPTIONS:
                    return False, f"Unknown include option: {option_pair}"
    
    return True, None


def transform_line(line):
    """
    Validate include directives in a line.
    
    Args:
        line: Input line to process
        
    Returns:
        Transformed line (currently just validates and warns)
    """
    match = INCLUDE_PATTERN.match(line)
    if match:
        indentation = match.group(1)
        escape = match.group(2)
        filepath = match.group(3)
        options = match.group(4)
        
        # Skip escaped includes
        if escape:
            return line
        
        # Validate the include directive
        is_valid, error_msg = validate_include_directive(filepath, options)
        if not is_valid:
            print(f"Warning: {error_msg} in: {line.strip()}")
    
    # For now, just return the line as-is (validation only)
    # Future enhancement: could fix common issues
    return line


def process_file(filepath):
    """
    Process a single .adoc file, validating include directives.
    
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
    """Main function for the IncludeDirective plugin."""
    process_adoc_files(args, process_file)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser("IncludeDirective", help=__description__)
    common_arg_parser(parser)
    parser.set_defaults(func=main)
