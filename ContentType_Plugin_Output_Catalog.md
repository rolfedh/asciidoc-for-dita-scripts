# ContentType Plugin Output Catalog

## Overview
This document catalogs all the different types of outputs that users see when using the ContentType plugin (`adt ContentType -r`).

## Output Categories

### 1. File Processing Status Messages

#### 1.1 File Processing Initiation
```
Checking [filename].adoc...
```
- **Purpose**: Indicates the plugin has started processing a specific file
- **Example**: `Checking installing_docker.adoc...`

#### 1.2 Successful Operations
```
✓ Updated: [TYPE]
✓ Added content type: [TYPE]  
✓ Converted from deprecated content type: [TYPE]
✓ Converted from deprecated module type: [TYPE]
✓ Converted from commented out content type: [TYPE]
```
- **Purpose**: Indicates successful completion of different types of content type operations
- **Visual**: Green checkmark (✓) indicates success
- **Examples**:
  - `✓ Updated: CONCEPT`
  - `✓ Added content type: SNIPPET`
  - `✓ Converted from deprecated content type: CONCEPT`

### 2. Content Analysis Output

#### 2.1 Analysis Initiation
```
🔍 Analyzing file content...
```
- **Purpose**: Indicates the plugin is analyzing file content to suggest a content type
- **Visual**: Magnifying glass emoji (🔍)

#### 2.2 Analysis Results
```
💭 Analysis suggests: [TYPE]
   Based on title: '[title]'
```
- **Purpose**: Shows the AI analysis result and the title that influenced the decision
- **Visual**: Thought bubble emoji (💭)
- **Example**: `💭 Analysis suggests: PROCEDURE` with `Based on title: 'Installing Docker'`

#### 2.3 Analysis Summary
```
Content type not specified. Based on analysis, this appears to be a [TYPE].
Reasoning: [reasoning text]
```
- **Purpose**: Provides a plain text summary of the analysis and reasoning
- **Examples**:
  - `Reasoning: Found procedure pattern: ^\s*\d+\.\s; Found procedure pattern: ^\.\s*Procedure\s*$`
  - `Reasoning: Title doesn't match specific patterns, defaulting to CONCEPT`
  - `Reasoning: Found assembly pattern: include::`

### 3. Interactive User Prompts

#### 3.1 Type Selection Menu
```
Type: 1 ASSEMBLY, 2 CONCEPT, 3 PROCEDURE, 4 REFERENCE, 5 SNIPPET, 6 TBD, 7 Skip
```
- **Purpose**: Presents numbered options for content type selection
- **Options**: 7 total options (6 content types + Skip)

#### 3.2 Suggestion Prompt
```
💡 Suggestion: [number] — Press Enter to accept, 1–7 to choose, or Ctrl+C to quit
```
- **Purpose**: Highlights the recommended choice and provides interaction instructions
- **Visual**: Lightbulb emoji (💡) indicates suggestion
- **The suggested number corresponds to the detected type and shows a lightbulb in the menu**
- **Example**: `💡 Suggestion: 3` with `3 PROCEDURE 💡` in the menu

### 4. Automatic Detection Messages

#### 4.1 Filename-Based Detection
```
💡 Detected from filename: [TYPE]
```
- **Purpose**: Indicates the content type was automatically determined from filename patterns
- **Visual**: Lightbulb emoji (💡)
- **Examples**:
  - `💡 Detected from filename: SNIPPET`
  - `💡 Detected from filename: REFERENCE`

### 5. Error Messages

#### 5.1 Detailed Error Messages
```
ERROR:asciidoc_dita_toolkit.asciidoc_dita.plugins.ContentType:Unexpected error processing file [filename]: [error message]
```
- **Purpose**: Provides full error context including module path and specific error
- **Format**: Standard Python logging format with module path

#### 5.2 User-Friendly Error Messages
```
❌ Error: Unexpected error: [error message]
```
- **Purpose**: Simplified error message for user consumption
- **Visual**: Cross mark emoji (❌) indicates error
- **Example**: `❌ Error: Unexpected error: module 'tty' has no attribute 'cbreak'`

### 6. Visual Separators

#### 6.1 Section Separators
```
========================================
```
- **Purpose**: Visually separates successful operations from the next file processing
- **Only appears after successful operations (✓ messages)**

## Content Type Options

The plugin supports 7 options in the interactive menu:

1. **ASSEMBLY** - Documents that include other documents
2. **CONCEPT** - Explanatory or informational content
3. **PROCEDURE** - Step-by-step instructions
4. **REFERENCE** - Reference material, commands, parameters
5. **SNIPPET** - Reusable content fragments
6. **TBD** - To be determined later
7. **Skip** - Skip processing this file

## Current Issues Identified

1. **TTY Error**: Multiple files are failing with `module 'tty' has no attribute 'cbreak'` error
2. **Inconsistent Error Handling**: Some files show both detailed and user-friendly errors
3. **Empty File Handling**: Files with no content still trigger interactive prompts

## Analysis Patterns

The plugin uses various patterns to detect content types:

- **Procedure Patterns**: `^\s*\d+\.\s` (numbered steps), `^\.\s*Procedure\s*$`
- **Assembly Patterns**: `include::` (file includes)
- **Reference Patterns**: `\|====` (tables), `^\[options="header"\]`, title matching `(reference|commands?|options?|parameters?|settings?|configuration)`
- **Filename Patterns**: Files with `snip_`, `ref_`, `con_`, `proc_` prefixes
- **Default Fallback**: When no patterns match, defaults to CONCEPT