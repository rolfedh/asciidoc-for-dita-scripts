# AsciiDoc DITA Toolkit

[![PyPI version](https://img.shields.io/pypi/v/asciidoc-dita-toolkit.svg)](https://pypi.org/project/asciidoc-dita-toolkit/)
[![Container](https://img.shields.io/badge/container-ghcr.io-blue?logo=docker)](https://github.com/rolfedh/asciidoc-dita-toolkit/pkgs/container/asciidoc-dita-toolkit-prod)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A command-line toolkit for technical writers to review and fix AsciiDoc content for DITA-based publishing workflows.

##  What is this?

The AsciiDoc DITA Toolkit helps you:

- **Find and fix** common issues in `.adoc` files before publishing
- **Apply automated checks** and transformations using a plugin system  
- **Ensure consistency** across large documentation projects
- **Integrate** with your existing documentation workflow

## � Documentation

**👉 Complete documentation and tutorials:** https://rolfedh.github.io/asciidoc-dita-toolkit/

## � Quick Start

### Option 1: Container (Recommended)

```sh
# Run on current directory
docker run --rm -v $(pwd):/workspace ghcr.io/rolfedh/asciidoc-dita-toolkit-prod:latest --help

# List available plugins
docker run --rm -v $(pwd):/workspace ghcr.io/rolfedh/asciidoc-dita-toolkit-prod:latest --list-plugins
```

### Option 2: Python Package

```sh
# Install
pip install asciidoc-dita-toolkit

# Use
adt --help
adt --list-plugins
```

## � Basic Usage

```sh
# Fix HTML entity references
adt EntityReference -r

# Add content type labels  
adt ContentType -r
```

## 🤝 Contributing

- **Documentation**: https://rolfedh.github.io/asciidoc-dita-toolkit/
- **Issues**: https://github.com/rolfedh/asciidoc-dita-toolkit/issues
- **Contributing Guide**: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
