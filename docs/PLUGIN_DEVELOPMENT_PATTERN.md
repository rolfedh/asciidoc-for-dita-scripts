# Plugin Development Pattern

This document describes the standardized pattern for developing plugins and their corresponding test fixtures in the AsciiDoc DITA Toolkit. This pattern was established during the EntityReference plugin implementation and should be followed for all future plugins.

## Overview

The plugin development pattern ensures:

- Consistent plugin architecture and behavior
- Robust testing with proper fixture management
- Clear separation of concerns between transformation logic and test infrastructure
- Compliance with external rule specifications (e.g., Vale rules)

## Directory Structure

```text
asciidoc_dita_toolkit/
├── asciidoc_dita/
│   └── plugins/
│       └── PluginName.py              # Main plugin implementation
└── tests/
    ├── test_PluginName.py             # Unit tests for the plugin
    ├── asciidoc_testkit.py            # Shared test utilities
    └── fixtures/
        └── PluginName/                # Plugin-specific test fixtures
            ├── vale.ini               # Vale configuration (if applicable)
            ├── input_case1.adoc       # Input test file
            ├── input_case1.expected   # Expected output (colocated)
            ├── input_case2.adoc
            ├── input_case2.expected
            └── ...
```

## Plugin Implementation Pattern

### 1. Plugin Structure (`PluginName.py`)

```python
"""
Plugin for the AsciiDoc DITA toolkit: PluginName

Brief description of what the plugin does.

See: 
- Link to external rule specification (if applicable)
- Link to external fixtures (if applicable)
"""
__description__ = "Brief description for CLI help"

import re
from ..file_utils import read_text_preserve_endings, write_text_preserve_endings, process_adoc_files, common_arg_parser

# Constants and mappings
CONSTANT_PATTERN = re.compile(r"pattern")
MAPPING_DICT = {
    "key": "value",
    # ...
}

def transform_line(line):
    """
    Apply transformation to a single line.
    
    Args:
        line: Input line to process
        
    Returns:
        Transformed line
    """
    # Implementation for simple line-by-line transformations
    pass

def process_file(filepath):
    """
    Process a single .adoc file with full context.
    Use this for transformations that require state tracking across lines.
    
    Args:
        filepath: Path to the file to process
    """
    try:
        lines = read_text_preserve_endings(filepath)
        new_lines = []
        # State variables for complex transformations
        state_var = False
        
        for text, ending in lines:
            # Process each line with state awareness
            # Example: tracking block comments, sections, etc.
            if needs_state_tracking:
                # Handle state changes
                new_lines.append((process_with_state(text), ending))
            else:
                new_lines.append((transform_line(text), ending))
        
        write_text_preserve_endings(filepath, new_lines)
        print(f"Processed {filepath} (preserved per-line endings)")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main(args):
    """Main function for the plugin."""
    process_adoc_files(args, process_file)

def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser("PluginName", help=__description__)
    common_arg_parser(parser)
    parser.set_defaults(func=main)
```

### 2. Key Implementation Guidelines

- **Use `process_file()` for stateful transformations** (e.g., tracking comments, blocks)
- **Use `transform_line()` for simple line-by-line transformations**
- **Preserve line endings** using `read_text_preserve_endings()` and `write_text_preserve_endings()`
- **Handle edge cases** like comments, code blocks, or special AsciiDoc syntax
- **Provide meaningful error messages** and warnings

## Test Implementation Pattern

### 1. Test Structure (`test_PluginName.py`)

```python
"""
Test suite for the PluginName plugin.

This script tests the transformation logic using fixtures from
tests/fixtures/PluginName/.

For each .adoc file, it expects a corresponding .expected file in the same directory.
"""

import os
import sys
import unittest

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from asciidoc_dita_toolkit.asciidoc_dita.plugins.PluginName import transform_line, process_file
from tests.asciidoc_testkit import run_linewise_test, get_same_dir_fixture_pairs, run_file_based_test

FIXTURE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures', 'PluginName'))

class TestPluginName(unittest.TestCase):
    
    def test_basic_functionality(self):
        """Test basic transformation functionality."""
        input_text = "input example"
        expected = "expected output"
        result = transform_line(input_text)
        self.assertEqual(result, expected)
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test cases for edge conditions
        pass
    
    def test_fixture_based_tests(self):
        """Run tests based on fixture files if they exist."""
        if os.path.exists(FIXTURE_DIR):
            fixture_count = 0
            for input_path, expected_path in get_same_dir_fixture_pairs(FIXTURE_DIR):
                fixture_count += 1
                with self.subTest(fixture=os.path.basename(input_path)):
                    fixture_name = os.path.basename(input_path)
                    
                    # Choose test method based on whether state tracking is needed
                    if requires_state_tracking(fixture_name):
                        success = run_file_based_test(input_path, expected_path, process_file)
                    else:
                        success = run_linewise_test(input_path, expected_path, transform_line)
                    
                    self.assertTrue(success, f"Fixture test failed for {input_path}")
            
            if fixture_count > 0:
                print(f"Ran {fixture_count} fixture-based tests")
        else:
            self.skipTest(f"Fixture directory not found: {FIXTURE_DIR}")

if __name__ == '__main__':
    unittest.main()
```

### 2. Test Method Selection

