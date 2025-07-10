# Migration Guide: Unified Package (v2.0.0+)

## Overview

The AsciiDoc DITA Toolkit has been unified under a single PyPI package: **`asciidoc-dita-toolkit`**

**Key Changes in v2.0.0:**
- **Same package name**: Still `asciidoc-dita-toolkit` for familiarity
- **Unified functionality**: Now includes both core framework and all plugins in one package
- **Short CLI command**: Use the convenient `adt` command instead of the long package name
- **Complete toolkit**: No more missing modules or installation issues

## For New Users

Simply install and use:

```sh
pip install asciidoc-dita-toolkit
adt --help  # Short, convenient command
```

## For Existing Users

If you were using previous versions, you may have encountered split packages or issues. Here's how to ensure you have the complete, working toolkit:

### Clean Installation (Recommended)

```sh
# Remove any previous installations
pip uninstall adt-core asciidoc-dita-toolkit -y

# Install the unified v2.0.0+ package
pip install asciidoc-dita-toolkit

# Verify everything works
adt --version
adt --list-plugins
```

### Update Scripts and Documentation

The CLI command is now the short and convenient `adt`:

**Before (if you used the long command):**
```sh
asciidoc-dita-toolkit EntityReference -f file.adoc
```

**Now (short and convenient):**
```sh
adt EntityReference -f file.adoc
```

### Update Container Aliases (if using)

Container usage remains the same:

```sh
alias adt='docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest'
```

## What's New in v2.0.0

✅ **Complete Package**: Includes both the core framework and all plugins  
✅ **Simplified CLI**: Short, memorable `adt` command  
✅ **Same Installation**: Familiar `pip install asciidoc-dita-toolkit`  
✅ **Better Testing**: More comprehensive packaging and installation testing  
✅ **No Missing Modules**: All functionality available in one package  

## Backwards Compatibility

- Package name remains the same: `asciidoc-dita-toolkit`
- All CLI options and flags work exactly the same
- All plugins have the same names and behavior
- Container images remain unchanged
- Python import paths remain the same for developers

## Verification

After installation, verify everything works:

```sh
# Check installation
adt --version

# List available plugins
adt --list-plugins

# Test a plugin
adt EntityReference --help
```

## Troubleshooting

### "Command not found: adt"

This usually means the package isn't installed or there's a PATH issue:

```sh
pip install asciidoc-dita-toolkit
# or if upgrading:
pip install --upgrade asciidoc-dita-toolkit
```

### Import errors in Python code

If you're developing with the toolkit, verify the package is installed correctly:

```sh
python -c "import adt_core; import asciidoc_dita_toolkit; print('Success')"
```

### Package conflicts

If you see conflicts or import errors:

```sh
pip list | grep -E "(adt|asciidoc)"
# Should show: asciidoc-dita-toolkit    2.0.0 (or higher)
```

## Support

If you encounter any issues during migration:

1. Check the [troubleshooting section](README.md#-troubleshooting) in the main README
2. [Open an issue](https://github.com/rolfedh/asciidoc-dita-toolkit/issues) with details about your environment and the error
3. Include the output of `pip list | grep -E "(adt|asciidoc)"` to help diagnose package conflicts

## Summary

**For new users:**
```bash
pip install asciidoc-dita-toolkit
adt EntityReference -f file.adoc
```

**For existing users:**
```bash
pip install --upgrade asciidoc-dita-toolkit  # Get v2.0.0+
adt EntityReference -f file.adoc              # Same great CLI
```

The v2.0.0 release represents a significant improvement in packaging and user experience while maintaining full backwards compatibility for all functionality.