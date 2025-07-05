# Plugin Development Guide

Complete guide for developing plugins for the AsciiDoc DITA Toolkit.

## 🔌 Plugin Architecture Overview

The AsciiDoc DITA Toolkit uses a plugin-based architecture that allows modular transformations of AsciiDoc content. Each plugin implements a standardized interface and can be enabled or disabled independently.

### Core Principles

- **Single Responsibility**: Each plugin handles one specific transformation
- **Stateless Design**: Plugins don't maintain state between file processing
- **Error Isolation**: Plugin errors don't stop processing of other files
- **Consistent Interface**: All plugins follow the same function signature

### Plugin Discovery

Plugins are automatically discovered from the `plugins/` directory using Python's module system. Any Python file in this directory with a `process()` function is considered a plugin.

## 🚀 Creating a New Plugin

### 1. Plugin File Structure

Create a new file in `asciidoc_dita_toolkit/asciidoc_dita/plugins/`:

```python
# plugins/YourPlugin.py
"""
Plugin for the AsciiDoc DITA toolkit: YourPlugin

Brief description of what this plugin does and why it's useful.

See: 
- Link to external rule specification (if applicable)
- Link to documentation or standards this implements
"""

__description__ = "Brief description shown in CLI help"

import re
from pathlib import Path

def process(file_path, content):
    """
    Process AsciiDoc file content and apply transformations.
    
    This is the main entry point that the toolkit calls for each file.
    
    Args:
        file_path (str): Path to the file being processed
        content (str): Current file content as string
        
    Returns:
        tuple: (changed: bool, new_content: str)
            changed: True if content was modified, False otherwise
            new_content: Modified content, or original if unchanged
    """
    # Your plugin logic here
    modified_content = content
    changed = False
    
    # Example: Simple text replacement
    if "find_this" in content:
        modified_content = content.replace("find_this", "replace_with_this")
        changed = True
    
    return changed, modified_content
```

### 2. Plugin Interface Contract

All plugins must implement this exact function signature:

```python
def process(file_path: str, content: str) -> tuple[bool, str]:
    """
    Required plugin interface.
    
    Args:
        file_path: Path to file being processed (for context/filename analysis)
        content: Current file content
        
    Returns:
        (changed, new_content): Tuple indicating if content changed and the new content
    """
```

### 3. Plugin Metadata

Include these module-level attributes:

```python
__description__ = "Short description for --list-plugins command"
__version__ = "1.0.0"  # Optional: plugin version
__author__ = "Your Name"  # Optional: plugin author
```

## 📝 Plugin Development Patterns

### Content Analysis Plugin

For plugins that analyze content structure (like ContentType):

```python
def process(file_path, content):
    """Analyze content and add metadata."""
    lines = content.split('\n')
    
    # Check if content already has the metadata
    if any('content-type:' in line for line in lines):
        return False, content  # No changes needed
    
    # Analyze content structure
    content_type = analyze_content_structure(content)
    
    # Add metadata at the top
    metadata_block = f"[cols=\"1\"]\n|===\n\na|*Content Type:* {content_type}\n\n|===\n\n"
    modified_content = metadata_block + content
    
    return True, modified_content

def analyze_content_structure(content):
    """Analyze content to determine type."""
    if re.search(r'^\d+\.\s', content, re.MULTILINE):
        return "procedure"
    elif "assembly" in content.lower():
        return "assembly"
    else:
        return "concept"
```

### Text Transformation Plugin

For plugins that transform text content (like EntityReference):

```python
def process(file_path, content):
    """Transform text patterns in content."""
    # Define transformation patterns
    transformations = {
        r'&amp;': '{amp}',
        r'&hellip;': '{hellip}',
        r'&mdash;': '{mdash}',
        r'&copy;': '{copy}',
    }
    
    modified_content = content
    changed = False
    
    for pattern, replacement in transformations.items():
        new_content = re.sub(pattern, replacement, modified_content)
        if new_content != modified_content:
            modified_content = new_content
            changed = True
    
    return changed, modified_content
```

### File-Based Configuration Plugin

For plugins that use external configuration:

```python
import json
from pathlib import Path

def process(file_path, content):
    """Process based on configuration file."""
    config = load_configuration()
    if not config:
        return False, content  # No configuration, no changes
    
    # Apply transformations based on configuration
    modified_content = apply_config_transformations(content, config)
    changed = modified_content != content
    
    return changed, modified_content

def load_configuration():
    """Load configuration from standard locations."""
    config_paths = [
        Path('./.yourplugin.json'),
        Path.home() / '.yourplugin.json'
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                return json.loads(config_path.read_text())
            except json.JSONDecodeError:
                # Log warning and continue
                pass
    
    return None
```

