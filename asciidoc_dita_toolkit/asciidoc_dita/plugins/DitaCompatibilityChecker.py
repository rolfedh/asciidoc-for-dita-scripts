"""
Plugin for the AsciiDoc DITA toolkit: DitaCompatibilityChecker

This plugin validates and fixes AsciiDoc content for DITA compatibility issues.
DITA (Darwin Information Typing Architecture) has specific requirements and
limitations that can cause issues when converting from AsciiDoc.

Common DITA compatibility issues this plugin addresses:
- Unsupported HTML elements or attributes
- Nested block elements that DITA doesn't support
- Invalid ID/reference patterns
- Content structure issues
- Missing required metadata

Features:
- Validates content against DITA constraints
- Suggests fixes for common issues
- Ensures proper content structure
- Validates cross-references and links
"""

__description__ = "Validate and fix AsciiDoc content for DITA compatibility issues."

import re

from ..file_utils import (common_arg_parser, process_adoc_files,
                          read_text_preserve_endings,
                          write_text_preserve_endings)

# DITA-unsupported patterns that should be flagged or fixed
DITA_ISSUES = {
    # Nested block elements (DITA doesn't support these)
    'nested_blocks': [
        re.compile(r'^\[.*\]\s*\n\s*\[.*\]', re.MULTILINE),  # Consecutive block attributes
        re.compile(r'^\*\*\*\*\s*\n.*\n\*\*\*\*\s*\n.*\n----', re.MULTILINE),  # Nested delimited blocks
    ],
    
    # Invalid ID patterns for DITA
    'invalid_ids': [
        re.compile(r'\[\[([^]]*[^a-zA-Z0-9_-][^]]*)\]\]'),  # IDs with invalid characters
        re.compile(r'\[\[([0-9][^]]*)\]\]'),  # IDs starting with numbers
        re.compile(r'\[\[([^]]*\s+[^]]*)\]\]'),  # IDs with spaces
    ],
    
    # Problematic HTML elements that don't map well to DITA
    'problematic_html': [
        re.compile(r'<(font|center|blink|marquee)[^>]*>'),  # Deprecated HTML elements
        re.compile(r'<[^>]+style\s*='),  # Inline styles
        re.compile(r'<script[^>]*>'),  # Script tags
        re.compile(r'<iframe[^>]*>'),  # Iframe tags
    ],
    
    # Unsupported table features
    'table_issues': [
        re.compile(r'\|===.*\n.*colspan.*\n.*rowspan', re.MULTILINE | re.DOTALL),  # Complex table spans
        re.compile(r'\|===.*\n.*<[^>]*>.*\n.*\|===', re.MULTILINE | re.DOTALL),  # HTML in table cells
    ],
    
    # Cross-reference issues
    'xref_issues': [
        re.compile(r'<<[^>]*#[^>]*>>'),  # Fragment identifiers in cross-references
        re.compile(r'<<[^>]*\.[^>]*>>'),  # File extensions in cross-references
    ],
}

# Fixes for common DITA issues
DITA_FIXES = {
    # Fix invalid ID characters
    'fix_invalid_ids': lambda match: '[[' + re.sub(r'[^a-zA-Z0-9_-]', '_', match.group(1)) + ']]',
    
    # Fix IDs starting with numbers
    'fix_numeric_ids': lambda match: '[[id_' + match.group(1) + ']]',
    
    # Remove problematic HTML attributes
    'fix_html_styles': lambda match: match.group(0).split(' style=')[0] + '>',
}


def check_dita_compatibility(lines):
    """
    Check AsciiDoc content for DITA compatibility issues.
    
    Args:
        lines: List of (text, ending) tuples
        
    Returns:
        List of compatibility issues found
    """
    issues = []
    content = ''.join(text for text, ending in lines)
    
    for issue_type, patterns in DITA_ISSUES.items():
        for pattern in patterns:
            matches = pattern.findall(content)
            if matches:
                issues.append({
                    'type': issue_type,
                    'pattern': pattern.pattern,
                    'matches': matches,
                    'count': len(matches)
                })
    
    return issues


