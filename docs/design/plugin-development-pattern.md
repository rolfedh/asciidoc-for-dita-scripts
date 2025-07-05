# Plugin Development Pattern

Technical specification for the standardized plugin development pattern in the AsciiDoc DITA Toolkit.

## 🎯 Pattern Overview

This document establishes the standardized pattern for developing plugins and their test infrastructure. This pattern was refined through the development of ContentType, EntityReference, and DirectoryConfig plugins.

### Pattern Goals

- **Consistency**: Uniform plugin architecture across the toolkit
- **Testability**: Robust testing with comprehensive fixture management
- **Maintainability**: Clear separation of concerns and modular design
- **Compliance**: Adherence to external specifications (e.g., Vale rules, DITA standards)

## 📁 Directory Structure Pattern

```
asciidoc_dita_toolkit/
├── asciidoc_dita/
│   └── plugins/
│       ├── __init__.py
│       ├── PluginName.py              # Plugin implementation
│       └── AnotherPlugin.py           # Additional plugins
└── tests/
    ├── test_PluginName.py             # Unit tests
    ├── test_AnotherPlugin.py          # More plugin tests
    ├── asciidoc_testkit.py            # Shared test utilities
    └── fixtures/
        ├── PluginName/                # Plugin-specific fixtures
        │   ├── input_case1.adoc       # Input test file
        │   ├── input_case1.expected   # Expected output (colocated)
        │   ├── input_case2.adoc       # Additional test case
        │   ├── input_case2.expected   # Expected output
        │   └── vale.ini               # External tool config (if needed)
        └── AnotherPlugin/             # Another plugin's fixtures
            ├── input_basic.adoc
            ├── input_basic.expected
            └── ...
```

## 🔧 Plugin Implementation Pattern

### Standard Plugin Template

```python
"""
Plugin for the AsciiDoc DITA toolkit: PluginName

Brief description of what this plugin does and its purpose in the DITA workflow.

References:
- External specification: https://example.com/spec
- Related Vale rules: https://github.com/example/vale-rules
- DITA standard: https://docs.oasis-open.org/dita/
"""

__description__ = "Brief description for CLI --list-plugins output"
__version__ = "1.0.0"
__author__ = "Developer Name"

import re
import logging
from pathlib import Path

# Module-level constants
PATTERN_REGEX = re.compile(r'pattern_to_match', re.MULTILINE)
REPLACEMENT_MAP = {
    'find_pattern': 'replace_pattern',
    # Additional mappings
}

logger = logging.getLogger(__name__)

def process(file_path, content):
    """
    Main plugin entry point called by the toolkit.
    
    Args:
        file_path (str): Path to the file being processed
        content (str): Current file content as string
        
    Returns:
        tuple[bool, str]: (changed, new_content)
            changed: True if content was modified
            new_content: Modified content or original if unchanged
    """
    try:
        return _safe_process(file_path, content)
    except Exception as e:
        logger.warning(f"Plugin PluginName failed on {file_path}: {e}")
        return False, content  # Fail gracefully

def _safe_process(file_path, content):
    """
    Core processing logic with potential for exceptions.
    
    This is separated from the main process() function to allow
    for comprehensive error handling.
    """
    # Early exit if no work needed
    if not _needs_processing(content):
        return False, content
    
    # Apply transformations
    modified_content = _apply_transformations(file_path, content)
    changed = modified_content != content
    
    return changed, modified_content

def _needs_processing(content):
    """
    Quick check to determine if content needs processing.
    
    This optimization avoids expensive processing when no
    changes are needed.
    """
    return PATTERN_REGEX.search(content) is not None

def _apply_transformations(file_path, content):
    """
    Apply plugin-specific transformations to content.
    
    Args:
        file_path: File path for context-aware processing
        content: Content to transform
        
    Returns:
        str: Transformed content
    """
    modified_content = content
    
    # Apply transformations based on plugin logic
    for pattern, replacement in REPLACEMENT_MAP.items():
        modified_content = re.sub(pattern, replacement, modified_content)
    
    return modified_content
```

### Error Handling Pattern

```python
def process(file_path, content):
    """Plugin with comprehensive error handling."""
    try:
        # Validate inputs
        if not content or not content.strip():
            return False, content
            
        # Process content
        return _process_content(file_path, content)
        
    except UnicodeError as e:
        logger.error(f"Encoding error in {file_path}: {e}")
        return False, content
    except Exception as e:
        logger.warning(f"Unexpected error in plugin: {e}")
        return False, content

def _process_content(file_path, content):
    """Core processing with specific error handling."""
    # Plugin-specific logic that might raise exceptions
    pass
```

