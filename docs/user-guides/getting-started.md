# Getting Started

This guide will help you get up and running with the AsciiDoc DITA Toolkit in just a few minutes.

## 📋 Prerequisites

Before you begin, make sure you have:
- Installed the toolkit (see [Installation Guide](installation.md))
- Some AsciiDoc (`.adoc`) files to work with
- Basic familiarity with command-line tools

## 🚀 Your First Run

### Step 1: Check Your Files

First, let's see what the toolkit can do with a simple dry run:

```bash
# Dry run to see what would be changed
asciidoc-dita-toolkit your-docs-folder/ --dry-run

# Or with containers
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest your-docs-folder/ --dry-run
```

This will analyze your files and show what changes would be made without actually modifying anything.

### Step 2: Run with Specific Plugins

The toolkit uses plugins to apply different transformations. Here's how to use them:

```bash
# Run only the ContentType plugin
asciidoc-dita-toolkit your-docs-folder/ --plugins ContentType

# Run multiple plugins
asciidoc-dita-toolkit your-docs-folder/ --plugins ContentType,EntityReference

# See available plugins
asciidoc-dita-toolkit --list-plugins
```

### Step 3: Apply Changes

When you're ready to apply changes:

```bash
# Apply all enabled plugins
asciidoc-dita-toolkit your-docs-folder/

# Apply with verbose output
asciidoc-dita-toolkit your-docs-folder/ --verbose
```

## 🔧 Common Use Cases

### Fixing Content Types

The `ContentType` plugin adds DITA content type attributes to your AsciiDoc files:

```bash
# Add content type attributes
asciidoc-dita-toolkit docs/ --plugins ContentType
```

Before:
```asciidoc
= Installing Docker

This procedure shows how to install Docker.
```

After:
```asciidoc
[cols="1"]
|===

a|*Content Type:* procedure

|===

= Installing Docker

This procedure shows how to install Docker.
```

### Converting HTML Entities

The `EntityReference` plugin converts HTML entities to AsciiDoc attributes:

```bash
# Convert HTML entities
asciidoc-dita-toolkit docs/ --plugins EntityReference
```

Before:
```asciidoc
Use the &amp; symbol to join commands.
```

After:
```asciidoc
Use the {amp} symbol to join commands.
```

### Batch Processing

Process multiple directories:

```bash
# Process multiple folders
asciidoc-dita-toolkit docs/ examples/ tutorials/

# Use wildcards
asciidoc-dita-toolkit */
```

## 📁 Working with Different File Structures

The toolkit works with various directory structures:

```bash
# Single file
asciidoc-dita-toolkit my-doc.adoc

# Specific directory
asciidoc-dita-toolkit docs/

# Multiple directories
asciidoc-dita-toolkit docs/ examples/

# Current directory
asciidoc-dita-toolkit .
```

## ⚙️ Configuration Options

### Environment Variables

Control behavior with environment variables:

```bash
# Non-interactive mode (use first config choice)
export ADT_CONFIG_CHOICE=1
asciidoc-dita-toolkit docs/

# Enable debug logging
export ADT_LOG_LEVEL=DEBUG
asciidoc-dita-toolkit docs/ --verbose
```

### Plugin Configuration

Some plugins support configuration:

```bash
# DirectoryConfig plugin (if enabled)
asciidoc-dita-toolkit docs/ --plugins DirectoryConfig
```

## 🔍 Understanding Output

The toolkit provides helpful output to understand what it's doing:

```bash
# Verbose output shows detailed information
asciidoc-dita-toolkit docs/ --verbose

# Dry run shows changes without applying them
asciidoc-dita-toolkit docs/ --dry-run
```

Example output:
```
Found 15 .adoc files in docs/
Processing with plugins: ContentType, EntityReference
✓ docs/installation.adoc - Added content type, converted 3 entities
✓ docs/getting-started.adoc - No changes needed
✗ docs/broken.adoc - Error: Invalid content structure
```

## 🎯 Best Practices

1. **Always use dry run first**: Test changes before applying them
   ```bash
   asciidoc-dita-toolkit docs/ --dry-run
   ```

2. **Version control**: Commit your files before running the toolkit
   ```bash
   git add . && git commit -m "Before AsciiDoc DITA Toolkit changes"
   ```

3. **Use specific plugins**: Only enable plugins you need
   ```bash
   asciidoc-dita-toolkit docs/ --plugins ContentType
   ```

4. **Test incrementally**: Start with a small subset of files
   ```bash
   asciidoc-dita-toolkit docs/getting-started.adoc --dry-run
   ```

## 🚀 Next Steps

Now that you've got the basics down:

- Check the [CLI Reference](cli-reference.md) for all available options
- Learn about [Container Usage](containers.md) for team workflows
- See [Troubleshooting](troubleshooting.md) if you run into issues
- Explore the [Plugin Reference](../reference/plugins.md) to understand what each plugin does

## 💡 Tips and Tricks

- Use `--dry-run` frequently to preview changes
- The toolkit preserves your original file formatting where possible
- Plugin order matters - some plugins work better when run in sequence
- Large repositories can be processed in batches for better performance

Happy documenting! 📝
