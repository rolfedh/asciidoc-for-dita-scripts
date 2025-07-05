# Configuration Reference

Configuration options and environment variables for the AsciiDoc DITA Toolkit.

## 🌍 Environment Variables

### `ADT_CONFIG_CHOICE`
**Purpose**: Non-interactive configuration selection for DirectoryConfig plugin.

**Values**: Integer (1, 2, 3, etc.)

**Usage**:
```bash
# Automatically select first configuration option
export ADT_CONFIG_CHOICE=1
asciidoc-dita-toolkit docs/

# Use in CI/CD for automated processing
export ADT_CONFIG_CHOICE=1
```

**Default**: Interactive prompt when multiple configurations exist

### `ADT_LOG_LEVEL`
**Purpose**: Control logging verbosity for detailed debugging.

**Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`

**Usage**:
```bash
# Enable debug logging
export ADT_LOG_LEVEL=DEBUG
asciidoc-dita-toolkit docs/ --verbose

# Show only warnings and errors
export ADT_LOG_LEVEL=WARNING
asciidoc-dita-toolkit docs/
```

**Default**: `INFO`

### `ADT_ENABLE_DIRECTORY_CONFIG`
**Purpose**: Enable the DirectoryConfig plugin (preview feature).

**Values**: `true`, `false`

**Usage**:
```bash
# Enable DirectoryConfig plugin
export ADT_ENABLE_DIRECTORY_CONFIG=true
asciidoc-dita-toolkit docs/ --plugins DirectoryConfig

# Disable (default behavior)
unset ADT_ENABLE_DIRECTORY_CONFIG
```

**Default**: `false` (disabled)

## 📁 Configuration Files

### DirectoryConfig (`.adtconfig.json`)

The DirectoryConfig plugin uses JSON configuration files to specify which directories to process.

#### File Locations
Configuration files are searched in this order:
1. `./.adtconfig.json` (current directory) - **takes precedence**
2. `~/.adtconfig.json` (home directory) - global default

#### Schema
```json
{
  "version": "1.0",
  "repoRoot": "/absolute/path/to/repository",
  "includeDirs": ["relative/path1", "relative/path2"],
  "excludeDirs": ["relative/path3", "relative/path4"],
  "lastUpdated": "2025-01-15T12:00:00.000000"
}
```

#### Properties

**`version`** (string, required)
- Configuration format version
- Current version: `"1.0"`

**`repoRoot`** (string, required)
- Absolute path to repository root
- Used as base for relative directory paths

**`includeDirs`** (array of strings, optional)
- Relative paths to directories to include
- Empty array means "include all directories"
- Paths are relative to `repoRoot`

**`excludeDirs`** (array of strings, optional)
- Relative paths to directories to exclude
- Empty array means "exclude nothing"
- Excludes take precedence over includes

**`lastUpdated`** (string, required)
- ISO 8601 timestamp of last configuration update
- Used to show which configuration is newer when choosing

#### Examples

**Include specific directories only**:
```json
{
  "version": "1.0",
  "repoRoot": "/home/user/docs-project",
  "includeDirs": ["user-guide", "admin-guide", "api-reference"],
  "excludeDirs": [],
  "lastUpdated": "2025-01-15T10:30:00.000000"
}
```

**Exclude legacy content**:
```json
{
  "version": "1.0",
  "repoRoot": "/home/user/docs-project",
  "includeDirs": [],
  "excludeDirs": ["legacy", "archive", "drafts", "old-versions"],
  "lastUpdated": "2025-01-15T14:45:00.000000"
}
```

**Process everything (no restrictions)**:
```json
{
  "version": "1.0",
  "repoRoot": "/home/user/docs-project",
  "includeDirs": [],
  "excludeDirs": [],
  "lastUpdated": "2025-01-15T16:20:00.000000"
}
```

#### Creating Configuration Files

**Interactive setup**:
```bash
# Enable DirectoryConfig and run setup wizard
export ADT_ENABLE_DIRECTORY_CONFIG=true
asciidoc-dita-toolkit docs/ --plugins DirectoryConfig
```

**Manual creation**:
```bash
# Create local configuration
cat > .adtconfig.json << EOF
{
  "version": "1.0",
  "repoRoot": "$(pwd)",
  "includeDirs": ["docs", "guides"],
  "excludeDirs": ["legacy"],
  "lastUpdated": "$(date -Iseconds)"
}
EOF

