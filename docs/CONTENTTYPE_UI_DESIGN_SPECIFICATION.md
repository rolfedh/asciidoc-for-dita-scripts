# ContentType Plugin Interactive UI Design Specification

## Executive Summary

This document defines a comprehensive user interface design for the ContentType plugin, focusing on intuitive interaction patterns, clear feedback mechanisms, and flexible automation levels to accommodate diverse user workflows and preferences.

## Context & Requirements

### Vale Rule Integration

Based on the [AsciiDocDITA Vale ContentType rule](https://github.com/jhradilek/asciidoctor-dita-vale):

> **Rule Objective**: Without an explicit content type definition, the Vale style cannot reliably report problems related to procedure modules such as TaskSection or TaskExample. Add the correct `:_mod-docs-content-type:` definition at the top of the file.

### Content Type Standards

The `:_mod-docs-content-type:` attribute must be:
- **Positioned**: At the top of the file, above the ID and title
- **Format**: `:_mod-docs-content-type: TYPE_VALUE`
- **Values**: ASSEMBLY, CONCEPT, PROCEDURE, REFERENCE, SNIPPET, TBD

#### Correct Example
```asciidoc
:_mod-docs-content-type: CONCEPT

[id="my-concept-module-a_{context}"]
= My concept module A
```

*Reference: [Red Hat Modular Docs Examples](https://github.com/redhat-documentation/modular-docs/tree/main/modular-docs-manual/files)*

## User Experience Framework

### 1. Automation Levels

Users should be able to choose their preferred level of automation:

- **🤖 Auto-fix**: Automatically apply all fixes without prompting
- **🔍 Review Mode**: Flag issues but make no changes (output report only)  
- **🎯 Interactive**: Prompt for each change with context and options
- **📝 Guided**: Step-by-step assistance with explanations

### 2. Issue Severity Levels

Three distinct severity levels with appropriate visual and behavioral cues:

- **💡 SUGGESTION**: Optional improvements (blue/cyan color scheme)
- **⚠️ WARNING**: Recommended fixes (yellow/amber color scheme)  
- **❌ ERROR**: Critical issues requiring attention (red color scheme)

## Command Line Interface Design

### Global Options

```bash
asciidoc-dita-toolkit ContentType [options] [files...]

Options:
  --mode, -m          Interaction mode: auto|review|interactive|guided (default: interactive)
  --severity, -s      Minimum severity to process: suggestion|warning|error (default: warning)
  --batch            Apply the same choice to all similar issues
  --dry-run          Show what would be changed without making changes
  --format           Output format: text|json|markdown (default: text)
  --config           Configuration file path for custom settings
  --quiet, -q        Suppress non-essential output
  --verbose, -v      Enable detailed logging
```

### Interactive Interface Components

#### 1. Context Headers

```text
📄 File: src/modules/my-concept.adoc (Line 3)
💡 SUGGESTION: Deprecated content type attribute detected
```

#### 2. Issue Explanation

```text
Found: :_content-type: PROCEDURE
Expected: :_mod-docs-content-type: PROCEDURE

The :_content-type: attribute is deprecated. Modern Vale rules require 
:_mod-docs-content-type: for proper validation.
```

#### 3. Action Choice Menu

```text
Choose an action:
  [y] Replace with :_mod-docs-content-type: PROCEDURE
  [n] Skip this change
  [a] Apply to all similar issues in this session
  [?] Show more details
  [q] Quit and save progress

Choice [y/n/a/?/q]: 
```

### Progress Feedback

```text
Processing: src/modules/my-concept.adoc [2/15] ████████░░░░░░░░░░ 53%
Issues found: 3 suggestions, 1 warning, 0 errors
Applied: 2 fixes, Skipped: 1, Remaining: 1
```

## Content Type Issue Scenarios & Interaction Patterns

### Overview

The ContentType plugin handles six primary scenarios, each requiring tailored user interaction patterns based on the issue type, severity, and user preferences.

### Scenario 1: Deprecated `:_content-type:` Attribute

**File**: `ignore_content_type.expected`

**Issue**: Deprecated `:_content-type:` attribute detected

```asciidoc
:_content-type: PROCEDURE

= Topic title

A paragraph.
```

**UI Interaction Pattern**:

```text
⚠️ WARNING: Deprecated content type attribute detected
File: src/modules/procedure.adoc (Line 1)

Found: :_content-type: PROCEDURE
Issue: This attribute format is deprecated in modern Vale rules

Suggested fix: Replace with :_mod-docs-content-type: PROCEDURE

Actions:
  [y] Apply fix (recommended)
  [n] Skip this file
  [a] Apply to all deprecated attributes in session
  [?] Show documentation link
  [q] Quit

Choice [y/n/a/?/q]: 
```

**Batch Mode Option**:
```text
✅ Found 5 more files with deprecated :_content-type: attributes
   Apply the same fix to all? [Y/n]
```

### Scenario 2: Already Correct Content Type

**File**: `ignore_defined_type.expected`

**Issue**: No action needed - content type is correctly defined

```asciidoc
:_mod-docs-content-type: PROCEDURE

= Topic title

A paragraph.
```

**UI Interaction Pattern**:
```text
✅ PASS: Content type correctly defined
File: src/modules/procedure.adoc
Status: :_mod-docs-content-type: PROCEDURE (valid)
```

### Scenario 3: Deprecated `:_module-type:` Attribute

**File**: `ignore_module_type.expected`

**Issue**: Legacy `:_module-type:` attribute detected

```asciidoc
:_module-type: PROCEDURE

= Topic title

A paragraph.
```

**UI Interaction Pattern**:

```text
💡 SUGGESTION: Legacy attribute format detected
File: src/modules/procedure.adoc (Line 1)

Found: :_module-type: PROCEDURE
Note: This is an older format that should be updated

Suggested fix: Replace with :_mod-docs-content-type: PROCEDURE

Actions:
  [y] Apply modernization fix
  [n] Keep legacy format
  [a] Modernize all legacy attributes
  [?] Show migration guide
  [q] Quit

Choice [y/n/a/?/q]: 
```

### Scenario 4: Misplaced Content Type

**File**: `ignore_preceding_content.expected`

**Issue**: Content type attribute placed after title instead of before

```asciidoc
= Topic title
:_mod-docs-content-type: PROCEDURE

A paragraph.
```

**UI Interaction Pattern**:

```text
⚠️ WARNING: Content type attribute misplaced
File: src/modules/procedure.adoc (Line 2)

Issue: :_mod-docs-content-type: should be at the top of the file
Current position: After title (line 2)
Required position: Before ID and title (line 1)

Actions:
  [y] Move to correct position
  [n] Leave as-is
  [a] Fix all misplaced attributes
  [?] Show positioning guide
  [q] Quit

Choice [y/n/a/?/q]:
```

### Scenario 5: Commented Out Content Type

**File**: `report_comments.expected`

**Issue**: Required content type attribute is commented out

```asciidoc
//:_mod-docs-content-type: PROCEDURE

= Topic title

A paragraph.
```

**UI Interaction Pattern**:

```text
❌ ERROR: Required content type attribute is disabled
File: src/modules/procedure.adoc (Line 1)

Issue: Content type is commented out
Impact: Vale rules cannot validate this file properly

Actions:
  [y] Uncomment attribute (recommended)
  [n] Leave commented
  [a] Uncomment all similar cases
  [d] Delete comment entirely
  [?] Show why this is required
  [q] Quit

Choice [y/n/a/d/?/q]:
```

### Scenario 6: Missing Content Type

**File**: `report_missing_type.expected`

**Issue**: No content type attribute present

```asciidoc
= Topic title

A paragraph.
```

**UI Interaction Pattern**:

```text
❌ ERROR: Missing required content type attribute
File: src/modules/unknown.adoc

Issue: No :_mod-docs-content-type: attribute found
Impact: Vale cannot validate this file type

Select content type:
  1. ASSEMBLY     - Collection of modules on a topic
  2. CONCEPT      - Conceptual overview information  
  3. PROCEDURE    - Step-by-step instructions
  4. REFERENCE    - Lookup information (tables, lists)
  5. SNIPPET      - Reusable content fragment
  6. TBD          - Temporary placeholder for unclassified or legacy content requiring analysis

Actions:
  [1-6] Select type and add attribute
  [?] Show content type guide
  [s] Skip this file
  [q] Quit

Choice [1-6/?/s/q]:
```

### Scenario 7: Empty Content Type Value

**File**: `report_missing_value.expected`

**Issue**: Content type attribute exists but has no value

```asciidoc
:_mod-docs-content-type:

= Topic title

A paragraph.
```

**UI Interaction Pattern**:

```text
❌ ERROR: Content type attribute has no value
File: src/modules/unknown.adoc (Line 1)

Found: :_mod-docs-content-type:
Issue: Missing required value

Select content type:
  1. ASSEMBLY     - Collection of modules on a topic
  2. CONCEPT      - Conceptual overview information  
  3. PROCEDURE    - Step-by-step instructions
  4. REFERENCE    - Lookup information (tables, lists)
  5. SNIPPET      - Reusable content fragment
  6. TBD          - Temporary placeholder for unclassified or legacy content requiring analysis

Actions:
  [1-6] Select type and set value
  [?] Show content type guide
  [s] Skip this file
  [q] Quit

Choice [1-6/?/s/q]:
```

## Content Type Guidelines

### Standard Content Types

1. **ASSEMBLY** - Collection of modules that covers a complete user story or workflow
2. **CONCEPT** - Explains what something is, provides background information and context
3. **PROCEDURE** - Step-by-step instructions for completing a specific task
4. **REFERENCE** - Quick lookup information such as tables, lists, or specifications
5. **SNIPPET** - Reusable content fragments included in other modules

### Special Content Type

**TBD (To Be Determined)** - Temporary classification for content that requires analysis

**Use TBD when:**

- Content type cannot be immediately determined from file analysis
- Legacy documentation requires expert review to classify properly
- Mixed content needs refactoring into separate, focused modules  
- Content doesn't clearly fit existing categories and may need custom classification
- Files are placeholders or drafts awaiting proper content development

**TBD Workflow:**

```text
File marked as TBD → Content analysis → Expert review → Reclassification
                                                      ↓
                                    Refactor if needed → Apply correct type
```

**Note**: TBD should be considered a temporary state. Content marked as TBD should be reviewed and reclassified during regular documentation audits.

## Advanced Features

### Smart Type Detection

```text
🔍 ANALYZING: Content patterns detected...

Based on file analysis:
- Contains numbered steps → Likely PROCEDURE
- Has step verification → Confirms PROCEDURE type

Suggested: :_mod-docs-content-type: PROCEDURE

Accept suggestion? [Y/n]
If 'n': Show full content type menu [1-6]
```

**Alternative scenario for unclear content:**

```text
🔍 ANALYZING: Content patterns detected...

Based on file analysis:
- Mixed content types detected
- No clear procedural or conceptual pattern
- May require content refactoring

Suggested: :_mod-docs-content-type: TBD

This content may need expert review to determine the appropriate type.
Accept TBD classification? [Y/n]
```

### Batch Operations Summary

```text
📊 BATCH OPERATION COMPLETE

Files processed: 15
✅ Fixed: 8 files
⚠️  Warnings: 3 files  
❌ Errors: 2 files
⏭️  Skipped: 2 files

View detailed report? [Y/n]
```

### Configuration Persistence

```text
💾 SAVE PREFERENCES

Your choices this session:
- Auto-fix deprecated attributes: Yes
- Skip commented attributes: No  
- Default content type: PROCEDURE

Save as default for future sessions? [Y/n]
```

## Implementation Guidelines

### Color Coding Standards

```text
💡 SUGGESTION (Blue/Cyan):   Optional improvements, best practices
⚠️ WARNING (Yellow/Amber):   Recommended fixes, compatibility issues  
❌ ERROR (Red):              Critical problems, validation failures
✅ SUCCESS (Green):          Confirmed fixes, valid states
📄 INFO (Gray):              Contextual information, file details
🔍 ANALYSIS (Purple):        Smart detection, pattern recognition
```

### Keyboard Shortcuts

```text
Global Navigation:
  1-9           Select numbered options (content types, actions)
  Enter         Confirm current selection
  Space         Toggle selection (multi-choice scenarios)
  Tab           Next field/section
  Shift+Tab     Previous field/section
  
Quick Actions:
  y             Yes/Apply
  n             No/Skip  
  a             Apply to all
  s             Skip all similar
  ?             Help/Documentation
  q             Quit with confirmation
  
Advanced:
  Ctrl+C        Emergency quit
  Ctrl+Z        Undo last action
  r             Retry/Refresh analysis
```

### Responsive Design Principles

#### Terminal Width Adaptation

```text
Narrow terminals (< 80 chars):
┌─ File: procedure.adoc (L:1) ─┐
│ ❌ ERROR: Missing content type│
│                              │
│ [y] Add PROCEDURE            │
│ [n] Skip file                │
│ [?] Help                     │
└──────────────────────────────┘

Wide terminals (≥ 120 chars):
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 📄 File: src/modules/user-authentication-procedure.adoc (Line 1, Column 1)                       │
│ ❌ ERROR: Missing required content type attribute                                                  │
│                                                                                                   │
│ Issue Details:                              │ Suggested Actions:                                │
│ • No :_mod-docs-content-type: found         │ [y] Add PROCEDURE type (recommended)             │
│ • Vale cannot validate module type          │ [c] Choose different type                        │
│ • Required for proper documentation         │ [s] Skip this file                               │
│                                             │ [?] Show content type guide                      │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Error Handling & Recovery

#### Network/File Access Errors

```text
🚫 ERROR: Cannot access file
Path: /protected/documentation/secret.adoc
Reason: Permission denied

Actions:
  [r] Retry with sudo
  [s] Skip this file  
  [c] Change file permissions
  [q] Quit processing

Choice [r/s/c/q]:
```

#### Malformed Content Detection

```text
⚠️ WARNING: File contains parsing errors
File: src/modules/broken.adoc (Line 15)

Issues detected:
• Unclosed code block (line 15)
• Invalid attribute syntax (line 23)
• Missing title separator (line 1)

Actions:
  [i] Ignore and process anyway
  [f] Fix syntax errors first
  [s] Skip this file
  [?] Show syntax guide

Choice [i/f/s/?]:
```

### Accessibility Features

#### Screen Reader Support

```text
NVDA/JAWS Compatible Output:
"Processing file 3 of 15. procedure dot adoc. Error detected. Missing required content type attribute. Navigation options: Y for yes apply fix, N for no skip file, A for apply to all, Question mark for help, Q for quit."
```

#### High Contrast Mode

```text
High Contrast Mode Active:
[ERROR]   Missing content type attribute
[WARNING] Deprecated format detected  
[INFO]    File: procedure.adoc
[SUCCESS] Fix applied successfully
```

### Internationalization Considerations

#### Message Templating

```yaml
# messages.yml
errors:
  missing_content_type:
    en: "Missing required content type attribute"
    es: "Falta el atributo de tipo de contenido requerido"
    fr: "Attribut de type de contenu requis manquant"
    
actions:
  apply_fix:
    en: "Apply fix"
    es: "Aplicar corrección"
    fr: "Appliquer la correction"
```

## Testing & Validation Framework

### User Interface Testing Scenarios

```yaml
test_scenarios:
  interactive_mode:
    - scenario: "User selects 'y' for deprecated attribute"
      expected: "Attribute replaced successfully"
      
    - scenario: "User selects 'a' for batch operation"
      expected: "All similar issues processed"
      
    - scenario: "User presses '?' for help"
      expected: "Context-sensitive help displayed"
      
  edge_cases:
    - scenario: "Invalid keyboard input"
      expected: "Clear error message and prompt retry"
      
    - scenario: "Terminal resize during operation"
      expected: "Interface adapts gracefully"
```

### Performance Benchmarks

```text
Target Performance Standards:
• File analysis: < 100ms per file
• UI responsiveness: < 50ms for key press
• Memory usage: < 10MB for 1000 files
• Startup time: < 500ms
```

### Usability Metrics

```text
Success Criteria:
• Task completion rate: > 95%
• Error recovery rate: > 90% 
• User satisfaction: > 4.5/5.0
• Learning curve: < 5 minutes for basic tasks
```

## Configuration & Customization

### User Preferences File

```yaml
# ~/.config/asciidoc-dita-toolkit/preferences.yml
interaction:
  default_mode: "interactive"
  auto_batch_similar: true
  show_progress_bar: true
  confirm_destructive_actions: true
  
display:
  color_scheme: "auto"  # auto, light, dark, high-contrast
  emoji_icons: true
  compact_mode: false
  terminal_width: "auto"
  
content_types:
  smart_detection: true
  preferred_default: "CONCEPT"
  suggest_based_on_filename: true
  allow_tbd_classification: true
  prompt_for_tbd_review: true
  
advanced:
  backup_before_changes: true
  max_batch_size: 50
  timeout_seconds: 30
```

### Plugin Integration Points

```python
# For plugin developers
class ContentTypeUI:
    def prompt_user(self, context: IssueContext) -> UserChoice:
        """
        Present issue to user and return their choice
        
        Args:
            context: Issue details, file info, suggested fixes
            
        Returns:
            UserChoice: User's selected action and any parameters
        """
        pass
        
    def show_progress(self, current: int, total: int, file: str):
        """Update progress display"""
        pass
        
    def display_summary(self, results: ProcessingResults):
        """Show final processing summary"""
        pass
```

## Future Enhancements

<!-- ### Planned Features

1. **Visual Mode**: GUI interface for non-terminal environments
2. **Web Interface**: Browser-based processing for remote workflows  
3. **IDE Integration**: VS Code, IntelliJ, Vim plugins
4. **AI Assistance**: Content type suggestion based on file analysis
5. **Collaborative Mode**: Team-wide preference sharing
6. **Analytics Dashboard**: Usage patterns and error trends -->

### Extensibility Framework

```python
# Plugin API for custom interaction modes
class CustomInteractionMode(BaseInteractionMode):
    def handle_issue(self, issue: ContentTypeIssue) -> Resolution:
        # Custom logic for handling specific issue types
        pass
        
    def get_user_preference(self, choices: List[str]) -> str:
        # Custom preference gathering
        pass
```

## TBD Content Management

### TBD Status Reporting

```text
📊 TBD CONTENT SUMMARY

Files classified as TBD: 3
├── src/legacy/mixed-content.adoc (45 days old)
├── src/drafts/planning-doc.adoc (12 days old)  
└── src/modules/unclear-purpose.adoc (3 days old)

Recommended actions:
• Schedule content review for files > 30 days old
• Consider refactoring mixed content into focused modules
• Request subject matter expert review for unclear content

Generate detailed TBD report? [Y/n]
```

### Batch TBD Operations

```text
🔄 BATCH TBD MANAGEMENT

Options for TBD content:
  [1] Review all TBD files interactively
  [2] Generate TBD audit report  
  [3] Set TBD review reminders
  [4] Export TBD list for team review
  [5] Mark TBD files for deletion (if obsolete)
  [q] Return to main menu

Choice [1-5/q]:
```

This comprehensive UI design specification provides a complete framework for implementing an intuitive, accessible, and highly functional user interface for the ContentType plugin. The addition of the TBD content type provides flexibility for handling edge cases and legacy content, ensuring excellent user experience across diverse workflows and technical environments while maintaining clear pathways for content classification and improvement.
