---
layout: default
title: Home
nav_order: 1
---

# AsciiDoc DITA Toolkit - User Guide

Welcome to the AsciiDoc DITA Toolkit (ADT) user guide. This documentation is designed for **technical writers** who need to prepare AsciiDoc content for migration to DITA format.

> **For ADT Developers & Plugin Developers**: Development documentation, contribution guidelines, and architecture details are available at [https://rolfedh.github.io/asciidoc-dita-toolkit/README.md](https://rolfedh.github.io/asciidoc-dita-toolkit/README.md)

## Overview

The AsciiDoc DITA Toolkit helps identify and fix common issues that prevent successful AsciiDoc-to-DITA conversion. Each plugin targets specific compliance requirements defined in the DITA 1.3 specification.

**What ADT does for you:**
- Automatically detects DITA compliance violations in your AsciiDoc files
- Provides interactive fixes for complex issues
- Applies automatic corrections where safe to do so
- Generates detailed reports of changes made to your content

## Available Plugins

### Content Validation Plugins

- **[ExampleBlock](plugins/ExampleBlock.md)** - Ensures example blocks are placed in valid locations according to DITA 1.3 requirements
- **ContentType** - Validates and fixes content type declarations (documentation coming soon)
- **CrossReference** - Fixes cross-reference formats for DITA compatibility (documentation coming soon)
- **EntityReference** - Converts HTML entities to AsciiDoc attributes (documentation coming soon)

### Analysis and Migration Plugins

- **ContextAnalyzer** - Analyzes document context usage (documentation coming soon)
- **ContextMigrator** - Migrates context-suffixed IDs (documentation coming soon)
- **DirectoryConfig** - Manages directory-level configuration (documentation coming soon)
- **MetaDataExtractor** - Extracts and formats metadata (documentation coming soon)

## Getting Started

### Installation

Install ADT using pip:
```bash
pip install asciidoc-dita-toolkit
```

### Quick Start

1. **Check what plugins are available:**
   ```bash
   adt --help
   ```

2. **Run a plugin on a single file:**
   ```bash
   adt ExampleBlock -f your-document.adoc
   ```

3. **Process all files in a directory:**
   ```bash
   adt ExampleBlock -r -d /path/to/your/docs
   ```

## Recommended Workflow

Follow this workflow to prepare your AsciiDoc content for DITA migration:

1. **Backup your content** - Always commit to version control before running ADT
2. **Start with analysis** - Run plugins to understand the scope of issues
3. **Process systematically** - Use one plugin at a time to understand changes
4. **Review each change** - Examine plugin output before proceeding
5. **Test conversion** - Validate your content with DITA conversion tools

## Common Usage Patterns

### Processing Individual Files
```bash
# Basic usage
adt ExampleBlock -f document.adoc

# With verbose output to see what's happening
adt ExampleBlock -f document.adoc -v

# Interactive mode for manual decision-making
adt ExampleBlock -f document.adoc --interactive
```

### Batch Processing
```bash
# Process all .adoc files in current directory
adt ExampleBlock -r -d .

# Process specific directory
adt ExampleBlock -r -d /path/to/your/documentation

# Combine with verbose output
adt ExampleBlock -r -d /path/to/docs -v
```

### Configuration-Driven Processing

Create `.adt-modules.json` in your project root to configure plugin behavior:

```json
{
  "version": "1.0",
  "modules": [
    {
      "name": "ExampleBlock", 
      "required": false,
      "config": {
        "interactive": false,
        "verbose": true
      }
    }
  ]
}
```

Then run ADT against your configured project:
```bash
adt ExampleBlock -r -d .
```

## Plugin Documentation

Each plugin includes detailed documentation covering:

- **Purpose and scope** - What issues the plugin addresses
- **Detection logic** - How problems are identified
- **Fix implementation** - How corrections are applied
- **Configuration options** - Available customization settings
- **Usage examples** - Real-world scenarios

## Best Practices for Technical Writers

### Before You Start
1. **Commit to version control** - Always save your work before running ADT plugins
2. **Create a test branch** - Work on a separate branch to easily revert if needed
3. **Understand your content** - Review the DITA compliance issues specific to your documentation

### During Processing
1. **Start small** - Test plugins on a few files before processing entire directories
2. **Use interactive mode** - Let ADT ask for your input when automatic fixes aren't clear
3. **Review each change** - Don't blindly accept all modifications
4. **Process incrementally** - Use one plugin at a time to understand the impact

### After Processing
1. **Test thoroughly** - Verify your content still renders correctly
2. **Check DITA conversion** - Test with your DITA conversion tools
3. **Document decisions** - Keep notes on any manual choices you made
4. **Share learnings** - Help your team understand the changes needed

## Understanding Plugin Output

ADT plugins provide clear feedback about what they find and fix:

- **✅ No issues found** - Your content already complies with DITA requirements
- **🔧 Auto-fixed** - Issues were automatically corrected
- **❓ Manual review needed** - Interactive prompts will guide you through decisions
- **💬 Comments added** - Explanatory comments inserted where fixes aren't possible

## Troubleshooting Common Issues

### Plugin Not Working as Expected
- Use the `-v` flag to see detailed output
- Check that your `.adt-modules.json` configuration is valid
- Verify you're using the correct plugin name with `adt --help`

### Files Not Being Processed
- Ensure file paths are correct and files are readable
- Check that files have the `.adoc` extension
- Verify directory permissions for batch processing

### Conversion Still Failing After ADT
- Run additional plugins - some issues require multiple fixes
- Check for custom AsciiDoc syntax not covered by ADT
- Consult your DITA conversion tool's documentation for specific requirements

## Support and Community

### Getting Help
- **Documentation**: Each plugin has detailed documentation with examples
- **Issues**: Report problems at [GitHub Issues](https://github.com/rolfedh/asciidoc-dita-toolkit/issues)
- **Questions**: Use GitHub Discussions for usage questions and community support

### Contributing Feedback
As a technical writer using ADT, your feedback is valuable:
- Report unclear plugin behavior or unexpected results
- Suggest improvements to interactive prompts and user guidance
- Share examples of complex AsciiDoc patterns that need support

---

*This user guide focuses on using ADT to prepare content for DITA migration. For development and contribution information, visit the [project documentation](https://rolfedh.github.io/asciidoc-dita-toolkit/README.md).*
