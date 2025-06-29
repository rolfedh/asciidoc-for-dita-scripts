# asciidoc-dita-toolkit

A toolkit for working with AsciiDoc and DITA.

## Package Structure

The package is organized as a Python package for PyPI distribution with the following structure:

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

## Installation

Install from PyPI:

```sh
python3 -m pip install asciidoc-dita-toolkit
```

## Usage

### Command Line Interface

The package provides a unified CLI command:

```sh
asciidoc-dita-toolkit --help
```

### List Available Plugins

```sh
asciidoc-dita-toolkit --list-plugins
```

### Run Plugins

```sh
# Fix HTML entity references in a specific file
asciidoc-dita-toolkit EntityReference -f path/to/file.adoc

# Add content type labels recursively
asciidoc-dita-toolkit ContentType -r

# Process all .adoc files in current directory
asciidoc-dita-toolkit EntityReference -r
```

### Plugin Options

Both plugins support common options:

- `-f FILE` or `--file FILE`: Process a specific file
- `-r` or `--recursive`: Process all .adoc files recursively
- `-d DIR` or `--directory DIR`: Specify root directory (default: current directory)

## Development

### Testing

Run the test suite:

```sh
make test
```

### Building and Publishing

Build the package:

```sh
make build
```

Publish to PyPI:

```sh
make publish
```

See the [Makefile](../Makefile) for all available development targets and the [CONTRIBUTING.md](CONTRIBUTING.md) guide for detailed development instructions.

---

For more details, see the [README.md](../README.md) and other documentation in the repository.