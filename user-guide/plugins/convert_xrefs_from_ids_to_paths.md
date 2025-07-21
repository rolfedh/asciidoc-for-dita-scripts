# Convert xrefs from IDs to paths

## Overview

This guide explains how to safely migrate from context-suffixed IDs to path-based cross-references.

The migration system consists of three plugins that work together in a phased approach:

1. **ContextAnalyzer** - Analyzes documentation to understand migration scope
2. **ContextMigrator** - Performs the actual migration with safety checks
3. **CrossReference** - Validates and fixes cross-references

## Quick Start

### Step 1: Analyze Your Documentation

Before making any changes, analyze your documentation to understand the scope:

```bash
# Analyze current directory for context usage
asciidoc-dita-toolkit ContextAnalyzer .

# Analyze specific directory with detailed output
asciidoc-dita-toolkit ContextAnalyzer /path/to/docs --detailed

# Generate JSON report for programmatic use
asciidoc-dita-toolkit ContextAnalyzer . --format json --output analysis.json

# Check only for potential ID collisions
asciidoc-dita-toolkit ContextAnalyzer . --collisions-only
```

### Step 2: Perform Migration

After analyzing, migrate your documentation:

```bash
# Dry run to preview changes
asciidoc-dita-toolkit ContextMigrator . --dry-run

# Perform actual migration with backups
asciidoc-dita-toolkit ContextMigrator . --backup-dir .migration_backup

# Migrate and validate results
asciidoc-dita-toolkit ContextMigrator . --validate
```

### Step 3: Validate Cross-References

After migration, validate your cross-references:

```bash
# Validate xrefs without fixing
asciidoc-dita-toolkit CrossReference . --check-only

# Fix xrefs with migration awareness
asciidoc-dita-toolkit CrossReference . --migration-mode

# Generate detailed validation report
asciidoc-dita-toolkit CrossReference . --validate --detailed
```

## Phase 1: ContextAnalyzer Plugin

The ContextAnalyzer plugin analyzes your AsciiDoc documentation to provide detailed reports on context usage and migration complexity.

### Features

- **Context ID Detection**: Finds all IDs with `_{context}` suffixes
- **Cross-Reference Analysis**: Identifies all xref and link usage
- **Collision Detection**: Predicts potential ID conflicts after migration
- **Risk Assessment**: Categorizes files by migration complexity

### Usage Examples

#### Basic Analysis

```bash
# Analyze current directory
asciidoc-dita-toolkit ContextAnalyzer .
```

**Sample Output:**
```
=== Context Migration Analysis Report ===

Files Scanned: 45
Files with Context IDs: 23
Total IDs with _{context}: 78
Total xrefs found: 156
Total links found: 34

=== Potential ID Collisions ===
Base ID 'installing-edge'
  - installing-edge_ocp4 in modules/installing-edge.adoc:1
  - installing-edge_k8s in modules/installing-edge-k8s.adoc:1
  Suggested: installing-edge-ocp4, installing-edge-k8s

=== Summary ===
- Low Risk: 45 files (simple context removal)
- Medium Risk: 8 files (potential collisions)
- High Risk: 2 files (complex multi-context scenarios)

Recommended approach: Batch migration by risk level
```

#### Detailed Analysis

```bash
# Include detailed per-file information
asciidoc-dita-toolkit ContextAnalyzer . --detailed
```

This adds a section showing exactly which IDs will be changed in each file:

```
=== Files Requiring Migration ===
modules/example.adoc:
  - [id="topic_banana"] → [id="topic"] (line 1)
  - [id="section_banana"] → [id="section"] (line 15)
```

#### Collision-Only Report

```bash
# Focus only on potential conflicts
asciidoc-dita-toolkit ContextAnalyzer . --collisions-only
```

#### JSON Output

```bash
# Generate machine-readable report
asciidoc-dita-toolkit ContextAnalyzer . --format json --output analysis.json
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--detailed` | Include detailed per-file analysis |
| `--collisions-only` | Show only potential ID collision information |
| `--format {text,json}` | Output format (default: text) |
| `--output FILE` | Save report to file instead of console |
| `--verbose` | Enable verbose logging |

## Phase 2: ContextMigrator Plugin

The ContextMigrator plugin performs the actual migration from context-suffixed IDs to context-free IDs with comprehensive safety checks.

### Features

- **Safe Migration**: Atomic file processing with automatic backups
- **Collision Resolution**: Automatic numbering for duplicate IDs
- **Dry-Run Mode**: Preview changes without modifying files
- **Validation**: Post-migration validation of results
- **Rollback Support**: Easy restoration from backups

### Usage Examples

#### Dry Run Migration

Always start with a dry run to preview changes:

```bash
asciidoc-dita-toolkit ContextMigrator . --dry-run
```

