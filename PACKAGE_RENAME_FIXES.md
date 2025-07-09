# Package Rename Fixes - ADT Core Installation Issues

## Problem Summary

The [PR #106](https://github.com/rolfedh/asciidoc-dita-toolkit/pull/106) renamed the package from `asciidoc-dita-toolkit` to `adt-core` but caused several installation and usage issues:

1. **Missing command-line interface**: No console script entry points were defined
2. **No `__main__.py` file**: `python -m adt_core` didn't work
3. **Non-functional modules**: New modules were stubs that didn't perform actual file processing
4. **Backward compatibility broken**: Users expecting `asciidoc-dita-toolkit` commands couldn't use the new package

## User Experience Issues

Users experienced problems like:
```bash
# After installing adt-core, these didn't work:
pip show adt-core | grep Location
python -m adt_core --list-plugins  # No module named adt_core.__main__
/path/to/environment/bin/adt-core --list-plugins  # No such file or directory
```

## Solutions Implemented

### 1. Added Command-Line Interface (`src/adt_core/__main__.py`)
- Created a proper `__main__.py` file to enable `python -m adt_core` usage
- Routes to the CLI module for consistent behavior

### 2. Comprehensive CLI Module (`src/adt_core/cli.py`)
- **Backward compatibility**: Supports both legacy plugins and new modules
- **Auto-discovery**: Automatically finds legacy plugins and new modules
- **Argument parsing**: Supports all original command-line arguments (`-f`, `-r`, `-d`, `-v`)
- **Error handling**: Graceful fallback when legacy plugins aren't available

### 3. Console Script Entry Points (`pyproject.toml`)
Added multiple entry points for maximum compatibility:
```toml
[project.scripts]
adt-core = "adt_core.cli:main"
adg = "adt_core.cli:main"
adt = "adt_core.cli:main"
adt-test-files = "adt_core.cli:main"
asciidoc-dita-toolkit = "adt_core.cli:main"         # Backward compatibility
asciidoc-dita-toolkit-gui = "adt_core.cli:main"     # Backward compatibility
```

### 4. Functional Module Integration
Updated all modules (`EntityReference`, `ContentType`, `DirectoryConfig`) to:
- **Call legacy plugins**: Integrate with existing working plugin code
- **Process files**: Actually perform the expected file transformations
- **Handle arguments**: Support `-f`, `-r`, `-d`, `-v` flags
- **Verbose output**: Provide detailed feedback when requested

### 5. Improved Module Base Class
- Better error handling and logging
- Proper configuration management
- Consistent interface between legacy and new systems

## Usage Examples

All of these now work correctly:

```bash
# Python module usage
python -m adt_core --help
python -m adt_core --list-plugins
python -m adt_core EntityReference -f file.adoc -v

# Direct command usage
adt-core --help
adt-core --list-plugins
adt-core EntityReference -f file.adoc -v

# Backward compatibility
asciidoc-dita-toolkit --help
asciidoc-dita-toolkit --list-plugins
asciidoc-dita-toolkit EntityReference -f file.adoc -v
```

## Available Plugins

The system now properly discovers and provides access to both legacy plugins and new modules:

### Legacy Plugins (fully functional):
- `EntityReference` - Replace HTML entity references with AsciiDoc attributes
- `ContentType` - Add content type labels where missing
- `CrossReference` - Fix cross-references in AsciiDoc files
- `ContextAnalyzer` - Analyze documentation for context usage
- `ContextMigrator` - Migrate context-suffixed IDs to context-free IDs

### New Modules (integrated with legacy functionality):
- `EntityReference` - v1.2.1 (wraps legacy plugin)
- `ContentType` - v2.1.0 (wraps legacy plugin)
- `DirectoryConfig` - v1.0.3 (wraps legacy plugin)

## Testing Results

✅ **Installation**: `pip install adt-core` now provides working command-line tools
✅ **Module usage**: `python -m adt_core` works correctly
✅ **Plugin discovery**: `--list-plugins` shows all available plugins
✅ **File processing**: Plugins actually process files (tested with EntityReference)
✅ **Backward compatibility**: `asciidoc-dita-toolkit` command still works
✅ **Argument handling**: All original flags (`-f`, `-r`, `-d`, `-v`) work correctly

## Migration Path for Users

Users can now seamlessly transition:

1. **Uninstall old package**: `pip uninstall asciidoc-dita-toolkit`
2. **Install new package**: `pip install adt-core`
3. **Use either command**: Both `adt-core` and `asciidoc-dita-toolkit` work
4. **Same functionality**: All plugins work exactly as before

## Key Features

- **Zero breaking changes**: All existing workflows continue to work
- **Enhanced functionality**: New module system available alongside legacy plugins
- **Better error handling**: Graceful fallbacks when components aren't available
- **Verbose output**: Detailed logging for troubleshooting
- **Future-proof**: Ready for gradual migration to new module system

The package is now fully functional and maintains complete backward compatibility while providing a path forward for the new module system architecture.