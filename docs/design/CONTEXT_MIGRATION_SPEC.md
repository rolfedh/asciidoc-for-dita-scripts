# Context Migration Implementation Specification

## Overview

This specification outlines the implementation of a phased migration strategy to remove `_{context}` suffixes from AsciiDoc IDs and transition to path-based cross-references.

## Goals

1. **Remove `_{context}` suffixes** from AsciiDoc IDs (e.g., `[id="topic_banana"]` → `[id="topic"]`)
2. **Transition to path-based xrefs** (e.g., `xref:filename.adoc#topic[]`)
3. **Maintain external link compatibility** during migration
4. **Ensure all internal xrefs remain functional**
5. **Provide comprehensive validation and reporting**

## Implementation Phases

### Phase 1: Analysis & Reporting Tool

**Purpose**: Understand the scope and complexity before making any changes.

#### Requirements

Create a new plugin: `ContextAnalyzer`

**File**: `asciidoc_dita_toolkit/asciidoc_dita/plugins/ContextAnalyzer.py`

#### Core Functionality

```python
class ContextAnalyzer:
    """
    Analyzes AsciiDoc documentation to report on context usage
    and potential migration complexity.
    """
    
    def __init__(self):
        # Regex patterns
        self.id_with_context_regex = re.compile(r'\[id="([^"]+)_([^"]+)"\]')
        self.xref_regex = re.compile(r'xref:([^#\[]+)(?:#([^#\[]+))?(\[.*?\])')
        self.link_regex = re.compile(r'link:([^#\[]+)(?:#([^#\[]+))?(\[.*?\])')
        self.context_attr_regex = re.compile(r'^:context:\s*(.+)$', re.MULTILINE)
        
    def analyze_directory(self, root_dir: str) -> AnalysisReport
    def analyze_file(self, filepath: str) -> FileAnalysis
    def detect_id_collisions(self) -> List[CollisionReport]
    def generate_report(self) -> str
```

#### Data Structures

```python
@dataclass
class IDWithContext:
    id_value: str           # Full ID (e.g., "topic_banana")
    base_id: str           # Base without context (e.g., "topic")
    context_value: str     # Context part (e.g., "banana")
    filepath: str
    line_number: int

@dataclass
class XrefUsage:
    target_id: str
    target_file: str       # Empty if same-file reference
    filepath: str          # File containing the xref
    line_number: int
    full_match: str        # Complete xref text

@dataclass
class CollisionReport:
    base_id: str
    conflicting_files: List[str]
    suggested_resolution: str

@dataclass
class FileAnalysis:
    filepath: str
    context_attributes: List[str]
    ids_with_context: List[IDWithContext]
    xref_usages: List[XrefUsage]
    link_usages: List[XrefUsage]

@dataclass
class AnalysisReport:
    total_files_scanned: int
    files_with_context_ids: int
    total_context_ids: int
    total_xrefs: int
    total_links: int
    potential_collisions: List[CollisionReport]
    file_analyses: List[FileAnalysis]
```

#### Command Line Interface

```bash
# Analyze current directory
adt ContextAnalyzer .

# Analyze specific directory with detailed output
adt ContextAnalyzer /path/to/docs --detailed

# Generate JSON report
adt ContextAnalyzer . --format json --output analysis.json

# Check for potential ID collisions only
adt ContextAnalyzer . --collisions-only
```

#### Report Output

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

=== Files Requiring Migration ===
modules/example.adoc:
  - [id="topic_banana"] → [id="topic"] (line 1)
  - xref:other_file#section_apple[] → needs update (line 15)

=== Summary ===
- Low Risk: 45 files (simple context removal)
- Medium Risk: 8 files (potential collisions)
- High Risk: 2 files (complex multi-context scenarios)

Recommended approach: Batch migration by risk level
```

### Phase 2: Context Migration Tool

**Purpose**: Perform the actual migration with safety checks.

#### Requirements

Create a new plugin: `ContextMigrator`

**File**: `asciidoc_dita_toolkit/asciidoc_dita/plugins/ContextMigrator.py`

#### Core Functionality

```python
class ContextMigrator:
    """
    Migrates AsciiDoc files from context-suffixed IDs to context-free IDs
    with comprehensive validation and rollback capabilities.
    """
    
    def __init__(self):
        self.dry_run = False
        self.backup_dir = None
        self.migration_log = []
        
    def migrate_directory(self, root_dir: str, options: MigrationOptions) -> MigrationResult
    def migrate_file(self, filepath: str) -> FileMigrationResult
    def remove_context_from_ids(self, content: str, filepath: str) -> Tuple[str, List[IDChange]]
    def update_xrefs_and_links(self, content: str, id_map: Dict[str, str]) -> Tuple[str, List[XrefChange]]
    def resolve_id_collisions(self, collisions: List[str], filepath: str) -> Dict[str, str]
    def create_backup(self, filepath: str) -> str
    def validate_migration(self, filepath: str) -> ValidationResult
