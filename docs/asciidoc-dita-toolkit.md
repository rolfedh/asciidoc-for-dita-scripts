# asciidoc-dita-toolkit

Technical documentation for the AsciiDoc DITA Toolkit package.

## Package Structure

The package is organized as a Python package for PyPI distribution:

```plaintext
asciidoc-dita-toolkit/
    asciidoc_dita_toolkit/
        __init__.py
        asciidoc_dita/
            __init__.py
            toolkit.py          # Main CLI entry point
            file_utils.py       # Shared file utilities
            plugins/
                __init__.py
                ContentType.py      # Content type labeling plugin
                EntityReference.py  # HTML entity conversion plugin
        beta_testing_files/     # Test files and examples (included in PyPI package)
            EntityReference/
                sample.adoc         # Sample file with entity references
                expected.adoc       # Expected output after transformation
                ...
            ContentType/
                sample_assembly.adoc
                sample_module.adoc
                ...
    find_beta_files.py          # Helper script (available as console command)
```

## Beta Testing Files

The package includes comprehensive test files and examples that are automatically included in both PyPI packages and Docker images.

### Accessing Test Files

**Find location of test files:**
```sh
# Using the helper script (available after installation)
find-beta-files

# Manual location (PyPI installation)
python -c "import asciidoc_dita_toolkit; import os; print(os.path.join(os.path.dirname(asciidoc_dita_toolkit.__file__), 'beta_testing_files'))"
```

**In Docker containers:**
```sh
# Test files are located at:
/usr/src/app/asciidoc_dita_toolkit/beta_testing_files/

# Use the helper script
docker run --rm rolfedh/asciidoc-dita-toolkit-prod:latest find-beta-files
```

### Test File Contents

Each plugin directory contains:
- **Sample files**: Real-world examples with common issues
- **Expected outputs**: Correct transformations for validation
- **Edge cases**: Complex scenarios for thorough testing

**Example test workflow:**
```sh
# Get test files location
BETA_DIR=$(find-beta-files)

# Copy EntityReference test files to work on
cp -r "$BETA_DIR/EntityReference" ./test-work

# Run the plugin on test files
asciidoc-dita-toolkit EntityReference -f test-work/sample.adoc

# Compare with expected output
diff test-work/sample.adoc test-work/expected.adoc
```

## Available Plugins

### EntityReference

Replaces unsupported HTML character entity references with AsciiDoc attribute references.

**Common entities handled:**

- `&hellip;` → `{hellip}`
- `&mdash;` → `{mdash}`
- `&ndash;` → `{ndash}`
- `&copy;` → `{copy}`

### ContentType

Adds `:_mod-docs-content-type:` labels to files where missing, based on filename patterns.

**Content type detection:**

- Files ending with `_assembly.adoc` → `assembly`
- Files ending with `_module.adoc` → `concept`, `procedure`, or `reference`
- Default → `concept`

---

For installation instructions and usage examples, see the main [README.md](../README.md).  
For development setup and commands, see [CONTRIBUTING.md](CONTRIBUTING.md).
