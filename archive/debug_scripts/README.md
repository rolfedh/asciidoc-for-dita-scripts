# Archived Debug Scripts

This directory contains development debugging scripts that were moved from the project root during code cleanup.

## Files

- **debug_admonition_detailed.py** - Detailed debugging for admonition detection
- **debug_code_blocks_detailed.py** - Detailed debugging for code block processing  
- **debug_code_blocks.py** - Basic code block debugging
- **debug_context_detection.py** - Context detection debugging with test cases
- **debug_detection.py** - General detection debugging utilities
- **debug_example_lines.py** - Example line detection debugging
- **debug_report_files.py** - File reporting debugging utilities
- **debug_specific_lines.py** - Specific line debugging tools

## Purpose

These scripts were created during plugin development to:

- Debug regex pattern matching
- Test detection algorithms
- Analyze specific file processing issues
- Validate plugin behavior on edge cases

## Status

These files are **archived** rather than deleted because they:

1. Contain domain-specific debugging knowledge
2. May be useful for future plugin development
3. Demonstrate debugging approaches for complex text processing
4. Preserve development history and context

## Usage

These scripts are not maintained as part of the main codebase but can be referenced or adapted for:

- Debugging new plugin issues
- Understanding detection algorithm behavior
- Creating new debugging tools
- Learning plugin development patterns

## Note

For active development, use the comprehensive test suite in `tests/` directory instead of these debugging scripts.