# Create global configuration
cat > ~/.adtconfig.json << EOF
{
  "version": "1.0",
  "repoRoot": "/home/$(whoami)/default-docs",
  "includeDirs": [],
  "excludeDirs": ["archive", "temp"],
  "lastUpdated": "$(date -Iseconds)"
}
EOF
```

#### Validation

The toolkit validates configuration files automatically:

- **JSON syntax**: Must be valid JSON
- **Required fields**: `version`, `repoRoot`, `lastUpdated`
- **Directory paths**: Must be relative paths (no leading `/`)
- **Repository root**: Must be an absolute path
- **Timestamp format**: Must be valid ISO 8601

**Common validation errors**:
```bash
# Invalid JSON syntax
Error: Configuration file contains invalid JSON

# Missing required fields
Error: Configuration missing required field 'version'

# Absolute path in directories
Error: Directory paths must be relative, found '/absolute/path'

# Invalid timestamp
Error: Invalid timestamp format in 'lastUpdated'
```

## ⚙️ Command-Line Options

### Global Options

**`--dry-run`**
- Preview changes without modifying files
- Works with all plugins
- Shows what would be changed

**`--verbose`**
- Enable detailed output
- Shows processing steps and debug information
- Useful for troubleshooting

**`--plugins`**
- Specify which plugins to run
- Comma-separated list
- Example: `--plugins ContentType,EntityReference`

**`--version`**
- Display toolkit version
- Exits after showing version

**`--help`**
- Show command help
- Lists all available options

**`--list-plugins`**
- Show available plugins and their status
- Indicates which plugins are enabled/disabled

### Plugin-Specific Options

Currently, the toolkit uses a simple plugin architecture where plugins are enabled/disabled rather than configured through command-line options. Plugin behavior is controlled through:

1. **Environment variables** (see above)
2. **Configuration files** (for DirectoryConfig)
3. **Built-in logic** (for ContentType and EntityReference)

## 🔧 Configuration Hierarchy

Configuration is applied in this order (later settings override earlier ones):

1. **Built-in defaults**
2. **Global configuration** (`~/.adtconfig.json`)
3. **Local configuration** (`./.adtconfig.json`)
4. **Environment variables**
5. **Command-line options**

## 💡 Configuration Tips

### Development Workflow
```bash
# Set up development environment
export ADT_LOG_LEVEL=DEBUG
export ADT_ENABLE_DIRECTORY_CONFIG=true

# Test with local configuration
asciidoc-dita-toolkit docs/ --dry-run --verbose
```

### Production/CI Workflow
```bash
# Non-interactive, minimal logging
export ADT_CONFIG_CHOICE=1
export ADT_LOG_LEVEL=WARNING

# Process with specific plugins only
asciidoc-dita-toolkit docs/ --plugins ContentType,EntityReference
```

### Team Collaboration
```bash
# Create shared configuration
cat > .adtconfig.json << EOF
{
  "version": "1.0",
  "repoRoot": "$(pwd)",
  "includeDirs": ["docs", "guides", "tutorials"],
  "excludeDirs": ["legacy", "archive"],
  "lastUpdated": "$(date -Iseconds)"
}
EOF

# Commit to version control
git add .adtconfig.json
git commit -m "Add AsciiDoc DITA Toolkit configuration"
```

## 🚀 Related Documentation

- [CLI Reference](../user-guides/cli-reference.md) - Complete command options
- [Plugin Reference](plugins.md) - Plugin-specific configuration
- [Getting Started](../user-guides/getting-started.md) - Basic usage examples
- [Troubleshooting](../user-guides/troubleshooting.md) - Configuration issues
