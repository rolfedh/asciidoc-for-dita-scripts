# AsciiDoc DITA Tool

**👉 Complete documentation and tutorials:** https://rolfedh.github.io/asciidoc-dita-toolkit/
## 📋 Prerequisites

### Option 1: Python Package
- **Python 3.8+** - Required for the package installation (we recommend upgrading to Python 3.8+)
- **pip** - Python package manager
- *Note: If you're using Python 3.7, please use the container option below*

### Option 2: Container
- **Docker** or **Podman** - Container runtime
- **curl** - For downloading the wrapper script
- *Recommended for users on Python 3.7 or those who prefer containerized tools*

## 🚀 Quick Start

[![PyPI version](https://img.shields.io/pypi/v/asciidoc-dita-toolkit.svg)](https://pypi.org/project/asciidoc-dita-toolkit/)
[![Container](https://img.shields.io/badge/container-ghcr.io-blue?logo=docker)](https://github.com/rolfedh/asciidoc-dita-toolkit/pkgs/container/asciidoc-dita-toolkit-prod)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
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

## 🚀 Quick Start

### Option 1: Python Package (Recommended)

```sh
# Install
pip install asciidoc-dita-toolkit

# Use
adt --help
adt --list-plugins
```

### Option 2: Container

```sh
# One-time setup: Download and install adt wrapper
curl -sSL https://raw.githubusercontent.com/rolfedh/asciidoc-dita-toolkit/main/scripts/adt-docker -o /usr/local/bin/adt && chmod +x /usr/local/bin/adt

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

## 🛠️ Troubleshooting

If you encounter issues like "Failed to load module" or "No module named 'modules'" errors, see our [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for solutions.

Common fixes:
- Remove conflicting packages: `pip uninstall adt-core`
- Clear package cache: `pip cache purge`
- Reinstall: `pip install --upgrade asciidoc-dita-toolkit`

## 🤝 Contributing

- **Documentation**: https://rolfedh.github.io/asciidoc-dita-toolkit/
- **Issues**: https://github.com/rolfedh/asciidoc-dita-toolkit/issues
- **Contributing Guide**: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
