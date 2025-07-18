# AsciiDoc DITA Toolkit - User Guide

Welcome to the AsciiDoc DITA Toolkit (ADT) user guide. This documentation is designed for technical writers who need to prepare AsciiDoc content for migration to DITA format.

## Overview

The AsciiDoc DITA Toolkit helps identify and fix common issues that prevent successful AsciiDoc-to-DITA conversion. Each plugin targets specific compliance requirements defined in the DITA 1.3 specification.

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

## Getting Started

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/rolfedh/asciidoc-dita-toolkit.git
   cd asciidoc-dita-toolkit
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

### Basic Usage

List all available plugins:
```bash
adt --help
```

Run a specific plugin:
```bash
adt ExampleBlock -f your-document.adoc
```

## General Workflow

1. **Assess your content**: Run analysis plugins to understand the scope of issues
2. **Fix validation issues**: Use content validation plugins to address DITA compliance problems
3. **Migrate content**: Use migration plugins for structural changes
4. **Verify results**: Test your content with DITA conversion tools

## Common Patterns

### Single File Processing
```bash
adt PluginName -f document.adoc
```

### Batch Processing
```bash
adt PluginName -r -d /path/to/docs
```

### Verbose Output
```bash
adt PluginName -f document.adoc -v
```

## Best Practices

1. **Use version control**: Always commit your changes before running ADT plugins
2. **Process incrementally**: Start with one plugin at a time to understand changes
3. **Review changes**: Examine plugin output before proceeding to the next step
4. **Test conversion**: Regularly test your content with DITA conversion tools

## Support

- [GitHub Issues](https://github.com/rolfedh/asciidoc-dita-toolkit/issues) - Report bugs or request features
- [Project Repository](https://github.com/rolfedh/asciidoc-dita-toolkit) - Source code and development information

---

*This documentation is part of the AsciiDoc DITA Toolkit (ADT) project.*