Choose the appropriate test method based on your plugin's needs:

- **`run_linewise_test()`**: For simple line-by-line transformations
- **`run_file_based_test()`**: For stateful transformations that require context across lines

## Fixture Development Pattern

### 1. Fixture Naming Convention

Use descriptive names that indicate the test purpose:

- **`ignore_*`**: Cases where the plugin should NOT make changes
  - `ignore_comments.adoc` - entities in comments should be preserved
  - `ignore_code_blocks.adoc` - entities in code blocks should be preserved
  - `ignore_supported_entities.adoc` - supported entities should be preserved

- **`report_*`**: Cases where the plugin SHOULD make changes
  - `report_entity_references.adoc` - basic entity replacement
  - `report_multiple_references.adoc` - multiple entities in one line
  - `report_complex_markup.adoc` - entities mixed with other markup

### 2. Expected File Creation Process

1. **Start with rule specification**: Review external rule documentation (e.g., Vale rules)
2. **Create input files**: Write `.adoc` files that test various scenarios
3. **Run the plugin**: Process input files to generate actual output
4. **Verify compliance**: Ensure output matches the rule specification
5. **Create expected files**: Copy the verified output to `.expected` files
6. **Colocate files**: Place `.expected` files alongside `.adoc` files in the same directory

### 3. Expected File Validation

```bash
# Manual validation process
cp tests/fixtures/PluginName/test_case.adoc /tmp/test.adoc
python3 -m asciidoc_dita_toolkit.asciidoc_dita.toolkit PluginName -f /tmp/test.adoc
diff /tmp/test.adoc tests/fixtures/PluginName/test_case.expected
```

## Example: EntityReference Pattern Implementation

The EntityReference plugin demonstrates this pattern:

### Rule Compliance

- **External Rule**: [AsciiDocDITA Vale EntityReference](https://github.com/jhradilek/asciidoctor-dita-vale)
- **Specification**: "DITA 1.3 supports five XML entities: &amp;, &lt;, &gt;, &apos;, &quot;. Replace others with AsciiDoc attributes."

### Implementation Features

- **Stateful processing**: Tracks comment blocks to skip entity replacement in comments
- **Mapping dictionary**: `ENTITY_TO_ASCIIDOC` for HTML entity → AsciiDoc attribute conversion
- **Comment handling**: Preserves entities in single-line (`//`) and block (`////`) comments

### Test Strategy

- **File-based tests**: For `ignore_*` fixtures that contain comments requiring state tracking
- **Line-based tests**: For `report_*` fixtures with simple entity replacement
- **Comprehensive coverage**: Tests basic replacement, multiple entities, mixed markup, and comment preservation

## Best Practices

### 1. Plugin Development

- **Follow the single responsibility principle**: Each plugin should handle one specific rule or transformation
- **Implement comprehensive error handling**: Catch and report processing errors gracefully
- **Preserve file structure**: Maintain line endings, indentation, and formatting
- **Add meaningful logging**: Help users understand what the plugin is doing

### 2. Test Development

- **Test both positive and negative cases**: Ensure the plugin transforms what it should and ignores what it shouldn't
- **Use descriptive fixture names**: Make it clear what each test case is validating
- **Maintain fixture independence**: Each fixture should test a specific scenario
- **Verify external rule compliance**: Ensure expected files match external specifications

### 3. Documentation

- **Link to external rules**: Reference the original rule specifications
- **Document edge cases**: Explain how the plugin handles special situations
- **Provide usage examples**: Show how to use the plugin effectively
- **Update CONTRIBUTING.md**: Add guidance for future plugin developers

## Integration with Existing Infrastructure

### 1. Test Infrastructure

- **Leverage `asciidoc_testkit.py`**: Use shared test utilities for consistency
- **Follow fixture discovery patterns**: Use `get_same_dir_fixture_pairs()` for new colocated structure
- **Maintain backward compatibility**: Support both old and new fixture patterns during transition

### 2. CLI Integration

- **Use `common_arg_parser()`**: Inherit standard CLI arguments (`-d`, `-f`, `-r`)
- **Register subcommands**: Follow the `register_subcommand()` pattern
- **Provide helpful descriptions**: Use clear, concise help text

### 3. File Processing

- **Use `process_adoc_files()`**: Leverage existing file discovery and filtering
- **Preserve encoding**: Handle UTF-8 files correctly
- **Maintain line endings**: Preserve original line ending style (LF, CRLF)

## Migration from Legacy Patterns

When updating existing plugins to follow this pattern:

1. **Refactor fixture organization**: Move `.expected` files to be colocated with `.adoc` files
2. **Update test infrastructure**: Switch from legacy fixture discovery to `get_same_dir_fixture_pairs()`
3. **Add state handling**: Implement stateful processing if needed for complex transformations
4. **Enhance error handling**: Add proper exception handling and user feedback
5. **Update documentation**: Ensure plugin documentation follows this pattern

## Conclusion

This pattern provides a robust, maintainable approach to plugin development that ensures:

- **Consistency** across all plugins
- **Reliability** through comprehensive testing
- **Maintainability** through clear separation of concerns
- **Compliance** with external rule specifications
- **Extensibility** for future enhancements

Following this pattern will help maintain code quality and make it easier for contributors to understand, modify, and extend the toolkit's functionality.