## 🧪 Testing Pattern

### Test File Structure

```python
"""
Test suite for PluginName following the standard testing pattern.

This module tests all aspects of the PluginName plugin including:
- Basic functionality and transformations
- Edge cases and error conditions  
- Integration with toolkit infrastructure
- Performance with large content
"""

import pytest
from pathlib import Path
from asciidoc_dita_toolkit.asciidoc_dita.plugins.PluginName import process

class TestPluginName:
    """Main test class for PluginName plugin."""
    
    def test_no_changes_when_not_needed(self):
        """Test plugin returns unchanged content when no transformations needed."""
        content = "= Document\n\nContent that doesn't need changes."
        changed, result = process("test.adoc", content)
        
        assert not changed
        assert result == content
    
    def test_basic_transformation(self):
        """Test core plugin functionality."""
        input_content = "= Document\n\nContent with pattern_to_match."
        expected_content = "= Document\n\nContent with replace_pattern."
        
        changed, result = process("test.adoc", input_content)
        
        assert changed
        assert result == expected_content
    
    def test_multiple_transformations(self):
        """Test plugin handles multiple transformations in same content."""
        input_content = "pattern_to_match and pattern_to_match again"
        expected_content = "replace_pattern and replace_pattern again"
        
        changed, result = process("test.adoc", input_content)
        
        assert changed
        assert result == expected_content
    
    def test_empty_content(self):
        """Test plugin handles empty content gracefully."""
        changed, result = process("test.adoc", "")
        
        assert not changed
        assert result == ""
    
    def test_malformed_content(self):
        """Test plugin handles malformed content without crashing."""
        malformed_content = "Invalid\x00content\nwith\nbinary\x01data"
        
        # Should not crash, may or may not change content
        changed, result = process("test.adoc", malformed_content)
        assert isinstance(result, str)
    
    @pytest.mark.parametrize("input_text,expected_output,should_change", [
        ("No patterns here", "No patterns here", False),
        ("pattern_to_match", "replace_pattern", True),
        ("Multiple pattern_to_match patterns pattern_to_match", 
         "Multiple replace_pattern patterns replace_pattern", True),
    ])
    def test_parametrized_cases(self, input_text, expected_output, should_change):
        """Test various input/output combinations."""
        changed, result = process("test.adoc", input_text)
        
        assert changed == should_change
        assert result == expected_output

class TestPluginNameFixtures:
    """Test class for fixture-based testing."""
    
    @pytest.fixture
    def fixture_dir(self):
        """Return path to plugin test fixtures."""
        return Path(__file__).parent / "fixtures" / "PluginName"
    
    def test_all_fixtures(self, fixture_dir):
        """Test plugin against all fixture files."""
        input_files = list(fixture_dir.glob("input_*.adoc"))
        assert input_files, "No fixture files found"
        
        for input_file in input_files:
            expected_file = input_file.with_suffix(".expected")
            assert expected_file.exists(), f"Missing expected file: {expected_file.name}"
            
            # Read fixture content
            input_content = input_file.read_text(encoding='utf-8')
            expected_content = expected_file.read_text(encoding='utf-8')
            
            # Process with plugin
            changed, result = process(str(input_file), input_content)
            
            # Verify results
            if input_content == expected_content:
                assert not changed, f"Plugin shouldn't change {input_file.name}"
            else:
                assert changed, f"Plugin should change {input_file.name}"
            
            assert result == expected_content, f"Output mismatch in {input_file.name}"

class TestPluginNamePerformance:
    """Performance tests for the plugin."""
    
    def test_large_content_performance(self):
        """Test plugin performance with large content."""
        import time
        
        # Create large content
        large_content = "= Document\n\n" + ("Content paragraph.\n\n" * 1000)
        
        start_time = time.time()
        changed, result = process("large.adoc", large_content)
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 1.0, "Plugin too slow on large content"
    
    def test_memory_efficiency(self):
        """Test plugin memory usage."""
        import tracemalloc
        
        tracemalloc.start()
        
        # Process moderately large content
        content = "= Document\n\n" + ("pattern_to_match paragraph.\n\n" * 5000)
        changed, result = process("memory_test.adoc", content)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Should not use excessive memory (threshold may need adjustment)
        assert peak < 10 * 1024 * 1024, f"Plugin used too much memory: {peak} bytes"
```

## 📋 Fixture Management Pattern

### Fixture Naming Convention