```

#### Migration Strategy

1. **Atomic File Processing**: Each file is processed completely before moving to the next
2. **Backup Creation**: Original files are backed up before modification
3. **Collision Resolution**: Automatic numbering for duplicate IDs (`topic-1`, `topic-2`)
4. **Validation**: Post-migration validation ensures all xrefs resolve
5. **Rollback Support**: Failed migrations can be reversed

#### Data Structures

```python
@dataclass
class MigrationOptions:
    dry_run: bool = False
    create_backups: bool = True
    backup_dir: str = ".migration_backups"
    resolve_collisions: bool = True
    validate_after: bool = True

@dataclass
class IDChange:
    old_id: str
    new_id: str
    line_number: int

@dataclass
class XrefChange:
    old_xref: str
    new_xref: str
    line_number: int

@dataclass
class FileMigrationResult:
    filepath: str
    success: bool
    id_changes: List[IDChange]
    xref_changes: List[XrefChange]
    errors: List[str]
    backup_path: str

@dataclass
class ValidationResult:
    filepath: str
    valid: bool
    broken_xrefs: List[str]
    warnings: List[str]
```

#### Command Line Interface

```bash
# Dry run migration
adt ContextMigrator . --dry-run

# Migrate with backups
adt ContextMigrator . --backup-dir .migration_backup

# Migrate specific files only
adt ContextMigrator modules/proc_*.adoc

# Migrate and validate
adt ContextMigrator . --validate

# Resume from previous migration log
adt ContextMigrator . --resume migration.log
```

### Phase 3: Enhanced CrossReference Plugin

**Purpose**: Update existing CrossReference plugin to handle migration scenarios.

#### Enhancements Required

1. **Validation Mode**: Check for broken xrefs without fixing
2. **Context-Aware Processing**: Handle mixed old/new ID scenarios
3. **Comprehensive Reporting**: Detailed validation reports

#### New Command Options

```bash
# Validation only
adt CrossReference . --check-only

# Generate validation report
adt CrossReference . --validate --report validation.json

# Process with context migration awareness
adt CrossReference . --migration-mode
```

#### Enhanced Functionality

```python
class CrossReferenceProcessor:
    # ...existing code...
    
    def __init__(self):
        # ...existing code...
        self.validation_only = False
        self.migration_mode = False
        self.broken_xrefs = []
        
    def validate_xrefs(self, file: str) -> List[BrokenXref]
    def generate_validation_report(self) -> ValidationReport
    def prefer_context_free_ids(self, old_id: str, file_path: str) -> str
```

## Implementation Guidelines

### Error Handling

- **Graceful Degradation**: Continue processing other files if one fails
- **Detailed Logging**: Comprehensive logs for debugging
- **User Feedback**: Clear progress indicators and error messages

### Testing Strategy

1. **Unit Tests**: Test regex patterns and core logic
2. **Integration Tests**: Test on sample documentation sets
3. **Regression Tests**: Ensure existing functionality remains intact

### Safety Measures

1. **Mandatory Backups**: Never modify files without backups
2. **Dry Run Default**: All destructive operations default to dry-run
3. **Validation Gates**: Automatic validation after each change
4. **Rollback Scripts**: Automated rollback from backups

### Performance Considerations

- **Memory Efficient**: Process files individually, not all in memory
- **Progress Reporting**: Show progress for large documentation sets
- **Parallel Processing**: Optional parallel file processing for large sets

## File Structure

```
asciidoc_dita_toolkit/asciidoc_dita/plugins/
├── ContextAnalyzer.py      # Phase 1: Analysis tool
├── ContextMigrator.py      # Phase 2: Migration tool
└── CrossReference.py       # Phase 3: Enhanced existing tool

tests/
├── test_context_analyzer.py
├── test_context_migrator.py
└── test_cross_reference_enhanced.py

docs/
├── CONTEXT_MIGRATION_GUIDE.md    # User documentation
└── CONTEXT_MIGRATION_SPEC.md     # This specification
```

## Success Criteria

1. **Zero Data Loss**: No content lost during migration
2. **All Xrefs Functional**: 100% of internal xrefs resolve correctly
3. **Rollback Capable**: Any migration can be completely reversed
4. **Comprehensive Reporting**: Clear visibility into all changes made
5. **Performance Acceptable**: Migration completes in reasonable time
6. **User-Friendly**: Clear documentation and intuitive commands

## Risk Mitigation

1. **Phased Approach**: Each phase can be tested independently
2. **Backup Strategy**: Multiple backup mechanisms
3. **Validation Framework**: Comprehensive pre and post-migration validation
4. **Selective Migration**: Ability to migrate subsets for testing
5. **Expert Review**: Analysis reports enable human review before migration

This specification provides a comprehensive, safe approach to context migration that prioritizes data integrity and provides multiple safety nets throughout the process.