**Sample Output:**
```
=== Context Migration Report ===

Total files processed: 23
Successful migrations: 23
Failed migrations: 0
Backup directory: .migration_backups

=== File Migration Details ===
modules/example.adoc: SUCCESS
  ID Changes: 2
    - topic_banana → topic (line 1)
    - section_banana → section (line 15)
  Xref Changes: 1
    - topic_banana[Topic] → topic[Topic] (line 25)
```

#### Production Migration

```bash
# Migrate with custom backup directory
asciidoc-dita-toolkit ContextMigrator . --backup-dir .migration_backup

# Migrate with validation
asciidoc-dita-toolkit ContextMigrator . --validate
```

#### Migration with Collision Resolution

```bash
# Automatically resolve ID collisions
asciidoc-dita-toolkit ContextMigrator . --backup-dir .backups

# Disable collision resolution (not recommended)
asciidoc-dita-toolkit ContextMigrator . --no-collision-resolution
```

#### Specific File Migration

```bash
# Migrate only specific files
asciidoc-dita-toolkit ContextMigrator -f modules/proc_installing.adoc

# Migrate files matching pattern
asciidoc-dita-toolkit ContextMigrator modules/proc_*.adoc
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview changes without modifying files |
| `--no-backup` | Skip creating backups (not recommended) |
| `--backup-dir DIR` | Directory for backup files (default: .migration_backups) |
| `--no-collision-resolution` | Don't resolve ID collisions automatically |
| `--validate` | Validate migration results after completion |
| `--output FILE` | Save migration report to file |
| `--verbose` | Enable verbose logging |

### What Gets Migrated

#### Before Migration
```asciidoc
= Example Document

:context: banana

[id="topic_banana"]
== Topic

See xref:section_banana[Section].

[id="section_banana"]
=== Section

Content here.
```

#### After Migration
```asciidoc
= Example Document

:context: banana

[id="topic"]
== Topic

See xref:section[Section].

[id="section"]
=== Section

Content here.
```

### Collision Resolution

When multiple context-suffixed IDs would become the same after migration, the migrator automatically resolves conflicts:

#### Before Migration
```asciidoc
:context: banana
[id="topic_banana"]
== Topic

:context: apple
[id="topic_apple"]
== Topic
```

#### After Migration
```asciidoc
:context: banana
[id="topic"]
== Topic

:context: apple
[id="topic-1"]
== Topic
```

## Phase 3: CrossReference Plugin

The enhanced CrossReference plugin validates and fixes cross-references with migration awareness and comprehensive reporting.

### Features

- **Cross-Reference Fixing**: Updates xrefs to use proper file paths
- **Migration Awareness**: Prefers context-free IDs during migration
- **Validation Mode**: Check for broken xrefs without fixing
- **Comprehensive Reporting**: Detailed validation and fix reports
- **Multiple Formats**: Text and JSON output formats

### Usage Examples

#### Basic Cross-Reference Fixing

```bash
# Fix xrefs starting from master.adoc
asciidoc-dita-toolkit CrossReference --master-file master.adoc

# Process all master.adoc files recursively
asciidoc-dita-toolkit CrossReference -r
```

#### Validation-Only Mode

```bash
# Only validate without fixing
asciidoc-dita-toolkit CrossReference . --check-only

# Generate validation report
asciidoc-dita-toolkit CrossReference . --validate --report validation.txt
```

#### Migration-Aware Processing

```bash
# Use migration-aware processing
asciidoc-dita-toolkit CrossReference . --migration-mode

# Combine with validation
asciidoc-dita-toolkit CrossReference . --migration-mode --validate --detailed
```

#### Detailed Reporting

```bash
# Generate detailed validation report
asciidoc-dita-toolkit CrossReference . --validate --detailed --report validation.json
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--master-file FILE` | Complete path to your master.adoc file |
| `--check-only` | Only validate xrefs without fixing |
| `--validate` | Generate validation report after processing |
| `--migration-mode` | Use migration-aware processing |
| `--report FILE` | Save validation report to file (.json for JSON) |
| `--detailed` | Include detailed information in reports |
| `--verbose` | Enable verbose logging |

### What Gets Fixed

#### Before Fixing
```asciidoc
= Master Document

[id="master_topic"]
== Master Topic

See xref:included_section[Included Section].

include::included.adoc[]
```

#### After Fixing
```asciidoc
= Master Document

[id="master_topic"]
== Master Topic

See xref:included.adoc#included_section[Included Section].

include::included.adoc[]
```

### Validation Reports

The CrossReference plugin generates comprehensive validation reports:

```
=== Cross-Reference Validation Report ===

Files processed: 25
Total xrefs found: 87
Broken xrefs: 3
Fixed xrefs: 45
Warnings: 2
Validation successful: No

