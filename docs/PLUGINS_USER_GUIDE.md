# AsciiDoc DITA Toolkit Plugin User Guide

## Overview

This guide explains how to use the AsciiDoc DITA Toolkit's plugins to process and validate AsciiDoc documentation for DITA-based publishing workflows.

## Available Plugins

### Core Plugins

1. **ContentType** - Add/update content type attributes
2. **ContextAnalyzer** - Analyze context IDs and references
3. **ContextMigrator** - Migrate context-dependent IDs
4. **CrossReference** - Validate and fix cross-references
5. **DirectoryConfig** - Manage directory-specific configurations
6. **EntityReference** - Convert HTML entities to AsciiDoc
7. **ExampleBlock** - Detect and process example blocks

## Quick Start

### Basic Usage Pattern

All plugins follow a consistent command-line interface:

```bash
# Basic usage
adt <PluginName> [options]

# Process current directory recursively
adt <PluginName> -r

# Process specific file
adt <PluginName> -f filename.adoc

# Process specific directory
adt <PluginName> -d /path/to/docs

# Get plugin-specific help
adt <PluginName> -h
```

### Common Options

| Option | Description |
|--------|-------------|
| `-r, --recursive` | Process all .adoc files recursively |
| `-f, --file FILE` | Process a specific file |
| `-d, --directory DIR` | Specify root directory (default: current) |
| `-v, --verbose` | Enable verbose output |
| `-h, --help` | Show plugin-specific help |

## Plugin Details

### ContentType Plugin

Adds or updates content type attributes in AsciiDoc files.

#### Usage Examples

```bash
# Add content type attributes to all files
adt ContentType -r

# Process specific file
adt ContentType -f modules/proc_example.adoc

# Process with verbose output
adt ContentType -r -v
```

#### What it does

- Analyzes AsciiDoc files to determine content type (procedure, concept, reference, etc.)
- Adds appropriate content type attributes
- Updates existing content type attributes if incorrect

### EntityReference Plugin

Converts HTML entities to AsciiDoc equivalents.

#### Usage Examples

```bash
# Convert HTML entities in all files
adt EntityReference -r

# Convert entities in specific directory
adt EntityReference -d modules/

# Dry run to preview changes
adt EntityReference -r --dry-run
```

#### Common Conversions

| HTML Entity | AsciiDoc Equivalent |
|-------------|-------------------|
| `&amp;` | `&` |
| `&lt;` | `<` |
| `&gt;` | `>` |
| `&nbsp;` | `{nbsp}` |
| `&copy;` | `{copy}` |

### CrossReference Plugin

Validates and fixes cross-references between AsciiDoc files.

#### Usage Examples

```bash
# Fix cross-references from master file
adt CrossReference --master-file master.adoc

# Process all master files recursively
adt CrossReference -r

# Validation only (no fixes)
adt CrossReference . --check-only

# Generate detailed report
adt CrossReference -r --validate --detailed
```

#### Features

- Identifies broken cross-references
- Fixes xref paths to use proper file references
- Validates include file paths
- Generates comprehensive reports

### DirectoryConfig Plugin

Manages directory-specific plugin configurations.

#### Usage Examples

```bash
# Initialize directory configuration
adt DirectoryConfig --init

# Validate current configuration
adt DirectoryConfig --validate

# Apply configuration to directory
adt DirectoryConfig -d modules/
```

#### Configuration File

Creates `.adt-config.json` files to specify directory-specific settings:

```json
{
  "plugins": {
    "ContentType": {
      "enabled": true,
      "auto_detect": true
    },
    "EntityReference": {
      "enabled": true,
      "preserve_nbsp": false
    }
  }
}
```

### ExampleBlock Plugin

Detects and processes example blocks in documentation.

#### Usage Examples

```bash
# Process example blocks
adt ExampleBlock -r

# Validate example block formatting
adt ExampleBlock -d examples/ --validate
```

## Context Migration Plugins

For migrating from context-suffixed IDs to context-free IDs:

### ContextAnalyzer Plugin

Analyzes documentation for context usage and migration complexity.

#### Usage Examples

```bash
# Analyze current directory
adt ContextAnalyzer .

# Detailed analysis with per-file information
adt ContextAnalyzer . --detailed

# Generate JSON report
adt ContextAnalyzer . --format json --output analysis.json

# Check only for ID collisions
adt ContextAnalyzer . --collisions-only
```

#### Sample Output

```
=== Context Migration Analysis Report ===

Files Scanned: 45
Files with Context IDs: 23
Total IDs with _{context}: 78
Total xrefs found: 156

=== Potential ID Collisions ===
Base ID 'installing-edge'
  - installing-edge_ocp4 in modules/installing-edge.adoc:1
  - installing-edge_k8s in modules/installing-edge-k8s.adoc:1

=== Summary ===
- Low Risk: 45 files (simple context removal)
- Medium Risk: 8 files (potential collisions)
- High Risk: 2 files (complex scenarios)
```

### ContextMigrator Plugin

Performs the actual migration with safety checks.

#### Usage Examples

```bash
# Dry run to preview changes
adt ContextMigrator . --dry-run

# Perform migration with backups
adt ContextMigrator . --backup-dir .migration_backup

# Migrate and validate results
adt ContextMigrator . --validate
```

#### Features

