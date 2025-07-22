---
layout: default
title: Plugins
nav_order: 3
has_children: true
permalink: /plugins/
---

# Available Plugins

ADT provides specialized plugins to address different DITA compliance issues. Each plugin focuses on specific requirements from the DITA 1.3 specification.

## Content Validation Plugins

These plugins ensure your AsciiDoc content follows DITA structural requirements:

### [ExampleBlock]({% link plugins/ExampleBlock.md %})
{: .d-inline-block }

Stable
{: .label .label-green }

Ensures example blocks are placed in valid locations according to DITA 1.3 requirements.

**Common issues fixed:**
- Example blocks within sections
- Nested example blocks
- Example blocks in lists or other containers

---

### ContentType
{: .d-inline-block }

Coming Soon
{: .label .label-yellow }

Validates and fixes content type declarations for DITA compatibility.

---

### [ValeFlagger]({% link plugins/ValeFlagger.md %})
{: .d-inline-block }

Stable
{: .label .label-green }

Automatically checks AsciiDoc files for DITA compatibility using Vale linter and inserts helpful flags.

**Common issues detected:**
- Heading capitalization problems
- Terminology inconsistencies
- Missing content structure elements
- Style and grammar issues

---

### CrossReference
{: .d-inline-block }

Coming Soon
{: .label .label-yellow }

Fixes cross-reference formats to ensure they work in DITA output.

---

### EntityReference
{: .d-inline-block }

Coming Soon
{: .label .label-yellow }

Converts HTML entities to AsciiDoc attributes for proper DITA processing.

## Analysis and Migration Plugins

These plugins help analyze and transform your content structure:

### ContextAnalyzer
{: .d-inline-block }

Coming Soon
{: .label .label-yellow }

Analyzes document context usage patterns.

---

### ContextMigrator
{: .d-inline-block }

Coming Soon
{: .label .label-yellow }

Migrates context-suffixed IDs to DITA-compatible formats.

---

### DirectoryConfig
{: .d-inline-block }

Coming Soon
{: .label .label-yellow }

Manages directory-level configuration for batch processing.

---

## Workflow Management Plugins

These plugins orchestrate and manage multi-module processing workflows:

### [UserJourney]({% link plugins/UserJourney.md %})
{: .d-inline-block }

Stable
{: .label .label-green }

Orchestrates multi-module document processing workflows with state persistence and progress tracking.

**Key features:**
- Persistent workflow state across interruptions
- Module dependency resolution and sequencing
- Rich CLI interface with progress visualization
- Atomic state management with corruption recovery
