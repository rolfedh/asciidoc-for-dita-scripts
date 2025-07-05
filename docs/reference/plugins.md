# Plugin Reference

The AsciiDoc DITA Toolkit uses a plugin-based architecture to apply different transformations to your AsciiDoc files. This page provides comprehensive documentation for all available plugins.

## 🔌 Available Plugins

### ContentType
**Purpose**: Adds DITA content type attributes to AsciiDoc files based on content analysis.

**Status**: ✅ Enabled by default

**What it does**: Analyzes your AsciiDoc content and adds appropriate content type metadata for DITA publishing workflows.

**Content type detection**:
- Files with numbered lists (procedures) → `procedure`
- Files with definition lists or reference content → `reference`  
- Assembly files (ending with `_assembly.adoc`) → `assembly`
- Default fallback → `concept`

**Example transformation**:
```asciidoc
// Before
= Installing Docker

Follow these steps to install Docker.

1. Download the installer
2. Run the installation
3. Verify the installation

// After
[cols="1"]
|===

a|*Content Type:* procedure

|===

= Installing Docker

Follow these steps to install Docker.

1. Download the installer
2. Run the installation
3. Verify the installation
```

### EntityReference  
**Purpose**: Converts HTML character entity references to AsciiDoc attribute references.

**Status**: ✅ Enabled by default

**What it does**: Replaces HTML entities that aren't supported in DITA output with proper AsciiDoc attributes.

**Common entities handled**:
- `&hellip;` → `{hellip}` (horizontal ellipsis)
- `&mdash;` → `{mdash}` (em dash)
- `&ndash;` → `{ndash}` (en dash)  
- `&copy;` → `{copy}` (copyright symbol)
- `&reg;` → `{reg}` (registered trademark)
- `&trade;` → `{trade}` (trademark)
- `&amp;` → `{amp}` (ampersand)
- `&lt;` → `{lt}` (less than)
- `&gt;` → `{gt}` (greater than)

**Example transformation**:
```asciidoc
// Before
Use the &amp; symbol to join commands.
The product&trade; is ready&hellip;

// After  
Use the {amp} symbol to join commands.
The product{trade} is ready{hellip}
```

### DirectoryConfig (Optional)
**Purpose**: Provides directory-scoped configuration for processing specific directories.

**Status**: ⚠️ Disabled by default (preview feature)

**What it does**: Allows you to configure which directories to include or exclude during processing, with configuration stored in `.adtconfig.json` files.

**Enable with**:
```bash
export ADT_ENABLE_DIRECTORY_CONFIG=true
```

**Configuration example**:
```json
{
  "version": "1.0",
  "repoRoot": "/home/user/docs-project",
  "includeDirs": ["user-guide", "admin-guide"],
  "excludeDirs": ["legacy", "archive"],
  "lastUpdated": "2025-01-15T12:00:00.000000"
}
```

## 🚀 Using Plugins

### Run All Enabled Plugins
```bash
# Process with all enabled plugins (ContentType + EntityReference)
asciidoc-dita-toolkit docs/
```

### Run Specific Plugins
```bash
# Run only ContentType plugin
asciidoc-dita-toolkit docs/ --plugins ContentType

# Run multiple specific plugins  
asciidoc-dita-toolkit docs/ --plugins ContentType,EntityReference

# Include optional DirectoryConfig plugin
export ADT_ENABLE_DIRECTORY_CONFIG=true
asciidoc-dita-toolkit docs/ --plugins ContentType,EntityReference,DirectoryConfig
```

### List Available Plugins
```bash
# See all available plugins and their status
asciidoc-dita-toolkit --list-plugins
```

## 🔧 Plugin Configuration

### Environment Variables

Some plugins can be configured through environment variables:

```bash
# DirectoryConfig: Non-interactive config selection
export ADT_CONFIG_CHOICE=1

# General: Control logging verbosity  
export ADT_LOG_LEVEL=DEBUG
```

### Plugin-Specific Options

#### ContentType Plugin
- **No configuration required** - works automatically based on content analysis
- Detects content types by analyzing document structure
- Falls back to "concept" type when unclear

#### EntityReference Plugin  
- **No configuration required** - uses built-in entity mapping
- Processes all standard HTML entities supported by AsciiDoc
- Preserves entities that are already in AsciiDoc format

#### DirectoryConfig Plugin
- **Requires setup** - run `asciidoc-dita-toolkit docs/ --plugins DirectoryConfig` to configure
- Configuration stored in `.adtconfig.json` files
- Supports both local (per-project) and global (home directory) configs

## 📊 Plugin Behavior

### Processing Order
1. **DirectoryConfig** (if enabled) - Determines which files to process
2. **ContentType** - Analyzes and adds content type metadata
3. **EntityReference** - Converts HTML entities to AsciiDoc attributes

### File Safety
- All plugins work **non-destructively** when possible
- Use `--dry-run` to preview all changes before applying
- Original file formatting is preserved where possible
- Backup your files before running (recommended)

### Error Handling
- Plugins skip files they cannot process safely
- Error messages indicate which files had issues
- Processing continues for other files even if some fail
- Use `--verbose` for detailed error information

## 🧪 Testing Plugins

### Dry Run Mode
```bash
# Preview what all plugins would do
asciidoc-dita-toolkit docs/ --dry-run

# Preview specific plugin changes
asciidoc-dita-toolkit docs/ --plugins ContentType --dry-run
```

### Verbose Output
```bash
# See detailed plugin processing information
asciidoc-dita-toolkit docs/ --verbose

# Combine with dry run for maximum detail
asciidoc-dita-toolkit docs/ --dry-run --verbose
```

## 🔍 Plugin Development

Interested in developing your own plugins? See the [Plugin Development Guide](../development/plugin-development.md) for:

- Plugin architecture overview
- Development patterns and best practices  
- Testing strategies and fixtures
- Integration with the toolkit infrastructure

## 🐛 Troubleshooting

### Common Issues

**Plugin not found**:
```bash
# Check available plugins
asciidoc-dita-toolkit --list-plugins

# Verify plugin name spelling
asciidoc-dita-toolkit docs/ --plugins ContentType  # Correct
asciidoc-dita-toolkit docs/ --plugins contenttype  # Wrong
```

**DirectoryConfig plugin not working**:
```bash
# Enable the preview feature first
export ADT_ENABLE_DIRECTORY_CONFIG=true
asciidoc-dita-toolkit docs/ --plugins DirectoryConfig
```

**Unexpected results**:
```bash
# Use dry run to understand what would change
asciidoc-dita-toolkit docs/ --dry-run --verbose

# Test on a single file first
asciidoc-dita-toolkit single-file.adoc --dry-run
```

For more troubleshooting help, see the [Troubleshooting Guide](../user-guides/troubleshooting.md).

## 📚 Related Documentation

- [Getting Started](../user-guides/getting-started.md) - Basic usage examples
- [CLI Reference](../user-guides/cli-reference.md) - Complete command options
- [Plugin Development](../development/plugin-development.md) - Creating custom plugins
- [Architecture](architecture.md) - Technical overview of the toolkit
