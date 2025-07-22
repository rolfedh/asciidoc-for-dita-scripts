---
layout: default
title: ValeFlagger
parent: Plugins
nav_order: 5
---

# ValeFlagger Plugin
{: .no_toc }

The ValeFlagger plugin integrates Vale linter to automatically check your AsciiDoc files for DITA compatibility issues and insert helpful flags directly in your source files.

{: .highlight }
**What it does**: Scans AsciiDoc files using the AsciiDocDITA ruleset and inserts comment flags above problematic lines with specific guidance on how to fix DITA compliance issues.

{: .important }
**Why it matters**: Ensures your AsciiDoc content follows DITA best practices for structure, terminology, and style before conversion, preventing common migration issues.

{: .note }
**New to ValeFlagger?** Check out the [5-minute Quick Start Guide](ValeFlagger-Quick-Start.md) for immediate setup.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Quick Start

### Zero-Configuration Usage

ValeFlagger is designed to work immediately without any setup:

```bash
# Check a single file (recommended for beginners)
adt ValeFlagger -f my-document.adoc

# Check all files in current directory
adt ValeFlagger -r

# Preview issues without modifying files
adt ValeFlagger -f my-document.adoc --dry-run
```

{: .note }
**Prerequisites**: Docker must be installed and running. ValeFlagger automatically downloads and configures the necessary DITA checking rules.

### Understanding the Output

When ValeFlagger finds an issue, it inserts a comment above the problematic line:

**Before:**
```asciidoc
= Getting Started With APIs
```

**After:**
```asciidoc
// ADT-FLAG [Headings.Capitalization]: Heading should use sentence-style capitalization.
= Getting Started With APIs
```

The flag format: `// ADT-FLAG [RuleName]: Helpful message explaining the issue`

---

## Common DITA Issues Detected

### Heading Capitalization

**Issue**: DITA prefers sentence-style capitalization for headings.

**ValeFlagger detects:**
```asciidoc
// ADT-FLAG [Headings.Capitalization]: Use sentence-style capitalization
= Getting Started With APIs  ❌
```

**Recommended fix:**
```asciidoc
= Getting started with APIs  ✅
```

### Terminology Consistency

**Issue**: Inconsistent terminology across documentation.

**ValeFlagger detects:**
```asciidoc
// ADT-FLAG [Terms.Use]: Use 'repository' instead of 'repo'
Clone the repo to your local machine.  ❌
```

**Recommended fix:**
```asciidoc
Clone the repository to your local machine.  ✅
```

### Content Structure

**Issue**: Missing or incorrectly structured content elements.

**ValeFlagger detects:**
```asciidoc
// ADT-FLAG [Structure.ShortDescription]: Consider adding a short description after the title
= API Overview

This section covers advanced topics...  ❌
```

**Recommended fix:**
```asciidoc
= API Overview

This guide explains how to use our REST API effectively.

This section covers advanced topics...  ✅
```

---

## Working with Flags

### Processing Workflow

1. **Review each flag**: Read the message to understand the issue
2. **Make the fix**: Update your content based on the guidance
3. **Remove the flag**: Delete the `// ADT-FLAG` comment after fixing
4. **Re-run ValeFlagger**: Verify the issue is resolved

### Flag Lifecycle Example

**Step 1 - Initial scan:**
```asciidoc
// ADT-FLAG [Terms.Use]: Use 'repository' instead of 'repo'
Clone the repo and install dependencies.
```

**Step 2 - Fix the content:**
```asciidoc
// ADT-FLAG [Terms.Use]: Use 'repository' instead of 'repo'
Clone the repository and install dependencies.
```

**Step 3 - Remove the flag:**
```asciidoc
Clone the repository and install dependencies.
```

**Step 4 - Verify:**
```bash
adt ValeFlagger -f my-file.adoc
# No new flags = issue resolved!
```

---

## Writer-Friendly Workflows

### Daily Writing Workflow

1. **Write your content** normally in AsciiDoc
2. **Run ValeFlagger** when you finish a section:
   ```bash
   adt ValeFlagger -f current-file.adoc
   ```
3. **Address flags** one by one
4. **Re-run to verify** fixes

### Team Review Workflow

1. **Before submitting for review:**
   ```bash
   adt ValeFlagger -r --dry-run > issues.txt
   ```
2. **Review the issues list** and fix major problems
3. **Run without dry-run** to insert flags for minor issues
4. **Submit for review** with flags intact for reviewer context

### Content Audit Workflow

1. **Scan entire documentation:**
   ```bash
   adt ValeFlagger -r
   ```
2. **Prioritize fixes** by severity and impact
3. **Work systematically** through each file
4. **Track progress** by monitoring flag count

---

## Advanced Configuration

### Custom Rules Configuration

Create a configuration file `valeflag-config.yaml`:

```yaml
vale:
  # Only check for critical issues
  enabled_rules:
    - "Headings.Capitalization"
    - "Terms.Use"
    - "Structure.ShortDescription"

  # Ignore certain rules that don't fit your style
  disabled_rules:
    - "Readability.TooWordy"

valeflag:
  # Customize flag appearance
  flag_format: "// REVIEW [{rule}]: {message}"
```

Use your custom configuration:
```bash
adt ValeFlagger -f my-file.adoc --config valeflag-config.yaml
```

### Available Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `vale.enabled_rules` | List of rules to enable | All rules |
| `vale.disabled_rules` | List of rules to disable | None |
| `vale.timeout_seconds` | Docker execution timeout | 300 seconds |
| `vale.docker_image` | Custom Docker image | Auto-generated |
| `valeflag.flag_format` | Custom flag format | `// ADT-FLAG [{rule}]: {message}` |

---

## Editor Integration

### VS Code Integration

