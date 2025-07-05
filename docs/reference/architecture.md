# Architecture Overview

Technical architecture and design principles of the AsciiDoc DITA Toolkit.

## 🏗️ System Architecture

### High-Level Design

```
┌─────────────────────┐
│   Command Line      │
│   Interface (CLI)   │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   Core Engine       │
│   (toolkit.py)      │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   File Utilities    │
│   (file_utils.py)   │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   Plugin System     │
│   (plugins/)        │
└─────────────────────┘
```

### Package Structure

The toolkit is organized as a Python package for PyPI distribution:

```
asciidoc-dita-toolkit/
├── asciidoc_dita_toolkit/          # Main package
│   ├── __init__.py
│   └── asciidoc_dita/              # Core module
│       ├── __init__.py
│       ├── toolkit.py              # CLI entry point & orchestration
│       ├── file_utils.py           # File operations & utilities
│       └── plugins/                # Plugin implementations
│           ├── __init__.py
│           ├── ContentType.py      # Content type detection
│           ├── EntityReference.py  # HTML entity conversion
│           └── DirectoryConfig.py  # Directory scoping (optional)
├── tests/                          # Test suite
│   ├── test_*.py                   # Unit tests
│   ├── fixtures/                   # Test fixtures
│   └── asciidoc_testkit.py        # Test utilities
├── docs/                           # Documentation
├── requirements.txt                # Runtime dependencies
├── requirements-dev.txt            # Development dependencies
├── pyproject.toml                  # Package configuration
└── Dockerfile*                     # Container configurations
```

## 🔧 Core Components

### CLI Interface (`toolkit.py`)

**Responsibilities**:
- Command-line argument parsing
- Plugin discovery and loading
- File path validation and processing orchestration
- Error handling and user feedback

**Key functions**:
- `main()` - Entry point for CLI
- `load_plugins()` - Dynamic plugin discovery
- `process_paths()` - Coordinate file processing

### File Utilities (`file_utils.py`)

**Responsibilities**:
- File system operations (find, read, write)
- Directory traversal and filtering
- Configuration management
- Path validation and sanitization

**Key functions**:
- `process_adoc_files()` - Main file processing coordinator
- `find_adoc_files()` - Recursive file discovery
- `load_directory_config()` - Configuration loading
- `validate_and_sanitize_path()` - Security and validation

### Plugin System (`plugins/`)

**Responsibilities**:
- Modular transformation logic
- Content analysis and modification
- Standardized plugin interface

**Plugin Interface**:
```python
class PluginBase:
    def process(self, file_path: str, content: str) -> tuple[bool, str]:
        """
        Process file content and return (changed, new_content)
        """
        pass
```

## 🔌 Plugin Architecture

### Plugin Discovery

Plugins are discovered automatically using Python's module system:

```python
# Dynamic plugin loading
import importlib
import pkgutil

def load_plugins():
    plugins = {}
    for _, name, _ in pkgutil.iter_modules(['plugins']):
        module = importlib.import_module(f'plugins.{name}')
        if hasattr(module, 'process'):
            plugins[name] = module
    return plugins
```

### Plugin Lifecycle

1. **Discovery**: Plugins found in `plugins/` directory
2. **Loading**: Python modules imported dynamically  
3. **Validation**: Check for required `process()` function
4. **Execution**: Called for each processed file
5. **Results**: Return tuple of `(changed: bool, content: str)`

### Plugin Interface Contract

All plugins must implement:

```python
def process(file_path, content):
    """
    Process AsciiDoc file content.
    
    Args:
        file_path (str): Path to the file being processed
        content (str): Current file content
        
    Returns:
        tuple: (changed: bool, new_content: str)
            changed: True if content was modified
            new_content: Modified content (or original if unchanged)
    """
```

## 📁 File Processing Pipeline

### Processing Flow

```
Input Files → Validation → Plugin Chain → Output Files
     ↓            ↓           ↓             ↓
  *.adoc    Path Safety   Transform    Modified *.adoc
            Check         Content      Content
```

### Detailed Pipeline

1. **File Discovery**
   - Recursive directory traversal
   - Filter for `.adoc` files
   - Apply directory configuration (if enabled)

2. **Path Validation**
   - Security checks (prevent path traversal)
   - Path sanitization
   - Existence verification

3. **Content Processing**
   - Read file content
   - Apply each enabled plugin sequentially
   - Track changes and modifications

4. **Output Generation**
   - Write modified content back to file
   - Preserve file permissions and metadata
   - Report processing results

### Error Handling Strategy

