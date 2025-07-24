# ArchiveUnusedFiles Plugin

The ArchiveUnusedFiles plugin scans for AsciiDoc files that are not referenced by any other AsciiDoc file in the project and optionally archives them.

## Features

- **Smart Detection**: Analyzes `include::` directives to identify unused files
- **Configurable Scanning**: Specify which directories to scan for AsciiDoc files
- **Flexible Exclusions**: Exclude specific directories, files, or use exclusion lists
- **Manifest Generation**: Creates timestamped manifests of unused files
- **Optional Archiving**: Move unused files to ZIP archives and delete originals
- **ADT Integration**: Full integration with the AsciiDoc DITA Toolkit ecosystem

## Usage

### Command Line Interface

The plugin can be used through the ADT CLI:

```bash
# List unused files (dry run)
adt ArchiveUnusedFiles -r

# Use the standalone module with full options
python3 modules/archive_unused_files.py --help
```

### Standalone Module

For full functionality, use the standalone module:

```bash
# Find unused files (dry run)
python3 modules/archive_unused_files.py

# Archive unused files
python3 modules/archive_unused_files.py --archive

# Exclude specific directories
python3 modules/archive_unused_files.py --exclude-dir ./modules/legacy --exclude-dir ./modules/archive

# Use custom scan directories
python3 modules/archive_unused_files.py --scan-dirs ./docs ./content --archive

# Use exclusion list file
python3 modules/archive_unused_files.py --exclude-list exclusions.txt --archive
```

## Configuration Options

### Command Line Arguments

- `--archive`: Move unused files to a dated ZIP archive and delete originals
- `--scan-dirs`: Directories to scan for AsciiDoc files (default: `./modules`, `./modules/rn`, `./assemblies`)
- `--archive-dir`: Directory to store archives and manifests (default: `./archive`)
- `--exclude-dir`: Directory to exclude from scanning (can be used multiple times)
- `--exclude-file`: Specific file to exclude (can be used multiple times)
- `--exclude-list`: Path to file containing directories/files to exclude, one per line
- `--verbose`: Enable detailed output

### ADT Module Configuration

When used as an ADT module, the plugin can be configured in `.adt-modules.json`:

```json
{
  "name": "ArchiveUnusedFiles",
  "required": false,
  "version": ">=1.0.0",
  "dependencies": [],
  "init_order": 5,
  "config": {
    "scan_dirs": ["./modules", "./modules/rn", "./assemblies"],
    "archive_dir": "./archive",
    "archive": false
  }
}
```

## Exclusion List Format

The exclusion list file should contain one path per line:

```
./modules/legacy
./modules/archive/obsolete.adoc
# This is a comment
./temp
./work-in-progress
```

- Lines starting with `#` are treated as comments
- Empty lines are ignored
- Directory paths exclude entire directories
- File paths exclude specific files

## Output

### Manifest Files

The plugin creates timestamped manifest files in the archive directory:

```
archive/
├── unused-files-2025-07-23_100022.txt
└── unused-files-2025-07-23_101534.txt
```

Each manifest contains the full paths of unused files, one per line.

### Archive Files (Optional)

When using the `--archive` option, the plugin creates ZIP archives:

```
archive/
├── unused-files-2025-07-23_100022.txt
├── unused-files-2025-07-23_100022.zip
└── manifest-and-archive-created.log
```

The ZIP archive contains all unused files with their relative paths preserved.

## How It Works

1. **File Collection**: Scans specified directories for `.adoc` files
2. **Reference Analysis**: Parses all AsciiDoc files to find `include::` directives
3. **Unused Detection**: Identifies files not referenced by any `include::` statement
4. **Exclusion Processing**: Removes excluded files and directories from results
5. **Output Generation**: Creates manifest and optionally archives files

## Integration with ADT

The ArchiveUnusedFiles plugin integrates seamlessly with the ADT ecosystem:

- **Module System**: Implements the ADTModule interface for orchestrated execution
- **Configuration Management**: Supports ADT configuration files and contexts
- **CLI Integration**: Available through the standard `adt` command
- **Testing Framework**: Includes comprehensive test coverage

## Testing

Run the plugin tests:

```bash
python3 -m pytest tests/test_archive_unused_files.py -v
```

## Examples

### Basic Usage

```bash
# Find unused files in default directories
python3 modules/archive_unused_files.py

# Output:
# modules/unused_module.adoc
# modules/obsolete_content.adoc
#
# Results:
#   Unused files found: 2
#   Manifest created: ./archive/unused-files-2025-07-23_100022.txt
#   Run with --archive to move files to archive
```

### Archive Unused Files

```bash
python3 modules/archive_unused_files.py --archive

# Output:
# modules/unused_module.adoc
# modules/obsolete_content.adoc
# INFO: Archiving: modules/unused_module.adoc -> ./archive/unused-files-2025-07-23_100022.zip
# INFO: Archiving: modules/obsolete_content.adoc -> ./archive/unused-files-2025-07-23_100022.zip
#
# Results:
#   Unused files found: 2
#   Manifest created: ./archive/unused-files-2025-07-23_100022.txt
#   Archive created: ./archive/unused-files-2025-07-23_100022.zip
#   Files archived and deleted: 2
```

### Custom Configuration

```bash
python3 modules/archive_unused_files.py \
  --scan-dirs ./documentation ./content \
  --exclude-dir ./documentation/legacy \
  --exclude-file ./content/template.adoc \
  --archive-dir ./backups \
  --verbose
```

## Error Handling

The plugin handles various error conditions gracefully:

- **Missing directories**: Warns about non-existent scan directories
- **Permission errors**: Reports files that cannot be read
- **Invalid exclusion lists**: Continues processing with warnings
- **Archive failures**: Reports specific archiving errors

## Best Practices

1. **Test First**: Always run without `--archive` to review unused files
2. **Use Exclusions**: Exclude template files, work-in-progress content, and legacy directories
3. **Regular Cleanup**: Schedule periodic runs to maintain a clean repository
4. **Backup Important**: Review archives before permanent deletion
5. **Version Control**: Commit exclusion lists to share team preferences

## Troubleshooting

### Common Issues

**No unused files found when they should exist:**
- Check that scan directories contain AsciiDoc files
- Verify include paths use correct syntax: `include::filename.adoc[]`
- Ensure files use `.adoc` extension

**Files incorrectly marked as unused:**
- Add false positives to exclusion list
- Check for non-standard include patterns
- Verify file references in comments or code blocks

**Permission denied errors:**
- Ensure read permissions on all scan directories
- Check write permissions for archive directory
- Run with `--verbose` for detailed error information

---

For more information, see the main [AsciiDoc DITA Toolkit documentation](../README.md).
