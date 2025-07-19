---
layout: default
title: ExampleBlock
parent: Plugins
nav_order: 1
---

# ExampleBlock Plugin
{: .no_toc }

The ExampleBlock plugin helps technical writers prepare AsciiDoc content for DITA migration by identifying and fixing example blocks that violate DITA 1.3 compliance requirements.

{: .highlight }
**What it does**: Detects example blocks placed in invalid locations (within sections, lists, or other blocks) and either moves them to the main body or provides guidance on how to fix them manually.

{: .important }
**Why it matters**: DITA 1.3 requires `<example>` elements to appear only in the main body of topics, not nested within other structures.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

## Quick Start

### Basic Usage

```bash
# Check a single file
adt ExampleBlock -f your-document.adoc

# Process all .adoc files in current directory
adt ExampleBlock -r

# Process files in a specific directory
adt ExampleBlock -d /path/to/your/docs -r

# Enable verbose output to see what's being processed
adt ExampleBlock -f your-document.adoc -v
```

### Command Options

| Option | Description |
|--------|-------------|
| `-f FILE` | Process a specific AsciiDoc file |
| `-r` | Process all .adoc files recursively |
| `-d DIRECTORY` | Specify the directory to search (default: current directory) |
| `-v` | Enable verbose output |
| `-h` | Show help message |

## Understanding Example Block Issues

### What are Example Blocks?

In AsciiDoc, example blocks can be created in two ways:

1. **Delimited blocks** using `====`:
   ```asciidoc
   ====
   This is an example block
   ====
   ```

2. **Style blocks** using `[example]`:
   ```asciidoc
   [example]
   This is also an example block
   ```

### DITA 1.3 Compliance Requirements

{: .note-title }
> Valid vs Invalid Placements

**✅ Valid placement** - Example blocks in the main body:
```asciidoc
= Topic Title

This is the main body content.

====
This example block is properly placed in the main body.
====

== First Section

Section content here.
```

{: .warning }
**❌ Invalid placements** that the plugin will detect:

1. **Within sections**:
   ```asciidoc
   == Section Title
   
   ====
   This example block is inside a section (invalid)
   ====
   ```

2. **Within lists**:
   ```asciidoc
   * List item 1
   * List item 2
   +
   ====
   This example block is inside a list (invalid)
   ====
   ```

3. **Within other blocks**:
   ```asciidoc
   [NOTE]
   ====
   This example block is inside a note block (invalid)
   ====
   ```

## How the Plugin Works

### Detection Process

The plugin scans your AsciiDoc files and identifies:
- Example blocks using `====` delimiters
- Example blocks using `[example]` style markers
- The document structure (main body, sections, lists, other blocks)

### What Gets Ignored

{: .note }
The plugin is smart enough to ignore:
- Example blocks that are already in the main body ✅
- Example blocks inside comments (these are documentation)
- Example blocks inside admonitions (NOTE, TIP, WARNING, etc.)
- Example blocks inside code blocks or literal blocks

### Interactive Mode

When the plugin finds violations, it presents you with options:

```
Found example block in section at line 45:
====
Your example content here
====

Choose an action:
1 - Move to end of main body
2 - Move to beginning of main body  
3 - Move before first section
4 - See more choices
L - Leave as-is and insert comment
S - Skip this block
Q - Quit plugin

Press: 1-4 for placement, L/S/Q
```

#### Interactive Options Explained

| Option | Action | Description |
|--------|--------|-------------|
| **1-3** | Automatic placement | Most common scenarios (end of main body, beginning, before first section) |
| **4** | More choices | Show additional placement options |
| **L** | Leave with comment | Add explanatory comment and leave block in place |
| **S** | Skip | Skip this block and continue to next |
| **Q** | Quit | Exit the plugin entirely |

### Non-Interactive Mode

{: .note-title }
> Batch Processing & CI/CD

For batch processing or CI/CD pipelines, the plugin runs in non-interactive mode by default and adds helpful comments:

```asciidoc
//
// ADT ExampleBlock: Move this example block to the main body of the topic 
// (before the first section header) for DITA 1.3 compliance.
//
====
Your example content here
====
```

## Common Scenarios and Solutions

### Scenario 1: Example Block in Section

**Problem**: Example block appears after a section header.

**Solution**: Move the example block to the main body (before any section headers).

**Before**:
```asciidoc
= Topic Title

Introduction text.

== How to Use the Feature

To use this feature:

====
Example of the feature in action
====
```