```
┌─────────────────┐
│ File Level      │ ← Individual file errors don't stop processing
│ Error Handling  │
└─────────────────┘
┌─────────────────┐
│ Plugin Level    │ ← Plugin errors are isolated
│ Error Handling  │
└─────────────────┘
┌─────────────────┐
│ System Level    │ ← Critical errors stop execution
│ Error Handling  │
└─────────────────┘
```

## 🔒 Security Architecture

### Path Traversal Protection

```python
def validate_and_sanitize_path(path):
    """
    Validate and sanitize file paths to prevent security issues.
    
    - Resolve symbolic links
    - Normalize path separators
    - Check for path traversal attempts
    - Validate against allowed patterns
    """
    resolved_path = Path(path).resolve()
    # Additional security checks...
    return resolved_path
```

### Input Validation

- **File paths**: Validated and sanitized
- **File content**: Encoding validation (UTF-8)
- **Configuration**: JSON schema validation
- **Plugin input**: Type checking and bounds validation

## 📊 Performance Considerations

### File Processing Optimization

- **Lazy loading**: Files read only when needed
- **Memory efficiency**: Process files individually, not all at once
- **Path caching**: Cache resolved paths to avoid repeated filesystem calls
- **Early termination**: Skip files that don't need processing

### Plugin Performance

- **Stateless design**: Plugins don't maintain state between files
- **Efficient algorithms**: O(n) complexity for most operations
- **Minimal dependencies**: Reduce import overhead

## 🧪 Testing Architecture

### Test Structure

```
tests/
├── test_toolkit.py         # CLI and integration tests
├── test_file_utils.py      # File utilities tests
├── test_ContentType.py     # ContentType plugin tests
├── test_EntityReference.py # EntityReference plugin tests
├── test_DirectoryConfig.py # DirectoryConfig plugin tests
├── fixtures/               # Test fixtures
│   ├── ContentType/        # Plugin-specific fixtures
│   ├── EntityReference/
│   └── DirectoryConfig/
└── asciidoc_testkit.py    # Shared test utilities
```

### Testing Strategy

- **Unit tests**: Individual component testing
- **Integration tests**: End-to-end workflow testing
- **Fixture-based testing**: Real AsciiDoc content samples
- **Parametrized tests**: Multiple scenarios with same test logic

## 🚀 Deployment Architecture

### Distribution Methods

1. **PyPI Package**
   - Standard Python package distribution
   - Dependency management via pip
   - Cross-platform compatibility

2. **Container Images**
   - Production image (~50MB): Minimal runtime
   - Development image (~200MB): Includes dev tools
   - Multi-platform support (linux/amd64, linux/arm64)

3. **Source Installation**
   - Development mode installation
   - Direct from Git repository
   - Editable installation for contributors

### Container Architecture

```dockerfile
# Multi-stage build for production image
FROM python:3.11-alpine AS builder
# Install dependencies and package

FROM python:3.11-alpine AS production
# Copy only necessary files
# Minimize attack surface and size
```

## 🔄 Extension Points

### Adding New Plugins

1. **Create plugin file**: `plugins/NewPlugin.py`
2. **Implement interface**: `process(file_path, content)` function
3. **Add tests**: `tests/test_NewPlugin.py`
4. **Create fixtures**: `tests/fixtures/NewPlugin/`
5. **Update documentation**

### Custom File Discovery

Plugins can implement custom file discovery:

```python
from ..file_utils import load_directory_config

def custom_file_discovery(directory_path):
    config = load_directory_config()
    # Custom logic using configuration
    return filtered_files
```

## 📚 Design Principles

### Code Quality

- **Single Responsibility**: Each module has one clear purpose
- **Separation of Concerns**: Clear boundaries between components
- **DRY (Don't Repeat Yourself)**: Shared utilities in `file_utils.py`
- **SOLID Principles**: Especially Open/Closed for plugin extensibility

### User Experience

- **Fail Fast**: Early validation and clear error messages
- **Progressive Disclosure**: `--dry-run` before actual changes
- **Consistent Interface**: Uniform CLI patterns across all operations
- **Helpful Output**: Verbose mode for debugging, quiet mode for automation

### Maintainability

- **Clear Interfaces**: Well-defined contracts between components
- **Comprehensive Testing**: High test coverage with realistic scenarios
- **Documentation**: Code comments and external documentation
- **Version Compatibility**: Backward-compatible changes where possible

## 🔗 Related Documentation

- [Plugin Development Guide](../development/plugin-development.md) - Building custom plugins
- [Contributing Guide](../development/contributing.md) - Development setup and practices
- [Plugin Reference](plugins.md) - Available plugins and their behavior
- [Configuration Reference](configuration.md) - Configuration options and files
