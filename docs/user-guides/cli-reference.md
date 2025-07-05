# CLI Reference

Complete command-line reference for the AsciiDoc DITA Toolkit.

## 📖 Basic Syntax

```bash
asciidoc-dita-toolkit [paths...] [options]
```

## 📂 Arguments

### `paths`
One or more paths to AsciiDoc files or directories to process.

```bash
# Single file
asciidoc-dita-toolkit my-doc.adoc

# Single directory
asciidoc-dita-toolkit docs/

# Multiple paths
asciidoc-dita-toolkit docs/ examples/ tutorials/

# Current directory
asciidoc-dita-toolkit .
```

## 🔧 Options

### `--plugins`
Specify which plugins to run (comma-separated).

```bash
# Run specific plugins
asciidoc-dita-toolkit docs/ --plugins ContentType,EntityReference

# Run single plugin
asciidoc-dita-toolkit docs/ --plugins ContentType
```

**Available plugins:**
- `ContentType` - Adds DITA content type attributes
- `EntityReference` - Converts HTML entities to AsciiDoc attributes  
- `DirectoryConfig` - Manages directory-specific configurations (optional)

### `--dry-run`
Show what changes would be made without actually modifying files.

```bash
# Preview changes
asciidoc-dita-toolkit docs/ --dry-run

# Preview with specific plugins
asciidoc-dita-toolkit docs/ --plugins ContentType --dry-run
```

### `--verbose`
Enable verbose output for detailed processing information.

```bash
# Detailed output
asciidoc-dita-toolkit docs/ --verbose

# Combine with other options
asciidoc-dita-toolkit docs/ --dry-run --verbose
```

### `--version`
Display the toolkit version.

```bash
asciidoc-dita-toolkit --version
```

### `--help`
Show help information and exit.

```bash
asciidoc-dita-toolkit --help
```

### `--list-plugins`
List all available plugins and their descriptions.

```bash
asciidoc-dita-toolkit --list-plugins
```

## 🌍 Environment Variables

### `ADT_CONFIG_CHOICE`
Non-interactive configuration selection for DirectoryConfig plugin.

```bash
# Use first configuration option automatically
export ADT_CONFIG_CHOICE=1
asciidoc-dita-toolkit docs/
```

### `ADT_LOG_LEVEL`
Control logging verbosity.

```bash
# Enable debug logging
export ADT_LOG_LEVEL=DEBUG
asciidoc-dita-toolkit docs/ --verbose

# Available levels: DEBUG, INFO, WARNING, ERROR
export ADT_LOG_LEVEL=WARNING
```

## 📋 Common Command Patterns

### Quick Processing
```bash
# Process current directory with all plugins
asciidoc-dita-toolkit .

# Process specific directory
asciidoc-dita-toolkit docs/
```

### Safe Testing
```bash
# Always test first
asciidoc-dita-toolkit docs/ --dry-run

# Test with verbose output
asciidoc-dita-toolkit docs/ --dry-run --verbose
```

### Selective Processing
```bash
# Only add content types
asciidoc-dita-toolkit docs/ --plugins ContentType

# Only convert entities
asciidoc-dita-toolkit docs/ --plugins EntityReference
```

### Batch Processing
```bash
# Process multiple directories
asciidoc-dita-toolkit docs/ examples/ tutorials/

# Process with environment variable
ADT_CONFIG_CHOICE=1 asciidoc-dita-toolkit docs/
```

## 🐳 Container Usage

When using containers, mount your workspace and use the same commands:

```bash
# Basic usage
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest docs/

# With options
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest docs/ --dry-run --verbose

# With environment variables
docker run --rm -v $(pwd):/workspace -e ADT_CONFIG_CHOICE=1 rolfedh/asciidoc-dita-toolkit-prod:latest docs/
```

See [Container Usage Guide](containers.md) for more details.

## 🔍 Output Understanding

### Success Output
```
Found 15 .adoc files in docs/
Processing with plugins: ContentType, EntityReference
✓ docs/installation.adoc - Added content type, converted 3 entities
✓ docs/getting-started.adoc - Added content type
✓ docs/cli-reference.adoc - No changes needed
Processed 15 files successfully.
```

### Dry Run Output
```
[DRY RUN] Found 15 .adoc files in docs/
[DRY RUN] Would process with plugins: ContentType, EntityReference
[DRY RUN] docs/installation.adoc - Would add content type, convert 3 entities
[DRY RUN] docs/getting-started.adoc - Would add content type
[DRY RUN] docs/cli-reference.adoc - No changes needed
[DRY RUN] Would process 15 files.
```

### Error Output
```
Found 15 .adoc files in docs/
Processing with plugins: ContentType, EntityReference
✓ docs/installation.adoc - Added content type
✗ docs/broken.adoc - Error: Invalid content structure on line 10
✗ docs/malformed.adoc - Error: Cannot parse file
Processed 13 files successfully, 2 files had errors.
```

## ⚠️ Return Codes

- `0` - Success, all files processed without errors
- `1` - Some files had errors or warnings
- `2` - Command-line argument errors
- `3` - No files found to process

## 🔗 Exit Codes in Scripts

```bash
#!/bin/bash
asciidoc-dita-toolkit docs/ --dry-run
if [ $? -eq 0 ]; then
    echo "All files look good, applying changes..."
    asciidoc-dita-toolkit docs/
else
    echo "Issues found, please review before applying changes"
    exit 1
fi
```

## 📝 Examples

### Complete Workflow
```bash
# 1. Test what changes would be made
asciidoc-dita-toolkit docs/ --dry-run --verbose

# 2. Apply changes if everything looks good
asciidoc-dita-toolkit docs/

# 3. Process additional directories
asciidoc-dita-toolkit examples/ tutorials/
```

### CI/CD Integration
```bash
# Non-interactive processing for automation
export ADT_CONFIG_CHOICE=1
export ADT_LOG_LEVEL=WARNING

# Process and fail if errors
asciidoc-dita-toolkit docs/ || exit 1
```

### Plugin-Specific Processing
```bash
# Step 1: Add content types
asciidoc-dita-toolkit docs/ --plugins ContentType

# Step 2: Convert entities
asciidoc-dita-toolkit docs/ --plugins EntityReference

# Step 3: Apply directory configs (if needed)
asciidoc-dita-toolkit docs/ --plugins DirectoryConfig
```

## 🚀 Related Documentation

- [Getting Started Guide](getting-started.md) - Learn the basics
- [Container Usage](containers.md) - Using with Docker
- [Plugin Reference](../reference/plugins.md) - Detailed plugin documentation
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
