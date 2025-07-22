# ValeFlagger Quick Start Guide

## Installation

1. **Build the Docker container:**
   ```bash
   cd docker/vale-adv
   chmod +x build.sh
   ./build.sh
   ```

2. **Install Python dependencies:**
   ```bash
   pip install pyyaml
   ```

3. **Make the wrapper executable:**
   ```bash
   chmod +x bin/valeflag
   ```

## Basic Usage

### Check current directory
```bash
./bin/valeflag
```

### Check specific directory
```bash
./bin/valeflag --path ./docs
```

### Dry run (see issues without modifying files)
```bash
./bin/valeflag --dry-run
```

### Enable specific rules
```bash
./bin/valeflag --enable-rules "Headings.Capitalization,Terms.Use"
```

### Use configuration file
```bash
./bin/valeflag --config valeflag-config.yaml
```

## Understanding Flags

Flags are inserted as comments above violations:
```adoc
// ADT-FLAG [Headings.Capitalization]: Heading should use sentence-style capitalization.
= this heading needs capitalization
```

## Removing Flags

To remove all flags from files:
```bash
find . -name "*.adoc" -exec sed -i '/^\/\/ ADT-FLAG/d' {} \;
```

## Available Rules

Run Vale directly to see all available rules:
```bash
docker run --rm asciidoc-dita-toolkit/vale-adv ls-config
```

Common rules:
- `Headings.Capitalization` - Enforce sentence-style capitalization
- `Terms.Use` - Enforce preferred terminology
- `Links.External` - Check external link formatting
- `Spelling.Terms` - Check technical term spelling
