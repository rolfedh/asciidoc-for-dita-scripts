# asciidoc-dita-toolkit

A toolkit for working with AsciiDoc and DITA.

## Package Structure

The code is now organized as a Python package for PyPI distribution:

```
asciidoc-dita-toolkit/
    asciidoc_dita_toolkit/
        __init__.py
        asciidoc_toolkit.py
        file_utils.py
        plugins/
            __init__.py
            ContentType.py
            EntityReference.py
    ...
```

## Installation (after PyPI release)

```sh
python3 -m pip install asciidoc-dita-toolkit
```

## Usage

Import modules in your Python code:

```python
from asciidoc_dita_toolkit import asciidoc_toolkit, file_utils
from asciidoc_dita_toolkit.plugins import ContentType, EntityReference
```

## Development & Packaging

To build and publish to PyPI:

1. Ensure you have `build` and `twine` installed:
   ```sh
   python3 -m pip install --upgrade build twine
   ```
2. Build the package:
   ```sh
   python3 -m build
   ```
3. Upload to PyPI:
   ```sh
   python3 -m twine upload dist/*
   ```

See `pyproject.toml` for project metadata and dependencies.

---

For more details, see the source files and documentation in the `docs/` directory.