## 🧪 Plugin Testing

### 1. Create Test File

Create `tests/test_YourPlugin.py`:

```python
import pytest
from pathlib import Path
from asciidoc_dita_toolkit.asciidoc_dita.plugins.YourPlugin import process

class TestYourPlugin:
    """Test suite for YourPlugin."""
    
    def test_no_changes_when_not_needed(self):
        """Test that plugin doesn't change content when no transformation is needed."""
        content = "= Simple Document\n\nContent that doesn't need changes."
        changed, result = process("test.adoc", content)
        
        assert not changed
        assert result == content
    
    def test_basic_transformation(self):
        """Test basic plugin functionality."""
        input_content = "= Document\n\nContent with find_this pattern."
        expected_content = "= Document\n\nContent with replace_with_this pattern."
        
        changed, result = process("test.adoc", input_content)
        
        assert changed
        assert result == expected_content
    
    @pytest.mark.parametrize("input_text,expected_text", [
        ("Text with find_this", "Text with replace_with_this"),
        ("Multiple find_this and find_this", "Multiple replace_with_this and replace_with_this"),
        ("No pattern here", "No pattern here"),  # No change expected
    ])
    def test_pattern_variations(self, input_text, expected_text):
        """Test plugin with various input patterns."""
        content = f"= Document\n\n{input_text}"
        expected = f"= Document\n\n{expected_text}"
        
        changed, result = process("test.adoc", content)
        
        if input_text == expected_text:
            assert not changed
        else:
            assert changed
        assert result == expected
```

### 2. Create Test Fixtures

Create directory `tests/fixtures/YourPlugin/` with test files:

```bash
# Create fixture directory
mkdir -p tests/fixtures/YourPlugin

# Create input file
cat > tests/fixtures/YourPlugin/input_basic.adoc << 'EOF'
= Example Document

This document contains find_this pattern that should be transformed.

Some more content with find_this again.
EOF

# Create expected output file  
cat > tests/fixtures/YourPlugin/input_basic.expected << 'EOF'
= Example Document

This document contains replace_with_this pattern that should be transformed.

Some more content with replace_with_this again.
EOF
```

### 3. Fixture-Based Tests

Add fixture-based tests to your test file:

```python
@pytest.fixture
def fixture_dir():
    """Return path to plugin fixtures."""
    return Path(__file__).parent / "fixtures" / "YourPlugin"

def test_with_fixtures(self, fixture_dir):
    """Test plugin with fixture files."""
    # Get all input fixture files
    input_files = list(fixture_dir.glob("input_*.adoc"))
    
    for input_file in input_files:
        expected_file = input_file.with_suffix(".expected")
        assert expected_file.exists(), f"Missing expected file for {input_file.name}"
        
        # Read fixture content
        input_content = input_file.read_text()
        expected_content = expected_file.read_text()
        
        # Process with plugin
        changed, result = process(str(input_file), input_content)
        
        # Verify results
        if input_content == expected_content:
            assert not changed, f"Plugin shouldn't change {input_file.name}"
        else:
            assert changed, f"Plugin should change {input_file.name}"
        
        assert result == expected_content, f"Output mismatch for {input_file.name}"
```

## 🔧 Advanced Plugin Features

### Environment Variable Support

Allow plugin configuration via environment variables:

```python
import os

def process(file_path, content):
    """Process with environment variable configuration."""
    # Check if plugin is enabled
    if not is_plugin_enabled():
        return False, content
    
    # Get configuration from environment
    custom_setting = os.environ.get('YOURPLUGIN_SETTING', 'default_value')
    
    # Apply transformations based on setting
    # ... plugin logic ...

def is_plugin_enabled():
    """Check if plugin is enabled via environment variable."""
    return os.environ.get('YOURPLUGIN_ENABLED', 'true').lower() == 'true'
```

### File Path Analysis

Use file path information for context-aware processing:

```python
from pathlib import Path

def process(file_path, content):
    """Process based on file path context."""
    path = Path(file_path)
    
    # Different behavior based on filename
    if path.name.endswith('_assembly.adoc'):
        return process_assembly_file(content)
    elif path.name.startswith('proc_'):
        return process_procedure_file(content)
    else:
        return process_generic_file(content)

def process_assembly_file(content):
    """Specific processing for assembly files."""
    # Assembly-specific logic
    return False, content

def process_procedure_file(content):
    """Specific processing for procedure files."""
    # Procedure-specific logic  
    return False, content

def process_generic_file(content):
    """Generic processing for other files."""
    # Generic logic
    return False, content
```

