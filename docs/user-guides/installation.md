# Installation Guide

The AsciiDoc DITA Toolkit can be installed using several methods. Choose the one that best fits your workflow.

## 📦 Installation Options

### Option 1: Container (Recommended)

Use Docker containers if you prefer not to install Python dependencies locally, or need consistent environments across teams:

```bash
# Production use (smaller, optimized)
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest --help

# Development use (includes dev tools)
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:latest --help

# GitHub Container Registry (alternative)
docker run --rm -v $(pwd):/workspace ghcr.io/rolfedh/asciidoc-dita-toolkit:latest --help
```

**Benefits of container approach:**
- No need to install Python or manage dependencies
- Consistent environment across different systems
- Easy to use in CI/CD pipelines
- Automatic cleanup after each run

For detailed container usage, see the [Container Usage Guide](containers.md).

### Option 2: PyPI (Python Package)

Install using pip if you have Python 3.7+ installed:

```bash
# Install from PyPI
pip install asciidoc-dita-toolkit

# Verify installation
asciidoc-dita-toolkit --help
```

### Option 3: Development Installation

For contributors and developers:

```bash
# Clone the repository
git clone https://github.com/rolfedh/asciidoc-dita-toolkit.git
cd asciidoc-dita-toolkit

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

## ✅ Verify Installation

After installation, verify everything is working:

```bash
# Check version
asciidoc-dita-toolkit --version

# Show help
asciidoc-dita-toolkit --help

# Run on test files (if available)
asciidoc-dita-toolkit test_files/ --dry-run
```

## 🔧 System Requirements

- **Python**: 3.7 or higher (for PyPI installation)
- **Docker**: Latest version (for container installation)  
- **Operating System**: Linux, macOS, Windows
- **Memory**: 512MB RAM minimum
- **Storage**: 50MB available space

## 🚀 Next Steps

Once installed, continue with the [Getting Started Guide](getting-started.md) to learn how to use the toolkit.

## 🐛 Troubleshooting

Having issues? Check the [Troubleshooting Guide](troubleshooting.md) for common problems and solutions.
