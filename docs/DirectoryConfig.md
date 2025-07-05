# Directory Configuration

Directory Configuration enables scoped processing of AsciiDoc files by defining which directories to include or exclude during ADT operations. This feature provides consistent directory filtering across all plugins.

## End User Guide

### Key Concepts

- **Repository Root**: The base directory containing your documentation project
- **Include Directories**: Specific directories to process (empty = process all)
- **Exclude Directories**: Directories to skip during processing
- **Configuration Files**: `.adtconfig.json` stored locally or in home directory
- **Directory Scoping**: Automatic application of filters to all plugin operations

### Configuration File Locations

Configuration files are searched in this order:
1. `./.adtconfig.json` (current directory) - **takes precedence**
2. `~/.adtconfig.json` (home directory) - global default

When both exist, ADT prompts you to choose which configuration to use and shows the last updated timestamp for each.

### Commands

#### Setup Configuration
```bash
# Interactive setup wizard
adt DirectoryConfig

# Enable preview feature first
export ADT_ENABLE_DIRECTORY_CONFIG=true
adt DirectoryConfig
```

#### View Configuration
```bash
adt DirectoryConfig --show
```

### Configuration Schema

```json
{
  "version": "1.0",
  "repoRoot": "/path/to/docs",
  "includeDirs": ["docs/user-guide", "docs/admin-guide"],
  "excludeDirs": ["docs/legacy", "archive"],
  "lastUpdated": "2025-07-04T12:00:00.000000"
}
```

### Examples

#### Example 1: Include Specific Directories
```json
{
  "version": "1.0",
  "repoRoot": "/home/user/docs-project",
  "includeDirs": ["user-guide", "installation"],
  "excludeDirs": [],
  "lastUpdated": "2025-07-04T12:00:00.000000"
}
```

**Result**: Only processes files in `user-guide/` and `installation/` directories.

#### Example 2: Exclude Legacy Content
```json
{
  "version": "1.0", 
  "repoRoot": "/home/user/docs-project",
  "includeDirs": [],
  "excludeDirs": ["legacy", "archive", "drafts"],
  "lastUpdated": "2025-07-04T12:00:00.000000"
}
```

**Result**: Processes all directories except `legacy/`, `archive/`, and `drafts/`.

#### Example 3: No Restrictions
```json
{
  "version": "1.0",
  "repoRoot": "/home/user/docs-project", 
  "includeDirs": [],
  "excludeDirs": [],
  "lastUpdated": "2025-07-04T12:00:00.000000"
}
```

**Result**: Processes all directories (equivalent to no configuration).

### Usage Patterns

#### With Directory Configuration
```bash
# Processes only configured directories
adt ContentType

# Processes a specific directory within the ones allowed by the configuration.
adt ContentType -d ./specific-dir
```

#### Directory Override Behavior

When you specify `-d ./directory` with configuration active:

- **If directory matches includes**: Processes the directory
- **If directory is excluded**: Warns and skips processing  
- **If directory not in includes** (when includes are defined): Warns but still processes

**Example**: Configuration includes `["docs", "guides"]`, excludes `["legacy"]`
```bash
adt ContentType -d ./docs     # ✓ Processes (matches include)
adt ContentType -d ./legacy   # ⚠ Skips (excluded)
adt ContentType -d ./other    # ⚠ Processes with warning (not in includes)
```

#### Without Directory Configuration
```bash
# Traditional behavior - processes current directory
unset ADT_ENABLE_DIRECTORY_CONFIG
adt ContentType

# Traditional behavior - processes specified directory
adt ContentType -d ./docs --recursive
```

### Status Messages

When directory configuration is active:
```
✓ Using directory configuration
✓ Processing 2 directories
✓ Found 15 .adoc files to process
```

When disabled or no configuration found:
```
(no status messages - traditional behavior)
```

### Enabling the Feature

DirectoryConfig is a **preview** feature that must be explicitly enabled:

```bash
export ADT_ENABLE_DIRECTORY_CONFIG=true
```

To disable:
```bash
unset ADT_ENABLE_DIRECTORY_CONFIG
```

