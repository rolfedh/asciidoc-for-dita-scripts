# Testing Guide

Comprehensive testing guide for the AsciiDoc DITA Toolkit development.

## 🧪 Testing Overview

The toolkit uses a comprehensive testing strategy with multiple types of tests to ensure reliability and maintainability.

### Test Types

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows end-to-end
- **Fixture Tests**: Test with real AsciiDoc content samples
- **Regression Tests**: Ensure fixes don't break existing functionality

### Test Structure

```
tests/
├── test_toolkit.py         # CLI and main integration tests
├── test_file_utils.py      # File utilities and core functions
├── test_ContentType.py     # ContentType plugin tests  
├── test_EntityReference.py # EntityReference plugin tests
├── test_DirectoryConfig.py # DirectoryConfig plugin tests
├── fixtures/               # Test fixture files
│   ├── ContentType/        # Plugin-specific test data
│   ├── EntityReference/
│   └── DirectoryConfig/
└── asciidoc_testkit.py    # Shared test utilities
```

## 🚀 Running Tests

### Quick Test Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_ContentType.py

# Run specific test method
pytest tests/test_ContentType.py::test_content_type_detection

# Run tests with coverage
pytest --cov=asciidoc_dita_toolkit

# Run tests in parallel (faster)
pytest -n auto
```

### Development Workflow

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install in development mode  
pip install -e .

# 3. Install test dependencies
pip install -r requirements-dev.txt

# 4. Run tests before making changes
pytest -v

# 5. Make your changes...

# 6. Run tests again to verify
pytest -v

# 7. Run specific tests for your changes
pytest tests/test_YourPlugin.py -v
```

### Continuous Testing

```bash
# Watch for file changes and re-run tests
pytest-watch

# Or use pytest-xdist for parallel execution
pytest -n auto --looponfail
```

## 📝 Writing Tests

### Test Organization

Each plugin should have its own test file following this pattern:

```python
# tests/test_YourPlugin.py
import pytest
from pathlib import Path
from asciidoc_dita_toolkit.asciidoc_dita.plugins import YourPlugin

class TestYourPlugin:
    """Test suite for YourPlugin functionality."""
    
    def test_basic_functionality(self):
        """Test basic plugin operation."""
        # Test implementation
        pass
        
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test implementation
        pass
        
    def test_with_fixtures(self):
        """Test with real AsciiDoc content."""
        # Test implementation
        pass
```

### Using Test Fixtures

#### File-Based Fixtures

```python
# tests/test_YourPlugin.py
import pytest
from pathlib import Path

@pytest.fixture
def fixture_dir():
    """Return path to plugin fixtures."""
    return Path(__file__).parent / "fixtures" / "YourPlugin"

def test_with_file_fixture(fixture_dir):
    """Test using file fixtures."""
    input_file = fixture_dir / "input_example.adoc"
    expected_file = fixture_dir / "input_example.expected"
    
    # Read input and expected content
    input_content = input_file.read_text()
    expected_content = expected_file.read_text()
    
    # Process with plugin
    changed, result = YourPlugin.process(str(input_file), input_content)
    
    # Verify results
    assert changed
    assert result == expected_content
```

#### Parameterized Tests

```python
@pytest.mark.parametrize("input_content,expected_content,should_change", [
    ("= Simple Document\n\nContent.", "= Simple Document\n\nContent.", False),
    ("= Document\n\n&amp; symbol", "= Document\n\n{amp} symbol", True),
    ("= Document\n\n&hellip;", "= Document\n\n{hellip}", True),
])
def test_entity_conversion(input_content, expected_content, should_change):
    """Test entity conversion with multiple scenarios."""
    changed, result = EntityReference.process("test.adoc", input_content)
    assert changed == should_change
    assert result == expected_content
```

### Test Utilities

Use the shared test utilities in `asciidoc_testkit.py`:

```python
# tests/asciidoc_testkit.py
from pathlib import Path
import tempfile
import shutil

class TestFixtures:
    """Utilities for working with test fixtures."""
    
    @staticmethod
    def create_temp_adoc_file(content, suffix=".adoc"):
        """Create temporary AsciiDoc file with content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(content)
            return Path(f.name)
    
    @staticmethod
    def create_test_directory(files_dict):
        """Create temporary directory with multiple test files."""
        temp_dir = Path(tempfile.mkdtemp())
        for filename, content in files_dict.items():
            (temp_dir / filename).write_text(content)
        return temp_dir

# Usage in tests
def test_with_temp_files():
    files = {
        "doc1.adoc": "= Document 1\n\nContent with &amp; entity.",
        "doc2.adoc": "= Document 2\n\nMore content.",
    }
    test_dir = TestFixtures.create_test_directory(files)
    
    # Test with the temporary directory
    # ... test logic ...
    
    # Cleanup
    shutil.rmtree(test_dir)
```

## 🔧 Plugin Testing

### Plugin Test Template

```python
# tests/test_YourPlugin.py
import pytest
from pathlib import Path
from asciidoc_dita_toolkit.asciidoc_dita.plugins.YourPlugin import process

class TestYourPlugin:
    """Test suite for YourPlugin."""
    
    def test_no_changes_needed(self):
        """Test content that doesn't need modification."""
        content = "= Simple Document\n\nAlready correct content."
        changed, result = process("test.adoc", content)
        assert not changed
        assert result == content
    
    def test_basic_transformation(self):
        """Test basic plugin transformation."""
        input_content = "= Document\n\nContent needing transformation."
        expected_content = "= Document\n\nTransformed content."
        
        changed, result = process("test.adoc", input_content)
        assert changed
        assert result == expected_content
    
    def test_error_handling(self):
        """Test plugin error handling."""
        invalid_content = "Malformed AsciiDoc content..."
        
        # Plugin should handle gracefully
        changed, result = process("test.adoc", invalid_content)
        # Assert appropriate behavior
    
    @pytest.mark.parametrize("filename,expected_type", [
        ("procedure_example.adoc", "procedure"),
        ("concept_example.adoc", "concept"),
        ("assembly_example.adoc", "assembly"),
    ])
    def test_filename_patterns(self, filename, expected_type):
        """Test filename-based behavior."""
        content = "= Example Document\n\nContent."
        changed, result = process(filename, content)
        # Assert expected behavior based on filename
```