def fix_dita_issues(line):
    """
    Fix common DITA compatibility issues in a line.
    
    Args:
        line: Input line to process
        
    Returns:
        Line with DITA compatibility fixes applied
    """
    # Fix invalid ID characters
    for pattern in DITA_ISSUES['invalid_ids']:
        if pattern.search(line):
            line = pattern.sub(DITA_FIXES['fix_invalid_ids'], line)
    
    # Fix IDs starting with numbers
    numeric_id_pattern = re.compile(r'\[\[([0-9][^]]*)\]\]')
    if numeric_id_pattern.search(line):
        line = numeric_id_pattern.sub(DITA_FIXES['fix_numeric_ids'], line)
    
    # Fix problematic HTML
    for pattern in DITA_ISSUES['problematic_html']:
        if 'style=' in line:
            line = re.sub(r'(<[^>]+)\s+style\s*=[^>]*>', r'\1>', line)
    
    # Fix cross-reference issues
    # Remove fragment identifiers from cross-references
    line = re.sub(r'<<([^>]*)#[^>]*>>', r'<<\1>>', line)
    
    # Remove file extensions from cross-references
    line = re.sub(r'<<([^>]*)\.adoc>>', r'<<\1>>', line)
    
    return line


def validate_content_structure(lines):
    """
    Validate the overall content structure for DITA compatibility.
    
    Args:
        lines: List of (text, ending) tuples
        
    Returns:
        List of structural issues found
    """
    issues = []
    content = ''.join(text for text, ending in lines)
    
    # Check for proper document structure
    if not re.search(r'^= .+$', content, re.MULTILINE):
        issues.append("Missing document title (should start with '= Title')")
    
    # Check for proper section hierarchy
    section_levels = re.findall(r'^(=+)\s', content, re.MULTILINE)
    if section_levels:
        prev_level = 0
        for level_str in section_levels:
            level = len(level_str)
            if level > prev_level + 1:
                issues.append(f"Section hierarchy jumps from level {prev_level} to {level}")
            prev_level = level
    
    # Check for required metadata
    if not re.search(r'^:[^:]+:', content, re.MULTILINE):
        issues.append("Consider adding document attributes for better DITA compatibility")
    
    return issues


def process_file(filepath):
    """
    Process a single .adoc file, checking and fixing DITA compatibility issues.
    
    Args:
        filepath: Path to the file to process
    """
    try:
        lines = read_text_preserve_endings(filepath)
        
        # Check for compatibility issues
        compatibility_issues = check_dita_compatibility(lines)
        structural_issues = validate_content_structure(lines)
        
        # Apply fixes
        new_lines = []
        changes_made = False
        in_code_block = False
        in_literal_block = False
        
        for text, ending in lines:
            original_text = text
            stripped = text.strip()
            
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
            
            # Skip processing if we're in a code or literal block
            if in_code_block or in_literal_block:
                new_lines.append((text, ending))
            else:
                processed_text = fix_dita_issues(text)
                if processed_text != original_text:
                    changes_made = True
                new_lines.append((processed_text, ending))
        
        # Report findings
        if compatibility_issues or structural_issues:
            print(f"\nDITA Compatibility Report for {filepath}:")
            print("=" * 60)
            
            if compatibility_issues:
                print("Compatibility Issues Found:")
                for issue in compatibility_issues:
                    print(f"  - {issue['type']}: {issue['count']} occurrences")
            
            if structural_issues:
                print("Structural Issues:")
                for issue in structural_issues:
                    print(f"  - {issue}")
            
            if changes_made:
                write_text_preserve_endings(filepath, new_lines)
                print(f"✓ Applied automatic fixes to {filepath}")
            else:
                print("✓ No automatic fixes needed")
        else:
            print(f"✓ {filepath} is DITA-compatible")
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")


def main(args):
    """Main function for the DitaCompatibilityChecker plugin."""
    process_adoc_files(args, process_file)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser("DitaCompatibilityChecker", help=__description__)
    common_arg_parser(parser)
    parser.set_defaults(func=main)