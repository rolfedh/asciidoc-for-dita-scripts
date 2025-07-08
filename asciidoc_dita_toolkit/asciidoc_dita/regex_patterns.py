"""
Shared regex patterns for AsciiDoc processing.

This module provides centralized regex patterns used across all AsciiDoc DITA Toolkit plugins.
Centralizing patterns reduces duplication, ensures consistency, and makes maintenance easier.

Pattern Categories:
- ID Patterns: For matching AsciiDoc ID attributes
- Cross-reference Patterns: For matching xref and link elements
- AsciiDoc Structure Patterns: For matching document structure elements
"""

import re
from typing import Pattern

# =============================================================================
# ID PATTERNS
# =============================================================================

# Basic ID pattern: [id="some_id"]
ID_PATTERN = r'\[id="([^"]+)"\]'

# Context-suffixed ID pattern: [id="base_context"] -> captures (base, context)
# Matches the last underscore as the separator between base and context
ID_WITH_CONTEXT_PATTERN = r'\[id="([^"]+)_([^"]+)"\]'

# =============================================================================
# CROSS-REFERENCE PATTERNS
# =============================================================================

# Basic xref pattern with optional file and fragment: xref:file.adoc#id[text]
# Captures: (file_or_id, optional_id, link_text)
XREF_BASIC_PATTERN = r'xref:([^#\[]+)(?:#([^#\[]+))?(\[.*?\])'

# Unfixed xref pattern (for CrossReference plugin) - excludes already fixed xrefs
# Uses negative lookahead to avoid matching xrefs that already have .adoc#
XREF_UNFIXED_PATTERN = r'(?<=xref:)(?!.*\.adoc#)([^\[]+)(\[.*?\])'

# Link pattern: link:url#anchor[text]
# Captures: (url, optional_anchor, link_text)
LINK_PATTERN = r'link:([^#\[]+)(?:#([^#\[]+))?(\[.*?\])'

# =============================================================================
# ASCIIDOC STRUCTURE PATTERNS
# =============================================================================

# Context attribute pattern: :context: value
# Requires at least one space after the colon
CONTEXT_ATTR_PATTERN = r'^:context:\s+(.+)$'

# Include directive pattern: include::filename.adoc[]
# Uses positive lookbehind and lookahead to ensure proper include syntax
INCLUDE_PATTERN = r'(?<=^include::)[^[]+(?=\[\])'

# =============================================================================
# PRE-COMPILED PATTERNS
# =============================================================================

class CompiledPatterns:
    """
    Pre-compiled regex patterns for better performance.
    
    Using pre-compiled patterns avoids recompilation overhead and ensures
    consistent pattern behavior across all plugins.
    """
    
    # ID patterns
    ID_REGEX: Pattern = re.compile(ID_PATTERN)
    ID_WITH_CONTEXT_REGEX: Pattern = re.compile(ID_WITH_CONTEXT_PATTERN)
    
    # Cross-reference patterns
    XREF_BASIC_REGEX: Pattern = re.compile(XREF_BASIC_PATTERN)
    XREF_UNFIXED_REGEX: Pattern = re.compile(XREF_UNFIXED_PATTERN)
    LINK_REGEX: Pattern = re.compile(LINK_PATTERN)
    
    # AsciiDoc structure patterns
    CONTEXT_ATTR_REGEX: Pattern = re.compile(CONTEXT_ATTR_PATTERN, re.MULTILINE)
    INCLUDE_REGEX: Pattern = re.compile(INCLUDE_PATTERN)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def compile_pattern(pattern: str, flags: int = 0) -> Pattern:
    """
    Compile a regex pattern with optional flags.
    
    Args:
        pattern: The regex pattern string to compile
        flags: Optional regex flags (e.g., re.MULTILINE, re.IGNORECASE)
        
    Returns:
        Compiled regex pattern object
        
    Example:
        >>> custom_pattern = compile_pattern(r'custom_(\\w+)', re.IGNORECASE)
        >>> match = custom_pattern.search("Custom_Text")
    """
    return re.compile(pattern, flags)