---

## Plugin Developer Guide

### Integration Overview

Directory configuration is automatically available to all plugins through the existing `process_adoc_files()` function in `file_utils.py`. No plugin code changes are required.

### Core Functions

#### `load_directory_config()`
```python
from ..file_utils import load_directory_config

config = load_directory_config()
# Returns: dict or None
```

Returns configuration dictionary or `None` if:
- DirectoryConfig plugin is disabled
- No configuration file found
- Configuration file is invalid

#### `is_plugin_enabled(plugin_name)`
```python
from ..file_utils import is_plugin_enabled

if is_plugin_enabled("DirectoryConfig"):
    # Directory configuration is available
```

#### `apply_directory_filters(base_path, config)`
```python
from ..file_utils import apply_directory_filters

# Get directories to process based on configuration
filtered_dirs = apply_directory_filters("/path/to/base", config)
# Returns: List of directory paths to process
```

#### `get_filtered_adoc_files(directory_path, config)`
```python
from ..file_utils import get_filtered_adoc_files

# Get .adoc files with configuration filtering applied
files = get_filtered_adoc_files("/path/to/dir", config)
# Returns: List of .adoc file paths
```

### Behavior Changes

When directory configuration is active, `process_adoc_files()`:
1. Loads configuration automatically
2. Applies directory filtering before file discovery
3. Uses recursive search for configured directories
4. Displays progress messages
5. Warns about missing/excluded directories

When disabled or no configuration:
- Identical to legacy behavior
- No status messages
- Respects `-r/--recursive` flag

### Custom File Discovery

For plugins that need custom file discovery:

```python
from ..file_utils import load_directory_config, apply_directory_filters, get_filtered_adoc_files

def custom_file_processor(directory_path):
    config = load_directory_config()
    
    if config:
        # Use configuration-aware discovery
        filtered_dirs = apply_directory_filters(directory_path, config)
        files = []
        for dir_path in filtered_dirs:
            files.extend(get_filtered_adoc_files(dir_path, config))
        print(f"✓ Using directory configuration")
    else:
        # Fall back to legacy behavior
        files = find_adoc_files(directory_path, recursive=False)
    
    return files
```

### Configuration Structure

Plugins can access configuration data:

```python
config = load_directory_config()
if config:
    repo_root = config['repoRoot']
    include_dirs = config['includeDirs']  # List of relative paths
    exclude_dirs = config['excludeDirs']  # List of relative paths
    last_updated = config['lastUpdated']  # ISO timestamp
```

### Toggle Detection

The DirectoryConfig plugin can be disabled via environment variable:

```python
import os

def is_directory_config_enabled():
    return os.environ.get("ADT_ENABLE_DIRECTORY_CONFIG", "false").lower() == "true"
```

### Compatibility Guidelines

1. **Always check** `load_directory_config()` result before using
2. **Provide fallback** to legacy behavior when `None`
3. **Don't assume** configuration exists
4. **Use existing** `process_adoc_files()` when possible
5. **Test both** enabled and disabled states

### Error Handling

The directory configuration system handles errors gracefully:
- Invalid JSON → warning + `None` return
- Missing directories → warning + continue processing
- Missing configuration → silent fallback to legacy behavior

Plugins should follow the same pattern for consistency.

---

## Testing and Development

### Test Coverage

The DirectoryConfig plugin includes comprehensive unit tests (`tests/test_DirectoryConfig.py`) covering:

- ✅ Configuration file creation, loading, and validation
- ✅ Directory filtering and file discovery
- ✅ Plugin enablement checking via environment variables
- ✅ Error handling for invalid JSON and missing files
- ✅ Integration with the `file_utils.py` configuration system

### Running Tests

```bash
# Run DirectoryConfig tests specifically
python3 -m pytest tests/test_DirectoryConfig.py -v

# Run all tests including DirectoryConfig
python3 -m pytest tests/ -v
```

### Test Fixtures

Test fixtures are located in `tests/fixtures/DirectoryConfig/` and include:
- Sample configuration files
- Test AsciiDoc files with expected outputs
- Various configuration scenarios for validation
