# ContentType Plugin Refactoring

## Overview

The ContentType plugin has been comprehensively refactored to address the issues identified in [#94](https://github.com/your-repo/issues/94). The refactoring focuses on improving separation of concerns, testability, and extensibility while maintaining backward compatibility.

## Key Improvements

### 1. Separation of Concerns

**Before**: The original `ContentType.py` mixed user interaction, file I/O, and business logic in a single monolithic file.

**After**: The functionality is now split into focused modules:

- `content_type_detector.py`: Core detection algorithms and configuration
- `ui_interface.py`: User interface abstraction layer
- `content_type_processor.py`: File processing and I/O operations
- `ContentType.py`: Main plugin coordination and CLI integration

### 2. Improved Testability

**Before**: Heavy use of `print()` and `input()` made automated testing difficult.

**After**: 
- Dependency injection allows mocking of file operations and user interface
- Abstract `UIInterface` enables different UI implementations (console, batch, test)
- Comprehensive unit tests cover all components
- Integration tests verify the complete workflow

### 3. Enhanced Extensibility

**Before**: Content type detection patterns were hardcoded throughout the plugin.

**After**:
- Configurable `ContentTypeConfig` class for detection patterns
- Easy to add new content types without modifying core code
- Custom configurations can be created for organization-specific patterns
- Plugin architecture supports different UI modes (interactive, batch, test)

### 4. Better Error Handling and Logging

**Before**: All output went to console with print statements.

**After**:
- Proper logging with configurable levels (DEBUG, INFO, WARNING, ERROR)
- Structured error handling with proper exception propagation
- User-friendly error messages through UI abstraction

### 5. Code Deduplication

**Before**: Logic for attribute detection and updating was repeated.

**After**: 
- Centralized detection logic in `ContentTypeDetector`
- Reusable helper functions for common operations
- Single source of truth for content type patterns

## Architecture

```
ContentType.py (Main Plugin)
├── content_type_detector.py (Detection Logic)
│   ├── ContentTypeConfig (Configuration)
│   ├── ContentTypeDetector (Detection Algorithms)
│   └── Data Classes (ContentTypeAttribute, DetectionResult)
├── ui_interface.py (User Interface)
│   ├── UIInterface (Abstract Base)
│   ├── ConsoleUI (Interactive CLI)
│   ├── BatchUI (Non-interactive)
│   └── TestUI (Testing Support)
└── content_type_processor.py (File Processing)
    └── ContentTypeProcessor (File I/O and Processing)
```

## New Features

### Batch Mode
```bash
python -m asciidoc_dita_toolkit ContentType --batch
```
Process files without user interaction, using automatic detection and fallback to TBD.

### Verbose Logging
```bash
python -m asciidoc_dita_toolkit ContentType --verbose
```
Enable detailed logging for debugging and troubleshooting.

### Quiet Mode
```bash
python -m asciidoc_dita_toolkit ContentType --quiet
```
Suppress non-error output for batch processing.

### Custom Configuration
```python
from asciidoc_dita_toolkit.asciidoc_dita.plugins.content_type_detector import ContentTypeConfig
from asciidoc_dita_toolkit.asciidoc_dita.plugins.ContentType import create_processor

# Create custom configuration
config = ContentTypeConfig(
    filename_prefixes={
        ("tut_", "tutorial-"): "TUTORIAL",
        ("api_", "api-"): "API_REFERENCE",
    },
    title_patterns={
        "TUTORIAL": [r'^(Tutorial|Learning|Step-by-step)'],
        "API_REFERENCE": [r'(api|endpoint|method)'],
    },
    content_patterns={
        "TUTORIAL": [r'^\s*Step\s+\d+:'],
        "API_REFERENCE": [r'^\s*GET\s+/', r'^\s*POST\s+/'],
    }
)

# Create processor with custom configuration
processor = create_processor(batch_mode=True, config=config)
```

## Testing

The refactored plugin includes comprehensive test coverage:

### Unit Tests
- `TestContentTypeDetector`: Tests for detection algorithms
- `TestUIInterface`: Tests for UI implementations
- `TestContentTypeProcessor`: Tests for file processing
- `TestContentTypeConfig`: Tests for configuration handling

### Integration Tests
- End-to-end workflow testing
- File I/O mocking and verification
- UI interaction testing

### Running Tests
```bash
python -m pytest tests/test_content_type_plugin.py -v
```

## Performance Improvements

### Optimized Detection
- Filename detection is prioritized (fastest)
- Content analysis is optimized for large files
- Lazy loading of file content where possible

### Reduced Memory Usage
- Streaming file processing for large files
- Efficient regex compilation and caching
- Minimal memory footprint for batch processing

## Backward Compatibility

The refactored plugin maintains full backward compatibility:

- All existing CLI arguments work unchanged
- Same detection algorithms and patterns
- Same output format and file modifications
- Existing deprecated attribute formats are still supported

## Migration Guide

### For Users
No changes required. The plugin works exactly as before with the same command-line interface.

### For Developers
If you've customized the plugin or want to extend it:

1. **Custom Detection Patterns**: Use `ContentTypeConfig` instead of modifying source code
2. **Testing**: Use `TestUI` and dependency injection for automated testing
3. **Batch Processing**: Use `BatchUI` for non-interactive workflows
4. **Logging**: Use the logging module instead of print statements

## Example Usage

### Basic Usage (unchanged)
```bash
python -m asciidoc_dita_toolkit ContentType docs/
```

### New Batch Mode
```bash
python -m asciidoc_dita_toolkit ContentType --batch docs/
```

### With Custom Configuration
```python
from asciidoc_dita_toolkit.asciidoc_dita.plugins.content_type_example_config import create_custom_processor

processor = create_custom_processor(batch_mode=True)
success = processor.process_file("path/to/file.adoc")
```

## Benefits Realized

1. **Improved Maintainability**: Code is now organized into focused, single-responsibility modules
2. **Better Testability**: Comprehensive test coverage with mocked dependencies
3. **Enhanced Extensibility**: Easy to add new content types and detection patterns
4. **Reduced Code Duplication**: Centralized logic and reusable components
5. **Better Error Handling**: Proper logging and user-friendly error messages
6. **Performance Optimization**: Efficient algorithms and memory usage
7. **Future-Proof Architecture**: Plugin can easily support new UI modes (GUI, web, etc.)

## Future Enhancements

The refactored architecture enables future improvements:

1. **Configuration Files**: YAML/JSON configuration for detection patterns
2. **Machine Learning**: AI-powered content type detection
3. **GUI Interface**: Desktop application using the same core logic
4. **Web Interface**: Browser-based content type management
5. **Plugins**: Third-party extensions for custom content types
6. **Metrics**: Analytics and reporting on content type usage

## Issues Resolved

This refactoring addresses all issues identified in #94:

- ✅ **Code Duplication**: Eliminated through centralized logic
- ✅ **Separation of Concerns**: Clear module boundaries and responsibilities
- ✅ **Testability**: Comprehensive test suite with dependency injection
- ✅ **Extensibility**: Configurable patterns and pluggable architecture
- ✅ **Performance**: Optimized algorithms and memory usage
- ✅ **Logging**: Proper logging with configurable levels

The ContentType plugin is now production-ready with enhanced maintainability, testability, and extensibility while preserving all existing functionality.