=== Broken Cross-References ===
modules/example.adoc:15
  Xref: xref:missing_section[Missing Section]
  Target ID: missing_section
  Reason: Target ID 'missing_section' not found in documentation
```

## Best Practices

### 1. Always Start with Analysis

Before making any changes, run the ContextAnalyzer to understand the scope:

```bash
asciidoc-dita-toolkit ContextAnalyzer . --detailed --output analysis.txt
```

### 2. Use Dry-Run Mode

Always test your migration with dry-run first:

```bash
asciidoc-dita-toolkit ContextMigrator . --dry-run
```

### 3. Create Backups

Always create backups before migration:

```bash
asciidoc-dita-toolkit ContextMigrator . --backup-dir .migration_backup
```

### 4. Validate After Migration

Always validate your cross-references after migration:

```bash
asciidoc-dita-toolkit CrossReference . --check-only --validate
```

### 5. Process in Batches

For large documentation sets, consider processing in batches:

```bash
# Process high-risk files first
asciidoc-dita-toolkit ContextMigrator modules/proc_*.adoc

# Then process the rest
asciidoc-dita-toolkit ContextMigrator assemblies/
```

## Migration Workflow

Here's a complete migration workflow:

### 1. Pre-Migration Analysis

```bash
# Analyze the documentation
asciidoc-dita-toolkit ContextAnalyzer . --detailed --output analysis.txt

# Review the analysis report
cat analysis.txt
```

### 2. Test Migration

```bash
# Test with dry-run
asciidoc-dita-toolkit ContextMigrator . --dry-run --output test-migration.txt

# Review the test results
cat test-migration.txt
```

### 3. Perform Migration

```bash
# Create backups and migrate
asciidoc-dita-toolkit ContextMigrator . --backup-dir .migration_backup --validate
```

### 4. Validate Results

```bash
# Check for broken xrefs
asciidoc-dita-toolkit CrossReference . --check-only --validate --report validation.txt

# Fix any remaining xref issues
asciidoc-dita-toolkit CrossReference . --migration-mode
```

### 5. Final Validation

```bash
# Final validation check
asciidoc-dita-toolkit CrossReference . --check-only --validate --detailed --report final-validation.json
```

## Troubleshooting

### Common Issues

#### 1. ID Collisions
**Problem**: Multiple IDs become the same after context removal.
**Solution**: The migrator automatically resolves this by adding numeric suffixes.

#### 2. Broken Cross-References
**Problem**: Xrefs point to non-existent IDs.
**Solution**: Use the CrossReference plugin's validation mode to identify and fix.

#### 3. Include File Issues
**Problem**: Include files not being processed.
**Solution**: Ensure include paths are correct and files exist.

### Recovery from Failed Migration

If migration fails or produces unexpected results:

```bash
# Restore from backups
cp -r .migration_backup/* .

# Or restore specific files
cp .migration_backup/modules/example.adoc modules/example.adoc
```

### Getting Help

For additional help:

```bash
# Plugin-specific help
asciidoc-dita-toolkit ContextAnalyzer --help
asciidoc-dita-toolkit ContextMigrator --help
asciidoc-dita-toolkit CrossReference --help

# Verbose output for debugging
asciidoc-dita-toolkit ContextAnalyzer . --verbose
```

## Advanced Usage

### Custom Collision Resolution

You can disable automatic collision resolution if you prefer manual handling:

```bash
asciidoc-dita-toolkit ContextMigrator . --no-collision-resolution
```

### JSON Output for Automation

All plugins support JSON output for integration with other tools:

```bash
asciidoc-dita-toolkit ContextAnalyzer . --format json --output analysis.json
asciidoc-dita-toolkit CrossReference . --validate --report validation.json
```

### Processing Specific File Types

You can target specific files or patterns:

```bash
# Process only procedure files
asciidoc-dita-toolkit ContextMigrator modules/proc_*.adoc

# Process only assemblies
asciidoc-dita-toolkit ContextMigrator assemblies/
```

## Integration with CI/CD

The migration tools can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Validate Cross-References
  run: |
    asciidoc-dita-toolkit CrossReference . --check-only --validate --report validation.json
    if [ $? -ne 0 ]; then
      echo "Cross-reference validation failed"
      exit 1
    fi
```

## Summary

The context migration system provides a safe, comprehensive approach to migrating from context-suffixed IDs to context-free IDs with path-based cross-references. By following the three-phase approach (analyze, migrate, validate), you can ensure a smooth migration with minimal risk of data loss or broken links.

Remember to always:
1. Analyze before migrating
2. Test with dry-run mode
3. Create backups
4. Validate after migration
5. Keep comprehensive reports for audit trails

The system is designed to be safe, reversible, and provide clear visibility into all changes made during the migration process.