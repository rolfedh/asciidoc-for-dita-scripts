## Title

[Feature] Unify file search behavior across plugins: standardize CLI options and directory handling

## Description

**Status: COMPLETED** ✅

This issue has been addressed as part of the comprehensive refactoring completed in PRs #1-5. Both `EntityReference` and `ContentType` plugins now implement consistent file handling and command-line interface patterns.

### Implemented Solution

- **Consistent CLI Options**: Both plugins now support:
  - `-f FILE` or `--file FILE`: Process a specific file
  - `-r` or `--recursive`: Enable recursive search into subdirectories  
  - `-d DIR` or `--directory DIR`: Specify the root directory for search (default: current directory)

- **Unified Behavior**:
  - By default, plugins process only `.adoc` files in the current directory (non-recursive)
  - Recursive search and custom root directory are supported via CLI options
  - Consistent help messages and documentation across all plugins

- **Shared Implementation**:
  - Common file discovery logic is implemented in `file_utils.py`
  - Both plugins use the same argument parsing patterns
  - Comprehensive test coverage ensures consistent behavior

### Verification

Run the following commands to verify the consistent behavior:

```sh
# Check help for both plugins
asciidoc-dita-toolkit EntityReference --help
asciidoc-dita-toolkit ContentType --help

# Test consistent option support
asciidoc-dita-toolkit EntityReference -r
asciidoc-dita-toolkit ContentType -r
```

### Documentation

All documentation has been updated to reflect the unified CLI interface:

- [README.md](../README.md)
- [docs/asciidoc-dita-toolkit.md](asciidoc-dita-toolkit.md)
- [docs/CONTRIBUTING.md](CONTRIBUTING.md)

**Assignee:** Code with Copilot Agent Mode - COMPLETED
