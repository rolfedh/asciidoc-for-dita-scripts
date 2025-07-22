# ValeFlagger Quick Start Guide

Get DITA-compliant AsciiDoc checking in 5 minutes.

## What is ValeFlagger?

ValeFlagger automatically checks your AsciiDoc files for DITA compatibility issues and inserts helpful comments to guide improvements.

## Prerequisites

- Docker installed and running
- AsciiDoc DITA Toolkit installed

## 5-Minute Setup

### 1. Check Docker is Running

```bash
docker --version
# Should show version info without errors
```

### 2. Test ValeFlagger

```bash
# Create a test file
echo "= Getting Started With APIs" > test.adoc

# Run ValeFlagger
adt ValeFlagger -f test.adoc

# Check the result
cat test.adoc
```

You should see something like:
```asciidoc
// ADT-FLAG [Headings.Capitalization]: Heading should use sentence-style capitalization.
= Getting Started With APIs
```

### 3. Fix the Issue

Edit your file:
```asciidoc
= Getting started with APIs
```

### 4. Verify the Fix

```bash
# Remove the flag comment and re-run
adt ValeFlagger -f test.adoc
# No new flags = issue resolved!
```

## Daily Usage

```bash
# Check single file while writing
adt ValeFlagger -f my-document.adoc

# Preview issues without changes
adt ValeFlagger -f my-document.adoc --dry-run

# Check all files in project
adt ValeFlagger -r
```

## Next Steps

- Read the comprehensive [ValeFlagger Guide](ValeFlagger.md)
- Set up [VS Code integration](ValeFlagger.md#vs-code-integration)
- Customize rules with [configuration files](ValeFlagger.md#advanced-configuration)

---

**Need help?** Run `adt ValeFlagger -h` or check the [full documentation](ValeFlagger.md).
