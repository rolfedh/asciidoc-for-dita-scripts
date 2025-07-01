# Beta Testing Guide

This guide explains how to access and use the beta-testing files included with the AsciiDoc DITA Toolkit for both PyPI and Docker installations.

## Overview

The toolkit includes comprehensive beta-testing files with real-world examples to help you:

- **Understand plugin behavior** with concrete examples
- **Test plugin functionality** before using on your own files
- **Validate transformations** by comparing inputs and expected outputs
- **Learn best practices** from curated examples

## Accessing Beta Testing Files

### PyPI Installation

**Quick access using the helper script:**
```sh
# Find the location of beta testing files
find-beta-files

# Store location in a variable for easy access
BETA_DIR=$(find-beta-files)
echo "Beta testing files are located at: $BETA_DIR"
```

**Manual location:**
```sh
# Using Python to find the installation directory
python -c "import asciidoc_dita_toolkit; import os; print(os.path.join(os.path.dirname(asciidoc_dita_toolkit.__file__), 'beta_testing_files'))"
```

### Docker Installation

**Find files in container:**
```sh
# Production container
docker run --rm rolfedh/asciidoc-dita-toolkit-prod:latest find-beta-files

# Development container
docker run --rm rolfedh/asciidoc-dita-toolkit:latest find-beta-files
```

**Copy files from container to host:**
```sh
# Copy all beta testing files to current directory
docker run --rm -v $(pwd):/output rolfedh/asciidoc-dita-toolkit-prod:latest sh -c 'cp -r $(find-beta-files)/* /output/'

# Copy specific plugin files
docker run --rm -v $(pwd):/output rolfedh/asciidoc-dita-toolkit-prod:latest sh -c 'cp -r $(find-beta-files)/EntityReference /output/'
```

**Interactive exploration:**
```sh
# Start interactive shell with development container
docker run --rm -it -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:latest /bin/bash

# Inside container, explore test files
find-beta-files
cd $(find-beta-files)
ls -la
```

## Working with Test Files

### File Structure

Each plugin has its own test directory containing:

```
beta_testing_files/
├── EntityReference/
│   ├── sample.adoc              # Input file with entity references
│   ├── expected.adoc            # Expected output after transformation
│   ├── complex_example.adoc     # More complex scenarios
│   └── edge_cases.adoc          # Edge cases and unusual patterns
├── ContentType/
│   ├── sample_assembly.adoc     # Assembly content example
│   ├── sample_module.adoc       # Module content example
│   └── expected_outputs/        # Directory with expected results
└── README.md                    # Overview of test files
```

### Testing Workflow

#### 1. Set up test workspace

```sh
# Create a test directory
mkdir test-workspace
cd test-workspace

# Copy test files to work with
BETA_DIR=$(find-beta-files)
cp -r "$BETA_DIR"/* .

# Or copy specific plugin tests
cp -r "$BETA_DIR"/EntityReference ./entity-test
```

#### 2. Run plugins on test data

```sh
# Test EntityReference plugin
asciidoc-dita-toolkit EntityReference -f EntityReference/sample.adoc

# Test ContentType plugin
asciidoc-dita-toolkit ContentType -f ContentType/sample_module.adoc

# Process all test files recursively
asciidoc-dita-toolkit EntityReference -r
```

#### 3. Validate results

```sh
# Compare transformed file with expected output
diff EntityReference/sample.adoc EntityReference/expected.adoc

# Use a visual diff tool for better comparison
code --diff EntityReference/sample.adoc EntityReference/expected.adoc
```

### Container Testing Examples

#### Quick test in container

```sh
# Run plugin on test files without copying to host
docker run --rm rolfedh/asciidoc-dita-toolkit-prod:latest sh -c '
  BETA_DIR=$(find-beta-files)
  asciidoc-dita-toolkit EntityReference -f "$BETA_DIR/EntityReference/sample.adoc"
'
```

#### Test with your own files

```sh
# Mount your files and use test files for reference
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest sh -c '
  # Copy test files to workspace for reference
  cp -r $(find-beta-files)/* /workspace/
  
  # Run plugin on your files
  asciidoc-dita-toolkit EntityReference -f /workspace/your-file.adoc
'
```

#### Development and experimentation

```sh
# Start development container with interactive shell
docker run --rm -it -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:latest /bin/bash

# Inside container:
BETA_DIR=$(find-beta-files)
cd "$BETA_DIR"

# Explore and test
ls -la EntityReference/
cat EntityReference/sample.adoc
asciidoc-dita-toolkit EntityReference -f EntityReference/sample.adoc
```

## Understanding Test Files

### EntityReference Plugin Tests

**sample.adoc** - Contains common HTML entity references:
```asciidoc
= Sample Document

This document contains HTML entities like &hellip; and &mdash; that need conversion.

Use &copy; for copyright and &ndash; for ranges like pages 1&ndash;10.
```

**expected.adoc** - Shows correct AsciiDoc attribute references:
```asciidoc
= Sample Document

This document contains HTML entities like {hellip} and {mdash} that need conversion.

Use {copy} for copyright and {ndash} for ranges like pages 1{ndash}10.
```

### ContentType Plugin Tests

**sample_assembly.adoc** - Assembly file without content type:
```asciidoc
= Managing User Accounts
:doctype: book

This assembly covers user account management.

include::user-creation_module.adoc[]
```

**After transformation** - Adds appropriate content type:
```asciidoc
:_mod-docs-content-type: ASSEMBLY

= Managing User Accounts
:doctype: book

This assembly covers user account management.

include::user-creation_module.adoc[]
```

## Troubleshooting

### File Not Found Errors

```sh
# Verify installation includes beta testing files
find-beta-files

# If command not found, ensure proper installation
pip install --upgrade asciidoc-dita-toolkit

# For development installations
pip install -e .
```

### Container Access Issues

```sh
# Verify container has access to test files
docker run --rm rolfedh/asciidoc-dita-toolkit-prod:latest find-beta-files

# Check if files exist in container
docker run --rm rolfedh/asciidoc-dita-toolkit-prod:latest ls -la /usr/src/app/asciidoc_dita_toolkit/beta_testing_files/
```

### Permission Issues

```sh
# When copying from container, ensure write permissions
docker run --rm -v $(pwd):/output rolfedh/asciidoc-dita-toolkit-prod:latest sh -c '
  cp -r $(find-beta-files)/* /output/ && 
  chmod -R 644 /output/*
'
```

## Integration with CI/CD

### Testing in CI Pipelines

```yaml
# Example GitHub Actions workflow
- name: Test with beta files
  run: |
    pip install asciidoc-dita-toolkit
    BETA_DIR=$(find-beta-files)
    cp -r "$BETA_DIR"/* ./test/
    asciidoc-dita-toolkit EntityReference -r test/
```

### Docker in CI

```yaml
- name: Test with Docker
  run: |
    docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest sh -c '
      cp -r $(find-beta-files)/* /workspace/test/
      asciidoc-dita-toolkit EntityReference -r /workspace/test/
    '
```

## Contributing Test Files

If you have additional test cases or examples that would benefit other users:

1. Add your test files to the appropriate plugin directory in `asciidoc_dita_toolkit/beta_testing_files/`
2. Include both input and expected output files
3. Document any special scenarios in comments
4. Submit a pull request with your additions

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details on the contribution process.
