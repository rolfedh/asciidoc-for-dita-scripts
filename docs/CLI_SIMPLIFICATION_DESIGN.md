# CLI Simplification Design Document

This document outlines improvements to make the AsciiDoc DITA Toolkit CLI more user-friendly and intuitive. Items marked with ✅ are implemented, items marked with an asterisk (*) require new core functionality to be developed.

## Command Structure Simplification

### 1. **Default Actions** ✅
Make the most common operations work without flags:
```bash
adt EntityReference file.adoc    # auto-detect it's a file
adt ContentType docs/            # auto-detect it's a directory
```

**Implementation Status:** ✅ **COMPLETED**
- Modified argument parsing in `file_utils.py` to detect file vs directory automatically
- Updated ContentType plugin to handle implicit target detection
- Users can now run `adt ContentType <file_or_dir>` without `-f` or `-d` flags
- Recursive processing is enabled by default for directories

### 2. **Smart Plugin Selection** *
Auto-run appropriate plugins based on file content:
```bash
adt --auto file.adoc            # analyzes file and runs relevant plugins
adt --fix-all docs/             # runs all applicable plugins
```

**Implementation Notes:**
- Requires content analysis engine to determine which plugins are needed
- Need plugin metadata to define applicability rules

### 3. **Preset Workflows** * see [Preset Workflows](#preset-workflows)

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

### 7. **Smart File Detection** ✅ **IMPLEMENTED + RED HAT STANDARDS READY**
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

**🚀 Ready for Red Hat Modular Docs Integration:**
- Red Hat modular documentation standards provide clear content type patterns
- Templates define standard `:_mod-docs-content-type:` attributes (CONCEPT, PROCEDURE, REFERENCE, ASSEMBLY, SNIPPET)
- File naming conventions (`con_`, `proc_`, `ref_`, `assembly_` prefixes) can be auto-detected
- Content structure analysis can identify module types based on:
  - Gerund vs noun phrase titles
  - Presence of numbered procedures, prerequisites, verification sections
  - Include statements indicating assemblies
  - Structured data indicating reference modules

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


**Implementation Notes:**
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
- **Smart File Detection** ✅ **IMPLEMENTED + SMART ANALYSIS ENHANCED** (enhance existing functionality)
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

## ContentType Plugin Enhancement ✅

### **Smart Content Type Detection** ✅ **COMPLETED**
Enhanced ContentType plugin with comprehensive analysis and user experience improvements:

```bash
adt ContentType docs/            # Smart analysis with interactive prompts
adt ContentType file.adoc        # Auto-detection with intelligent suggestions
```

**✅ Implementation Status: FULLY COMPLETED**

#### **Smart Analysis Features:**
- ✅ **Title Analysis**: Detects content types based on title patterns
  - Gerund titles (Installing, Configuring) → PROCEDURE 
  - Noun phrases (Docker commands) → REFERENCE
  - Concept-style titles → CONCEPT
- ✅ **Content Pattern Recognition**: 
  - Numbered procedure steps → PROCEDURE
  - Definition lists and tables → REFERENCE  
  - Include statements → ASSEMBLY
- ✅ **Filename Detection**: Auto-detection for standard prefixes
  - `proc_`, `con_`, `ref_`, `assembly_`, `snip_` prefixes
- ✅ **Deprecated Attribute Conversion**: 
  - `:_content-type:` → `:_mod-docs-content-type:`
  - `:_module-type:` → `:_mod-docs-content-type:`

#### **User Experience Improvements:**
- ✅ **Interactive Prompts**: When content type cannot be determined automatically
- ✅ **Intelligent Pre-selection**: Most likely content type is pre-selected in prompts
- ✅ **Clear Visual Feedback**: Colored output with success/warning indicators
- ✅ **Separator Lines**: Visual separation between file processing for clarity
- ✅ **Comprehensive Coverage**: Handles missing, empty, and commented attributes

#### **Ready for Production:**
- ✅ Comprehensive test suite with backup/restore system
- ✅ Documentation updated for new workflow
- ✅ Safety features for beta testing and production use
- ✅ Full Red Hat modular documentation standards compliance