```
fixtures/PluginName/
├── input_basic.adoc              # Basic functionality test
├── input_basic.expected          # Expected output for basic test
├── input_edge_case.adoc          # Edge case testing
├── input_edge_case.expected      # Expected output for edge case
├── input_no_change.adoc          # Content that shouldn't change
├── input_no_change.expected      # Should be identical to input
├── input_malformed.adoc          # Malformed content test
├── input_malformed.expected      # Expected handling of malformed content
└── vale.ini                      # External tool configuration (if applicable)
```

### Fixture Content Guidelines

**Input files should represent**:
- Typical real-world content
- Edge cases and boundary conditions
- Malformed or problematic content
- Content that should not be changed

**Expected files should**:
- Show exact expected output
- Preserve all formatting and whitespace
- Be identical to input files when no changes expected

### Fixture Validation

```python
def test_fixture_completeness(fixture_dir):
    """Ensure all input fixtures have corresponding expected files."""
    input_files = list(fixture_dir.glob("input_*.adoc"))
    
    for input_file in input_files:
        expected_file = input_file.with_suffix(".expected")
        assert expected_file.exists(), f"Missing expected file: {expected_file.name}"
        
        # Verify files are not empty
        assert input_file.stat().st_size > 0, f"Empty input file: {input_file.name}"
        assert expected_file.stat().st_size > 0, f"Empty expected file: {expected_file.name}"
```

## 🔄 Integration Pattern

### Plugin Discovery

Plugins are discovered automatically by the toolkit:

```python
# In toolkit.py - Plugin discovery pattern
import importlib
import pkgutil

def discover_plugins():
    """Discover all available plugins."""
    plugins = {}
    
    # Import plugins package
    import asciidoc_dita_toolkit.asciidoc_dita.plugins as plugins_package
    
    # Iterate through all modules in plugins package
    for finder, name, ispkg in pkgutil.iter_modules(plugins_package.__path__):
        if not ispkg:  # Only load modules, not packages
            try:
                module = importlib.import_module(f"{plugins_package.__name__}.{name}")
                if hasattr(module, 'process'):
                    plugins[name] = module
            except ImportError as e:
                logger.warning(f"Failed to load plugin {name}: {e}")
    
    return plugins
```

### Plugin Execution Pattern

```python
def execute_plugin(plugin_module, file_path, content):
    """Execute a plugin following the standard pattern."""
    try:
        # All plugins must implement this interface
        changed, new_content = plugin_module.process(file_path, content)
        
        # Validate return values
        if not isinstance(changed, bool):
            raise ValueError(f"Plugin returned non-boolean changed value: {type(changed)}")
        if not isinstance(new_content, str):
            raise ValueError(f"Plugin returned non-string content: {type(new_content)}")
            
        return changed, new_content
        
    except Exception as e:
        logger.error(f"Plugin {plugin_module.__name__} failed: {e}")
        return False, content  # Return original content on error
```

## 📊 Performance Pattern

### Optimization Guidelines

1. **Compile regex patterns once** at module level
2. **Use early exit strategies** when no processing needed
3. **Minimize string operations** - avoid unnecessary copying
4. **Process line-by-line** for very large files when possible

```python
# Good: Module-level compilation
ENTITY_PATTERN = re.compile(r'&(\w+);')

def process(file_path, content):
    # Good: Early exit
    if '&' not in content:
        return False, content
    
    # Process only when needed
    return True, ENTITY_PATTERN.sub(replace_entity, content)

def replace_entity(match):
    """Replace single entity match."""
    entity = match.group(1)
    return ENTITY_MAP.get(entity, match.group(0))
```

## 🔒 Security Pattern

### Input Validation

```python
def process(file_path, content):
    """Process with input validation."""
    # Validate file path
    if not isinstance(file_path, str) or not file_path:
        logger.warning("Invalid file path provided")
        return False, content
    
    # Validate content
    if not isinstance(content, str):
        logger.warning("Invalid content type provided")
        return False, content
    
    # Check for binary content
    try:
        content.encode('utf-8')
    except UnicodeEncodeError:
        logger.warning(f"Binary content detected in {file_path}")
        return False, content
    
    return _process_validated_content(file_path, content)
```

## 🔗 Related Documentation

- [Plugin Development Guide](../development/plugin-development.md) - Comprehensive development guide
- [Architecture Overview](../reference/architecture.md) - System architecture and design
- [Testing Guide](../development/testing.md) - Testing strategies and best practices
- [Plugin Reference](../reference/plugins.md) - Available plugins and their functionality