**After**:
```asciidoc
= Topic Title

Introduction text.

====
Example of the feature in action
====

== How to Use the Feature

To use this feature:
```

### Scenario 2: Example Block in List

**Problem**: Example block is part of a list item.

**Solution**: Move the example block to the main body and reference it from the list.

**Before**:
```asciidoc
Follow these steps:

1. First step
2. Second step
+
====
Example for step 2
====
3. Third step
```

**After**:
```asciidoc
Follow these steps:

====
Example for step 2
====

1. First step
2. Second step (see example above)
3. Third step
```

### Scenario 3: Example Block in Another Block

**Problem**: Example block is nested inside another block type.

**Solution**: Extract the example block to the main body.

**Before**:
```asciidoc
[TIP]
====
Here's a helpful tip with an example:

====
Example code
====
====
```

**After**:
```asciidoc
====
Example code
====

[TIP]
====
Here's a helpful tip (see example above).
====
```

## Best Practices

### 1. Structure Your Documents for DITA

- Place example blocks in the main body, before any section headers
- Use cross-references to link from sections to examples
- Keep examples close to the content they illustrate

### 2. Use Descriptive Titles

```asciidoc
.Example: Configuration File Setup
====
[source,yaml]
----
server:
  port: 8080
----
====
```

### 3. Group Related Examples

```asciidoc
= API Documentation

.Example: Basic API Call
====
curl -X GET https://api.example.com/users
====

.Example: API Call with Authentication
====
curl -X GET -H "Authorization: Bearer token" https://api.example.com/users
====

== Authentication

Details about authentication...
```

### 4. Reference Examples from Content

```asciidoc
= Configuration Guide

.Example: Complete Configuration
====
[source,yaml]
----
# Configuration file example
server:
  port: 8080
  host: localhost
----
====

== Server Configuration

To configure your server, use the settings shown in the example above.
Set the port and host values according to your environment.
```

## Troubleshooting

### Common Issues

### Common Issues

{: .warning-title }
> Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| **False positives reported** | Complex nested structures or unusual formatting | Use "L" option to leave block and add comment, review manually |
| **Not all example blocks detected** | Non-standard formatting or custom block types | Review document manually for blocks using `====` or `[example]` |
| **Automatic placement doesn't work** | Complex document structure | Use interactive options to choose best placement |

### Getting Help

- Run `adt ExampleBlock --help` for command options
- Use the `-v` flag for verbose output during processing
- Check the plugin output for specific guidance on each violation

## Integration with Other Tools

### CI/CD Integration

The plugin works well in automated environments:

```bash
# In your CI/CD pipeline
adt ExampleBlock -r -d ./docs
```

The plugin will add comments to guide manual fixes rather than prompting for user input.

### Version Control

The plugin modifies files in place, so always:
1. Commit your changes before running the plugin
2. Review the plugin's changes before committing
3. Use version control to track what was modified

## Migration Strategy

### Phase 1: Assessment
```bash
# Run on all files to see the scope of issues
adt ExampleBlock -r -v
```

### Phase 2: Batch Processing
```bash
# Process files interactively to make decisions
adt ExampleBlock -r
```

### Phase 3: Review and Cleanup
1. Review all changes made by the plugin
2. Test your documents with DITA conversion tools
3. Make manual adjustments where needed

## Advanced Usage

### Custom Workflows

You can integrate the plugin into custom workflows:

```bash
#!/bin/bash
# Process each file individually for better control
for file in $(find ./docs -name "*.adoc"); do
    echo "Processing: $file"
    adt ExampleBlock -f "$file" -v
done
```

### Selective Processing

Focus on specific directories or file patterns:

```bash
# Process only tutorial files
adt ExampleBlock -d ./docs/tutorials -r

# Process a specific file type pattern
find ./docs -name "*-tutorial.adoc" -exec adt ExampleBlock -f {} \;
```

## Related Documentation

- [DITA 1.3 Specification](https://docs.oasis-open.org/dita/dita/v1.3/dita-v1.3-part0-overview.html)
- [AsciiDoc User Manual](https://asciidoc.org/userguide.html)
- [ADT User Guide]({% link index.md %}) (main documentation)

---

*This documentation is part of the AsciiDoc DITA Toolkit (ADT) project. For more information, visit the [project repository](https://github.com/rolfedh/asciidoc-dita-toolkit).*
