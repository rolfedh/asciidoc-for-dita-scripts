# CLI Simplification Design Document

This document outlines improvements to make the AsciiDoc DITA Toolkit CLI more user-friendly and intuitive. Items marked with ✅ are implemented, items marked with an asterisk (*) require new core functionality to be developed.

## Command Structure Simplification

### 1. **Default Actions** *
Make the most common operations work without flags:
```bash
adt EntityReference file.adoc    # auto-detect it's a file
adt ContentType docs/            # auto-detect it's a directory
```

**Implementation Notes:**
- Requires modifying argument parsing to detect file vs directory automatically
- Need to update plugin interface to handle implicit target detection

### 2. **Smart Plugin Selection** *
Auto-run appropriate plugins based on file content:
```bash
adt --auto file.adoc            # analyzes file and runs relevant plugins
adt --fix-all docs/             # runs all applicable plugins
```

**Implementation Notes:**
- Requires content analysis engine to determine which plugins are needed
- Need plugin metadata to define applicability rules

### 3. **Preset Workflows** *
Create common workflow shortcuts:
```bash
adt --prep-for-dita docs/       # runs all DITA prep plugins
adt --clean file.adoc           # runs all cleanup plugins
adt --validate docs/            # runs all validation plugins
```

**Implementation Notes:**
- Can be implemented using existing plugin system
- Requires defining workflow configurations and plugin groupings

## User Experience Improvements

### 4. **Interactive Mode by Default** *
Make CLI interactive when no specific options given:
```bash
adt                             # launches interactive wizard
adt file.adoc                   # interactive mode for single file
```

**Implementation Notes:**
- Requires new interactive interface system
- Can leverage existing GUI components for consistency

### 5. **Better Discovery** *
Add discovery commands:
```bash
adt --scan docs/                # shows what issues were found
adt --recommend file.adoc       # suggests which plugins to run
```

**Implementation Notes:**
- Requires analysis engine to scan files without making changes
- Need recommendation system based on file content patterns

### 6. **Configuration Profiles** *
Allow saved configurations:
```bash
adt --save-config dita-prep     # saves current settings as profile
adt --config dita-prep docs/    # uses saved profile
```

**Implementation Notes:**
- Requires configuration management system
- Need file format for storing profiles (JSON/YAML)

## File Handling Simplification

### 7. **Smart File Detection** ✅ **IMPLEMENTED**
Auto-detect AsciiDoc files with recursive processing by default:
```bash
adt EntityReference docs/       # processes all .adoc files recursively (default)
adt ContentType . -nr           # explicit non-recursive with --no-recursive/-nr flag
```

**✅ Implementation Status:**
- ✅ Recursive processing is now the default for directory operations
- ✅ Added `--no-recursive/-nr` flag for backward compatibility
- ✅ Plugins automatically filter for .adoc files
- ✅ Enhanced user experience with sensible defaults

### 8. **Batch Operations** *
Simplified batch processing:
```bash
adt --all docs/                 # runs all plugins on directory
adt --common file.adoc          # runs most commonly used plugins
```

**Implementation Notes:**
- Requires plugin orchestration system
- Need to define "common" plugin sets based on usage patterns

## Output and Feedback

### 9. **Progress and Context**
Better user feedback:
```bash
adt --verbose                   # shows what's happening (exists)
adt --dry-run --summary         # shows what would change *
adt --report docs/              # generates a report instead of changes *
```

**Implementation Notes:**
- `--verbose` already exists
- Summary and report modes require new output formatting
- Could leverage existing dry-run foundations where available

### 10. **Undo/Backup** *
Safety features:
```bash
adt --backup EntityReference .  # creates backups before changes
adt --undo                      # undoes last operation
```

**Implementation Notes:**
- Requires backup management system
- Need operation history tracking
- Undo requires understanding of reversible operations

## Integration Helpers

### 11. **Git Integration** *
Work with version control:
```bash
adt --staged                    # process only staged files
adt --modified                  # process only modified files
```

**Implementation Notes:**
- Requires Git integration library
- Need to detect Git repository and parse status
- Filter file lists based on Git state

### 12. **Editor Integration** *
Quick editor commands:
```bash
adt --edit file.adoc            # process and open in editor
adt --diff file.adoc            # show changes before applying
```

**Implementation Notes:**
- Requires editor detection and launching
- Diff functionality needs before/after comparison
- Integration with system default editors

## Context-Aware Features

### 13. **Project Detection** *
Auto-configure based on project type:
```bash
adt --init                      # detects project type and suggests config
adt --project-scan              # analyzes entire project structure
```

**Implementation Notes:**
- Requires project type detection algorithms
- Need configuration templates for different project types
- Analysis of directory structure and file patterns

### 14. **Learning Mode** *
Help users learn:
```bash
adt --explain EntityReference   # explains what the plugin does
adt --tutorial                  # interactive tutorial
```

**Implementation Notes:**
- Explanation mode can use existing plugin documentation
- Tutorial requires interactive guidance system
- Could integrate with existing help system

## Implementation Priority

### Phase 1: Low-Hanging Fruit
- **Smart File Detection** (enhance existing functionality)
- **Progress and Context** (`--verbose` exists, enhance others)
- **Preset Workflows** (use existing plugin system)

### Phase 2: User Experience
- **Default Actions** (modify argument parsing)
- **Interactive Mode** (new interface system)
- **Configuration Profiles** (configuration management)

### Phase 3: Advanced Features
- **Smart Plugin Selection** (content analysis engine)
- **Better Discovery** (analysis and recommendation system)
- **Undo/Backup** (operation history and safety)

### Phase 4: Integration
- **Git Integration** (external tool integration)
- **Editor Integration** (system integration)
- **Project Detection** (project analysis)
- **Learning Mode** (educational features)

## Technical Considerations

### Backward Compatibility
All new features should maintain backward compatibility with existing command syntax and behavior.

### Plugin Architecture
Many features can be implemented as enhancements to the existing plugin system rather than core changes.

### Configuration Management
A unified configuration system would support multiple features (profiles, project detection, defaults).

### Error Handling
Enhanced user feedback requires improved error messages and recovery suggestions.

## Success Metrics

- **Reduced learning curve**: New users can accomplish common tasks with fewer commands
- **Fewer support questions**: Better discovery and help reduces user confusion
- **Increased adoption**: Simplified workflows encourage broader usage
- **Power user satisfaction**: Advanced features remain accessible

## Next Steps

1. **User Research**: Survey current users about pain points and desired simplifications
2. **Prototype**: Implement Phase 1 features to validate approach
3. **Documentation**: Update help system and documentation for new features
4. **Testing**: Ensure new simplified commands work reliably across platforms
5. **Migration Guide**: Help existing users adopt new simplified workflows

---

*This design balances simplicity for new users with power and flexibility for advanced users, building on the existing architecture while adding intuitive shortcuts and workflows.*