## Preset Workflows

I'll elaborate on the **Preset Workflows** concept from line 192. This is an interesting feature that could be implemented using the existing plugin system. Let me explain what this means and how it could work:

## **Preset Workflows** - Deep Dive

The "Preset Workflows" concept refers to creating predefined combinations of plugins that users can run with a single command, rather than having to run each plugin individually. This would dramatically simplify common documentation workflows.

### **Current State vs Vision**

**Current Reality:**
```bash
# Users must run plugins individually
adt ContentType docs/
adt EntityReference docs/
# (hypothetically, if more plugins existed)
```

**Preset Workflows Vision:**
```bash
# Single command runs multiple related plugins
adt --prep-for-dita docs/       # runs all DITA preparation plugins
adt --clean file.adoc           # runs all cleanup/formatting plugins  
adt --validate docs/            # runs all validation plugins
```

### **How It Could Work with Existing Plugin System**

The current plugin architecture in toolkit.py already has the foundation for this:

1. **Plugin Discovery**: The system already discovers plugins dynamically
2. **Plugin Registration**: Each plugin registers itself with `register_subcommand()`
3. **Plugin Execution**: Plugins are executed through their `func()` method

### **Implementation Approach**

#### **1. Plugin Metadata Enhancement**
Each plugin could declare categories/tags:

```python
# In ContentType.py
__description__ = "Add content type labels"
__categories__ = ["dita-prep", "cleanup", "validation"]
__priority__ = 1  # execution order within workflows
```

#### **2. Workflow Configuration**
Define workflows in a configuration file or code:

```python
# workflows.py
WORKFLOWS = {
    "prep-for-dita": {
        "description": "Prepare files for DITA publishing",
        "plugins": ["ContentType", "EntityReference"],
        "order": ["ContentType", "EntityReference"]  # execution order
    },
    "cleanup": {
        "description": "Clean up and format files",
        "plugins": ["EntityReference", "ContentType"],
        "order": ["EntityReference", "ContentType"]
    }
}
```

#### **3. Workflow Executor**
Add workflow support to the main CLI:

```python
# In toolkit.py
parser.add_argument(
    "--prep-for-dita",
    metavar="PATH", 
    help="Run all DITA preparation plugins on specified path"
)
```

### **Benefits of This Approach**

1. **User Simplicity**: One command instead of multiple
2. **Consistency**: Ensures plugins run in optimal order
3. **Efficiency**: Batch processing reduces overhead
4. **Discoverability**: Users learn about plugin combinations
5. **Extensibility**: Easy to add new workflows as plugins evolve

### **Example Workflows for AsciiDoc DITA**

Given the current two plugins (`ContentType` and `EntityReference`):

```bash
# Full DITA preparation workflow
adt --prep-for-dita docs/
# Internally runs:
# 1. ContentType docs/     # Add missing content type attributes
# 2. EntityReference docs/ # Fix HTML entity references

# Quick cleanup workflow  
adt --cleanup file.adoc
# Internally runs both plugins on a single file

# Validation-only workflow (future)
adt --validate docs/ --dry-run
# Runs plugins in report-only mode to show issues
```

### **Why This Makes Sense**

The **"use existing plugin system"** note is particularly insightful because:

1. **No Core Changes Needed**: The plugin architecture already supports this
2. **Plugin Independence**: Each plugin remains standalone and testable
3. **Workflow Flexibility**: Different workflows can combine plugins differently
4. **Easy Maintenance**: Adding new plugins automatically makes them available for workflows

### **Current Implementation Gap**

Right now, this would require:
1. Adding workflow configuration system
2. Enhancing the argument parser to support workflow flags
3. Creating a workflow executor that runs multiple plugins in sequence
4. Ensuring plugins can be composed safely (no conflicts)

This is a **Phase 1** feature because it builds on existing infrastructure rather than requiring new core functionality - making it relatively straightforward to implement while providing significant user value.

Would you like me to elaborate on any specific aspect of how preset workflows could be implemented?