### Error Handling

Implement robust error handling:

```python
import logging

logger = logging.getLogger(__name__)

def process(file_path, content):
    """Process with comprehensive error handling."""
    try:
        return safe_process(file_path, content)
    except Exception as e:
        logger.warning(f"Plugin YourPlugin failed on {file_path}: {e}")
        return False, content  # Return original content on error

def safe_process(file_path, content):
    """Core processing logic with potential for exceptions."""
    # Validate input
    if not content.strip():
        return False, content
    
    # Process content
    modified_content = transform_content(content)
    changed = modified_content != content
    
    return changed, modified_content

def transform_content(content):
    """Transform content with potential for exceptions."""
    # Your transformation logic here
    # This might raise exceptions for malformed content
    return content
```

## 📊 Plugin Integration

### Working with File Utils

Leverage existing file utilities:

```python
from ..file_utils import load_directory_config, is_plugin_enabled

def process(file_path, content):
    """Process with integration to toolkit infrastructure."""
    # Check if this plugin should run
    if not is_plugin_enabled("YourPlugin"):
        return False, content
    
    # Use directory configuration if available
    config = load_directory_config()
    if config and should_skip_file(file_path, config):
        return False, content
    
    # Process content
    return transform_content(content)

def should_skip_file(file_path, config):
    """Check if file should be skipped based on configuration."""
    # Implement logic based on directory configuration
    return False
```

### Plugin Dependencies

Handle dependencies between plugins:

```python
def process(file_path, content):
    """Process with awareness of other plugins."""
    # Check if prerequisite transformations are present
    if not has_required_metadata(content):
        logger.info(f"Skipping {file_path}: required metadata missing")
        return False, content
    
    # Apply transformations
    return apply_transformations(content)

def has_required_metadata(content):
    """Check if content has metadata from prerequisite plugins."""
    return "Content Type:" in content
```

## 🚀 Plugin Distribution

### Packaging for Distribution

If creating plugins for distribution:

```python
# setup.py or pyproject.toml entry points
entry_points = {
    'asciidoc_dita_toolkit.plugins': [
        'YourPlugin = your_package.plugins:YourPlugin',
    ],
}
```

### Documentation Standards

Document your plugin thoroughly:

```python
"""
YourPlugin for AsciiDoc DITA Toolkit

This plugin transforms [specific content] by [specific method] to ensure
compatibility with [specific standard/requirement].

Configuration:
    Environment Variables:
        YOURPLUGIN_ENABLED: Enable/disable plugin (default: true)
        YOURPLUGIN_SETTING: Configure behavior (default: value)
    
    Configuration Files:
        .yourplugin.json: Local configuration
        ~/.yourplugin.json: Global configuration

Examples:
    Basic usage:
        Input:  = Document\\n\\nContent with pattern
        Output: = Document\\n\\nContent with transformed pattern
    
    With configuration:
        YOURPLUGIN_SETTING=custom asciidoc-dita-toolkit docs/

References:
    - External specification: https://example.com/spec
    - Related tools: https://example.com/tools
"""
```

## 🔍 Plugin Best Practices

### Performance

1. **Minimize regex compilation**: Compile patterns once at module level
2. **Avoid unnecessary work**: Check if changes are needed before processing
3. **Use efficient algorithms**: Prefer O(n) over O(n²) operations
4. **Process line-by-line** for large files when possible

```python
# Good: Compile regex once
PATTERN = re.compile(r'pattern_to_match')

def process(file_path, content):
    if not PATTERN.search(content):
        return False, content  # Quick exit if no matches
    
    # Process only if needed
    return True, PATTERN.sub('replacement', content)
```

### Memory Efficiency

1. **Process content as strings**: Avoid converting to complex data structures
2. **Use generators** for large content processing
3. **Clean up temporary variables**: Delete large variables when done

### Error Handling

1. **Fail gracefully**: Return original content on errors
2. **Log meaningful messages**: Help users understand what went wrong
3. **Validate inputs**: Check for malformed content before processing

### Testing

1. **Test edge cases**: Empty files, malformed content, etc.
2. **Use realistic fixtures**: Test with real AsciiDoc content
3. **Test performance**: Ensure plugins handle large files efficiently
4. **Test integration**: Verify plugin works with others

## 🔗 Related Documentation

- [Architecture Overview](../reference/architecture.md) - System design and plugin infrastructure
- [Testing Guide](testing.md) - Comprehensive testing strategies
- [Contributing Guide](contributing.md) - Development workflow and standards
- [Plugin Reference](../reference/plugins.md) - Available plugins and their behavior
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
