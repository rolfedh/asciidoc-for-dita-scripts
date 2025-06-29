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