### Fixture Management

#### Creating Test Fixtures

```bash
# Create fixture directory
mkdir -p tests/fixtures/YourPlugin

# Create input file
cat > tests/fixtures/YourPlugin/input_example.adoc << 'EOF'
= Example Document

Content that needs processing.

* List item with &amp; entity
* Another item with &hellip; 
EOF

# Create expected output file
cat > tests/fixtures/YourPlugin/input_example.expected << 'EOF'
= Example Document

Content that needs processing.

* List item with {amp} entity
* Another item with {hellip}
EOF
```

#### Fixture Validation

```python
def test_fixture_completeness():
    """Ensure all input fixtures have corresponding expected files."""
    fixture_dir = Path(__file__).parent / "fixtures" / "YourPlugin"
    input_files = list(fixture_dir.glob("input_*.adoc"))
    
    for input_file in input_files:
        expected_file = input_file.with_suffix(".expected")
        assert expected_file.exists(), f"Missing expected file for {input_file.name}"
```

## 🔍 Test Coverage

### Measuring Coverage

```bash
# Generate coverage report
pytest --cov=asciidoc_dita_toolkit --cov-report=html

# View coverage report
open htmlcov/index.html

# Get terminal coverage summary
pytest --cov=asciidoc_dita_toolkit --cov-report=term-missing
```

### Coverage Goals

- **Overall coverage**: 90%+
- **Core utilities**: 95%+
- **Plugin logic**: 85%+
- **Error handling**: 80%+

### Coverage Analysis

```bash
# Generate detailed coverage report
coverage run -m pytest
coverage report -m
coverage html

# Check coverage for specific modules
coverage report --include="*/plugins/*"
```

## 🐛 Debugging Tests

### Debug Tools

```python
# Add debugging to tests
import pdb; pdb.set_trace()  # Python debugger

# Or use pytest debugging
pytest --pdb  # Drop to debugger on failures

# Capture print statements
pytest -s  # Don't capture stdout

# Run single test with maximum verbosity
pytest tests/test_YourPlugin.py::test_specific_case -vvv -s
```

### Test Debugging Workflow

1. **Isolate the failing test**:
   ```bash
   pytest tests/test_YourPlugin.py::test_failing_case -v
   ```

2. **Add debug output**:
   ```python
   def test_failing_case():
       # Add debugging
       print(f"Input: {input_content}")
       print(f"Expected: {expected_content}")
       print(f"Actual: {result}")
       assert result == expected_content
   ```

3. **Run with stdout capture disabled**:
   ```bash
   pytest tests/test_YourPlugin.py::test_failing_case -s
   ```

4. **Use debugger if needed**:
   ```python
   import pdb; pdb.set_trace()
   ```

## 🔄 Continuous Integration

### GitHub Actions Testing

The toolkit uses GitHub Actions for automated testing. See `.github/workflows/` for:

- **Pull Request Tests**: Run on every PR
- **Compatibility Tests**: Test across Python versions
- **Container Tests**: Verify Docker builds
- **Coverage Reports**: Track coverage changes

### Local CI Simulation

```bash
# Simulate CI environment locally
export CI=true
export PYTHONPATH=.

# Run tests as CI would
python -m pytest tests/ -v --cov=asciidoc_dita_toolkit
```

## 📊 Performance Testing

### Basic Performance Tests

```python
import time
import pytest

def test_plugin_performance():
    """Test plugin performance on large content."""
    large_content = "= Document\n\n" + "Content paragraph.\n\n" * 1000
    
    start_time = time.time()
    changed, result = YourPlugin.process("test.adoc", large_content)
    end_time = time.time()
    
    # Should process within reasonable time (e.g., 1 second)
    assert (end_time - start_time) < 1.0
```

### Memory Usage Tests

```python
import tracemalloc

def test_memory_usage():
    """Test plugin memory usage."""
    tracemalloc.start()
    
    # Process large content
    large_content = "= Document\n\n" + "Content paragraph.\n\n" * 10000
    changed, result = YourPlugin.process("test.adoc", large_content)
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Should not use excessive memory (adjust threshold as needed)
    assert peak < 50 * 1024 * 1024  # 50MB
```

## 🚀 Best Practices

### Test Design

1. **Test behavior, not implementation**
2. **Use descriptive test names**
3. **One assertion per test (when possible)**
4. **Test edge cases and error conditions**
5. **Use fixtures for common test data**

### Test Maintenance

1. **Keep tests simple and readable**
2. **Update tests when changing functionality**
3. **Remove obsolete tests**
4. **Regular fixture cleanup and updates**

### Performance

1. **Use pytest-xdist for parallel execution**
2. **Mock external dependencies**
3. **Minimize fixture setup/teardown time**
4. **Profile slow tests and optimize**

## 🔗 Related Documentation

- [Contributing Guide](contributing.md) - Development setup and workflow
- [Plugin Development](plugin-development.md) - Creating new plugins
- [Architecture Overview](../reference/architecture.md) - System design
- [Troubleshooting](../user-guides/troubleshooting.md) - Common issues
