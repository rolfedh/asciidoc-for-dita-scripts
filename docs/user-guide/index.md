---
layout: default
title: Home
nav_order: 1
---

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
- **DirectoryConfig** - Manages directory-specific configuration (documentation coming soon)
- **MetaDataExtractor** - Extracts and formats metadata (documentation coming soon)

## Quick Start

1. **Install the toolkit:**
   ```bash
   pip install asciidoc-dita-toolkit
   ```

2. **Run analysis on your content:**
   ```bash
   adt analyze /path/to/your/asciidoc/files
   ```

3. **Apply fixes automatically:**
   ```bash
   adt fix /path/to/your/asciidoc/files
   ```

## Plugin Documentation

Each plugin includes detailed documentation covering:

- **Purpose and scope** - What issues the plugin addresses
- **Detection logic** - How problems are identified
- **Fix implementation** - How corrections are applied
- **Configuration options** - Available customization settings
- **Usage examples** - Real-world scenarios

## Support

For issues, feature requests, or contributions, visit our [GitHub repository](https://github.com/rolfedh/asciidoc-dita-toolkit).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/LICENSE) file for details.