- Atomic file processing with automatic backups
- Collision resolution with automatic numbering
- Post-migration validation
- Rollback support from backups

## Best Practices

### 1. Always Start with Analysis

Before making changes, understand what will be affected:

```bash
# Analyze before processing
adt ContextAnalyzer . --detailed
```

### 2. Use Dry-Run Mode

Test changes before applying them:

```bash
# Preview changes without modifying files
adt EntityReference -r --dry-run
adt ContextMigrator . --dry-run
```

### 3. Process Incrementally

For large documentation sets, process in batches:

```bash
# Process specific file types first
adt ContentType modules/proc_*.adoc

# Then process remaining files
adt ContentType assemblies/
```

### 4. Create Backups

Always backup important files before major changes:

```bash
# Create backup directory
mkdir .backups
cp -r modules/ .backups/

# Use plugins with backup options
adt ContextMigrator . --backup-dir .migration_backup
```

### 5. Validate After Processing

Always validate results after processing:

```bash
# Validate cross-references
adt CrossReference . --check-only --validate

# Generate validation report
adt CrossReference . --validate --report validation.txt
```

## Workflow Examples

### Basic Content Validation Workflow

```bash
# 1. Add content type attributes
adt ContentType -r

# 2. Fix HTML entities
adt EntityReference -r

# 3. Validate cross-references
adt CrossReference -r --check-only

# 4. Generate report
adt CrossReference -r --validate --report validation.txt
```

### Context Migration Workflow

```bash
# 1. Analyze documentation
adt ContextAnalyzer . --detailed --output analysis.txt

# 2. Test migration
adt ContextMigrator . --dry-run

# 3. Perform migration
adt ContextMigrator . --backup-dir .migration_backup --validate

# 4. Fix cross-references
adt CrossReference . --migration-mode

# 5. Final validation
adt CrossReference . --check-only --validate --detailed
```

### Directory-Specific Processing

```bash
# 1. Set up directory configuration
adt DirectoryConfig modules/ --init

# 2. Process according to configuration
adt ContentType modules/
adt EntityReference modules/

# 3. Validate configuration compliance
adt DirectoryConfig modules/ --validate
```

## Troubleshooting

### Common Issues

#### Plugin Not Found
```
Error: Plugin 'PluginName' not found
```
**Solution**: Check plugin name spelling and use `adt --list-plugins` to see available plugins.

#### Permission Errors
```
Error: Permission denied writing to file
```
**Solution**: Check file permissions or run with appropriate privileges.

#### Backup Directory Conflicts
```
Error: Backup directory already exists
```
**Solution**: Use a different backup directory name or remove existing backup.

### Getting Help

#### Plugin-Specific Help
```bash
# Get help for specific plugin
adt ContentType --help
adt CrossReference --help
```

#### List Available Plugins
```bash
# See all available plugins
adt --list-plugins
```

#### Verbose Output for Debugging
```bash
# Enable verbose logging
adt ContentType -r --verbose
```

## Integration with Build Systems

### Makefile Integration

```makefile
.PHONY: validate-docs
validate-docs:
	adt ContentType -r
	adt EntityReference -r
	adt CrossReference -r --check-only

.PHONY: fix-docs
fix-docs:
	adt ContentType -r
	adt EntityReference -r
	adt CrossReference -r
```

### GitHub Actions Integration

```yaml
name: Validate Documentation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Install ADT
      run: pip install asciidoc-dita-toolkit

    - name: Validate Content Types
      run: adt ContentType -r

    - name: Fix Entity References
      run: adt EntityReference -r

    - name: Validate Cross References
      run: adt CrossReference -r --check-only --validate
```

## Advanced Usage

### Custom Plugin Configuration

Create `.adt-config.json` for project-specific settings:

```json
{
  "global": {
    "verbose": true,
    "backup_enabled": true
  },
  "plugins": {
    "ContentType": {
      "auto_detect": true,
      "default_type": "concept"
    },
    "EntityReference": {
      "preserve_nbsp": false,
      "convert_quotes": true
    },
    "CrossReference": {
      "validate_includes": true,
      "fix_case_sensitivity": true
    }
  }
}
```

### Scripting with JSON Output

Many plugins support JSON output for scripting:

```bash
# Generate JSON report
adt ContextAnalyzer . --format json --output analysis.json

# Process with script
python process_analysis.py analysis.json
```

### Batch Processing Scripts

```bash
#!/bin/bash
# batch_process.sh

DIRS=("modules" "assemblies" "images")

for dir in "${DIRS[@]}"; do
    echo "Processing $dir..."
    adt ContentType -d "$dir"
    adt EntityReference -d "$dir"
    adt CrossReference -d "$dir" --check-only
done
```

## Summary

The AsciiDoc DITA Toolkit provides a comprehensive set of plugins for processing and validating AsciiDoc documentation. By following the patterns and best practices outlined in this guide, you can:

- Maintain consistent content types across your documentation
- Convert legacy HTML entities to proper AsciiDoc
- Validate and fix cross-references between files
- Safely migrate from context-dependent to context-free IDs
- Integrate validation into your build and CI/CD processes

Remember to always:
1. Analyze before making changes
2. Use dry-run mode for testing
3. Create backups before major changes
4. Validate results after processing
5. Use verbose output for troubleshooting

For more detailed information about specific plugins, use the `--help` option with each plugin or refer to the individual plugin documentation.