ValeFlagger works excellently with VS Code for AsciiDoc editing:

1. **Install AsciiDoc extension** for syntax highlighting
2. **Use integrated terminal** to run ValeFlagger commands
3. **Set up tasks** for quick access

#### VS Code Tasks Setup

Create `.vscode/tasks.json` in your project root:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "ValeFlagger: Check Current File",
            "type": "shell",
            "command": "adt",
            "args": ["ValeFlagger", "-f", "${file}"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "panel": "new"
            }
        },
        {
            "label": "ValeFlagger: Preview Issues",
            "type": "shell",
            "command": "adt",
            "args": ["ValeFlagger", "-f", "${file}", "--dry-run"],
            "group": "test"
        }
    ]
}
```

**Access tasks via:**
- Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
- Type "Tasks: Run Task"
- Select your ValeFlagger task

### Other Editors

Most text editors work well with ValeFlagger's comment-based approach:
- **Vim/Neovim**: Comments are clearly visible and easy to navigate
- **Emacs**: Org-mode users will find the workflow familiar
- **Sublime Text**: Syntax highlighting makes flags stand out
- **IntelliJ IDEA**: Built-in AsciiDoc support works with flags

---

## Troubleshooting

### Common Issues

#### "Docker not found" Error

**Problem**: ValeFlagger requires Docker to run the Vale linter.

**Solution**: Install Docker Desktop and ensure it's running before using ValeFlagger.

```bash
# Test Docker installation
docker --version
# Should show version info without errors
```

#### "No issues found" but Content Seems Wrong

**Possible causes:**
1. ValeFlagger only checks configured rules
2. Some issues might not be covered by current ruleset
3. File might not be in AsciiDoc format

**Solution**: Run with verbose output:
```bash
adt ValeFlagger -f my-file.adoc -v
```

#### Too Many Flags on Existing Content

**Strategy for large existing documents:**

1. **Start with critical issues:**
   ```bash
   adt ValeFlagger -f doc.adoc --enable-rules "Headings.Capitalization,Terms.Use"
   ```

2. **Fix incrementally** - don't try to fix everything at once

3. **Focus on new content** - apply full checking to new sections

#### Flags Not Appearing

**Check:**
1. File is saved before running ValeFlagger
2. Running command from correct directory
3. File has `.adoc` extension
4. Docker is running and accessible

---

## Best Practices

### Preventive Writing

- **Learn common patterns** from flags you see repeatedly
- **Internalize terminology** to avoid consistency issues
- **Follow heading conventions** from the start

### Iterative Improvement

- **Don't aim for perfection** on first draft
- **Use dry-run mode** to assess scope before making changes
- **Fix systematically** rather than randomly

### Team Collaboration

- **Share configuration files** to ensure consistent checking
- **Document team-specific rules** and exceptions
- **Use flags as learning tools** for new team members

### Content Maintenance

- **Run periodic audits** on existing content
- **Update configurations** as style guides evolve
- **Track improvements** over time

---

## Integration with Documentation Workflows

### Git Workflows

```bash
# Before committing
adt ValeFlagger -r --dry-run
# Review and fix critical issues

# Add flags for team review
adt ValeFlagger -r
git add .
git commit -m "Add ValeFlagger flags for review"
```

### CI/CD Integration

ValeFlagger can be integrated into automated pipelines to catch issues early:

```bash
# In your CI script
adt ValeFlagger -r --dry-run > vale-issues.txt
if [ -s vale-issues.txt ]; then
    echo "DITA compliance issues found:"
    cat vale-issues.txt
    exit 1
fi
```

---

## Command Reference

### Essential Commands

| Command | Purpose |
|---------|---------|
| `adt ValeFlagger -f file.adoc` | Check single file |
| `adt ValeFlagger -r` | Check all files recursively |
| `adt ValeFlagger -f file.adoc --dry-run` | Preview issues only |
| `adt ValeFlagger -f file.adoc -v` | Verbose output |
| `adt ValeFlagger -h` | Get help |

### Flag Actions

| Action | Description |
|--------|-------------|
| Read flag message | Understand the issue |
| Fix the content | Make the suggested change |
| Delete the flag | Remove the comment line |
| Re-run ValeFlagger | Verify the fix |

---

## Configuration Examples

### Basic Configuration (`valeflag-basic.yaml`)

```yaml
# Basic ValeFlagger Configuration for Technical Writers
vale:
  enabled_rules:
    - "Headings.Capitalization"
    - "Terms.Use"
    - "Structure.ShortDescription"

  disabled_rules:
    - "Readability.TooWordy"
    - "Style.Contractions"

  timeout_seconds: 300

valeflag:
  flag_format: "// WRITER NOTE [{rule}]: {message}"
  backup_files: false
```

### Advanced Team Configuration (`valeflag-advanced.yaml`)

```yaml
# Advanced ValeFlagger Configuration for Technical Writing Teams
vale:
  enabled_rules:
    # Structure and organization
    - "Structure.ShortDescription"
    - "Structure.SectionOrder"
    - "Structure.ListFormat"

    # Content quality
    - "Headings.Capitalization"
    - "Headings.Length"
    - "Terms.Use"
    - "Terms.Spelling"

    # DITA-specific requirements
    - "DITA.CrossReferences"
    - "DITA.Metadata"
    - "DITA.Attributes"

  disabled_rules:
    - "Readability.TooWordy"
    - "Style.Contractions"

  timeout_seconds: 600

valeflag:
  flag_format: "// REVIEW [{rule}]: {message}"
  backup_files: true
```

---

{: .highlight }
For additional help, run `adt ValeFlagger -h` for command-line options or consult the [ADT documentation]({{ site.baseurl }}/) for general toolkit usage.