def validate_patterns() -> bool:
    """
    Validate that all compiled patterns are working correctly.
    
    Returns:
        True if all patterns compile and work as expected, False otherwise
        
    This function can be used in tests to ensure pattern integrity.
    """
    try:
        # Test ID patterns
        assert CompiledPatterns.ID_REGEX.match('[id="test"]')
        assert CompiledPatterns.ID_WITH_CONTEXT_REGEX.match('[id="base_context"]')
        
        # Test cross-reference patterns
        assert CompiledPatterns.XREF_BASIC_REGEX.search('xref:target[text]')
        assert CompiledPatterns.XREF_UNFIXED_REGEX.search('xref:target[text]')
        assert CompiledPatterns.LINK_REGEX.search('link:url[text]')
        
        # Test structure patterns
        assert CompiledPatterns.CONTEXT_ATTR_REGEX.search(':context: test')
        assert CompiledPatterns.INCLUDE_REGEX.search('include::file.adoc[]')
        
        return True
        
    except (AssertionError, re.error):
        return False

# =============================================================================
# PATTERN DOCUMENTATION
# =============================================================================

PATTERN_EXAMPLES = {
    'ID_PATTERN': {
        'pattern': ID_PATTERN,
        'description': 'Matches AsciiDoc ID attributes',
        'examples': {
            '[id="simple_id"]': 'Captures: simple_id',
            '[id="complex-id_with-chars"]': 'Captures: complex-id_with-chars',
        },
        'non_matches': ['id="missing_brackets"', '[id=no_quotes]']
    },
    
    'ID_WITH_CONTEXT_PATTERN': {
        'pattern': ID_WITH_CONTEXT_PATTERN,
        'description': 'Matches ID attributes with underscores, using last underscore as separator',
        'examples': {
            '[id="topic_banana"]': 'Captures: (topic, banana)',
            '[id="installing-edge_ocp4"]': 'Captures: (installing-edge, ocp4)',
        },
        'non_matches': ['[id="nounderscorehere"]', 'id="topic_banana"']
    },
    
    'XREF_BASIC_PATTERN': {
        'pattern': XREF_BASIC_PATTERN,
        'description': 'Matches xref cross-references with optional file and fragment',
        'examples': {
            'xref:target[Link Text]': 'Captures: (target, None, [Link Text])',
            'xref:file.adoc#section[Section]': 'Captures: (file.adoc, section, [Section])',
        },
        'non_matches': ['link:target[text]', 'xref:target']
    },
    
    'XREF_UNFIXED_PATTERN': {
        'pattern': XREF_UNFIXED_PATTERN,
        'description': 'Matches unfixed xrefs (without .adoc#) for CrossReference plugin',
        'examples': {
            'xref:target[text]': 'Captures: (target, [text])',
        },
        'non_matches': ['xref:file.adoc#target[text]', 'xref:path/file.adoc#target[text]']
    },
    
    'LINK_PATTERN': {
        'pattern': LINK_PATTERN,
        'description': 'Matches link elements with optional anchors',
        'examples': {
            'link:http://example.com[Example]': 'Captures: (http://example.com, None, [Example])',
            'link:file.html#anchor[Link]': 'Captures: (file.html, anchor, [Link])',
        },
        'non_matches': ['xref:target[text]', 'link:target']
    },
    
    'CONTEXT_ATTR_PATTERN': {
        'pattern': CONTEXT_ATTR_PATTERN,
        'description': 'Matches context attribute definitions with required space after colon',
        'examples': {
            ':context: banana': 'Captures: banana',
            ':context: ocp4': 'Captures: ocp4',
        },
        'non_matches': [':other: value', 'context: no_colon', ':context:no_space']
    },
    
    'INCLUDE_PATTERN': {
        'pattern': INCLUDE_PATTERN,
        'description': 'Matches include directive filenames with proper syntax',
        'examples': {
            'include::chapter1.adoc[]': 'Captures: chapter1.adoc',
            'include::modules/procedure.adoc[]': 'Captures: modules/procedure.adoc',
        },
        'non_matches': ['include chapter1.adoc', 'include::file.adoc[tag=part]', 'include::file.adoc']
    }
}

def get_pattern_documentation(pattern_name: str) -> dict:
    """
    Get documentation for a specific pattern.
    
    Args:
        pattern_name: Name of the pattern to get documentation for
        
    Returns:
        Dictionary containing pattern documentation, examples, and non-matches
        
    Example:
        >>> doc = get_pattern_documentation('ID_PATTERN')
        >>> print(doc['description'])
        Matches AsciiDoc ID attributes
    """
    return PATTERN_EXAMPLES.get(pattern_name, {})

def list_available_patterns() -> list:
    """
    Get a list of all available pattern names.
    
    Returns:
        List of pattern names available in this module
    """
    return list(PATTERN_EXAMPLES.keys())