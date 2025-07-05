# Troubleshooting Guide

Common issues and solutions when using the AsciiDoc DITA Toolkit.

## 🔍 Quick Diagnostics

Before diving into specific issues, run these quick checks:

```bash
# Check version
asciidoc-dita-toolkit --version

# Test with dry run
asciidoc-dita-toolkit your-docs/ --dry-run --verbose

# List available plugins
asciidoc-dita-toolkit --list-plugins
```

## 📁 File and Directory Issues

### "No .adoc files found"

**Problem**: The toolkit reports no AsciiDoc files found in the specified directory.

**Solutions**:
```bash
# Check if files exist
ls -la your-docs/*.adoc

# Check file extensions (must be .adoc)
find your-docs/ -name "*.adoc"

# Use correct path
asciidoc-dita-toolkit ./docs/  # Note the ./
```

### "Permission denied" errors

**Problem**: Cannot read or write files.

**Solutions**:
```bash
# Check file permissions
ls -la your-docs/

# Fix permissions
chmod 644 your-docs/*.adoc
chmod 755 your-docs/

# For containers, run as current user
docker run --rm -v $(pwd):/workspace --user $(id -u):$(id -g) rolfedh/asciidoc-dita-toolkit-prod:latest docs/
```

### "File is not valid AsciiDoc"

**Problem**: File cannot be parsed as AsciiDoc.

**Solutions**:
```bash
# Check file encoding (should be UTF-8)
file your-file.adoc

# Check for binary data
head -c 100 your-file.adoc

# Validate AsciiDoc syntax manually
asciidoctor --safe-mode=unsafe --backend=html5 your-file.adoc
```

## 🔧 Installation Issues

### "Command not found: asciidoc-dita-toolkit"

**Problem**: Toolkit not found after installation.

**Solutions**:
```bash
# Verify installation
pip list | grep asciidoc-dita-toolkit

# Check PATH
echo $PATH

# Reinstall
pip uninstall asciidoc-dita-toolkit
pip install asciidoc-dita-toolkit

# Use full path
python -m asciidoc_dita_toolkit.asciidoc_dita.toolkit --help
```

### Python version issues

**Problem**: "Python 3.7+ required" error.

**Solutions**:
```bash
# Check Python version
python --version
python3 --version

# Use specific Python version
python3.8 -m pip install asciidoc-dita-toolkit

# Use containers instead (no Python required)
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest --help
```

## 🐳 Container Issues

### "Docker command not found"

**Problem**: Docker not installed or not in PATH.

**Solutions**:
```bash
# Install Docker (Ubuntu/Debian)
sudo apt update && sudo apt install docker.io

# Install Docker (macOS)
brew install docker

# Check Docker status
docker --version
sudo systemctl status docker  # Linux
```

### "Cannot connect to Docker daemon"

**Problem**: Docker daemon not running or permission issues.

**Solutions**:
```bash
# Start Docker daemon (Linux)
sudo systemctl start docker

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Then log out and back in

# Use sudo (temporary fix)
sudo docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest --help
```

### "No such file or directory" in container

**Problem**: Files not accessible inside container.

**Solutions**:
```bash
# Check mount path
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest ls -la

# Use absolute paths
docker run --rm -v /full/path/to/docs:/workspace rolfedh/asciidoc-dita-toolkit-prod:latest .

# Verify working directory
pwd
ls -la docs/
```

## 🔌 Plugin Issues

### "Plugin not found" errors

**Problem**: Specified plugin doesn't exist.

**Solutions**:
```bash
# List available plugins
asciidoc-dita-toolkit --list-plugins

# Check plugin name spelling
asciidoc-dita-toolkit docs/ --plugins ContentType  # Correct
asciidoc-dita-toolkit docs/ --plugins contenttype  # Wrong

# Use exact plugin names
asciidoc-dita-toolkit docs/ --plugins ContentType,EntityReference
```

### Plugin configuration issues

**Problem**: DirectoryConfig plugin prompts in automation.

**Solutions**:
```bash
# Use environment variable for automation
export ADT_CONFIG_CHOICE=1
asciidoc-dita-toolkit docs/

# Or disable DirectoryConfig plugin
asciidoc-dita-toolkit docs/ --plugins ContentType,EntityReference
```

### "No content type detected" warnings

**Problem**: ContentType plugin cannot determine content type.

**Solutions**:
1. **Add content indicators** to your AsciiDoc:
   ```asciidoc
   = Installing Docker
   
   This procedure shows how to install Docker.
   
   . Download Docker
   . Install the package
   . Start the service
   ```

2. **Use explicit content type comments**:
   ```asciidoc
   // content-type: procedure
   = Installing Docker
   ```

3. **Check file structure** - ensure proper AsciiDoc formatting

## 📝 Content Processing Issues

### "Cannot parse file" errors

**Problem**: File has syntax issues that prevent processing.

**Solutions**:
```bash
# Test with AsciiDoctor directly
asciidoctor --safe-mode=unsafe your-file.adoc

# Check for common issues:
# - Missing blank lines after titles
# - Incorrect attribute syntax
# - Malformed tables or lists

# Use dry run to identify problematic files
asciidoc-dita-toolkit docs/ --dry-run --verbose
```

### "Unexpected character encoding"

**Problem**: File contains non-UTF-8 characters.

**Solutions**:
```bash
# Check file encoding
file -i your-file.adoc

# Convert to UTF-8
iconv -f ISO-8859-1 -t UTF-8 your-file.adoc -o your-file-utf8.adoc

# Find non-UTF-8 files
find docs/ -name "*.adoc" -exec file -i {} \; | grep -v "utf-8"
```

## ⚡ Performance Issues

### "Processing very slow"

**Problem**: Toolkit takes too long on large repositories.

**Solutions**:
```bash
# Process smaller batches
asciidoc-dita-toolkit docs/section1/
asciidoc-dita-toolkit docs/section2/

# Use specific plugins only
asciidoc-dita-toolkit docs/ --plugins ContentType

# Monitor with verbose output
asciidoc-dita-toolkit docs/ --verbose

# Check for very large files
find docs/ -name "*.adoc" -size +1M
```

### Memory issues

**Problem**: "Out of memory" errors or system slowdown.

**Solutions**:
```bash
# Process files individually
for file in docs/*.adoc; do
    asciidoc-dita-toolkit "$file"
done

# Use containers with memory limits
docker run --rm -m 512m -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest docs/

# Monitor memory usage
top -p $(pgrep -f asciidoc-dita-toolkit)
```

## 🔄 Environment and Configuration

### Environment variable issues

**Problem**: Environment variables not being recognized.

**Solutions**:
```bash
# Check environment variables
echo $ADT_CONFIG_CHOICE
echo $ADT_LOG_LEVEL

# Set for current session
export ADT_CONFIG_CHOICE=1
export ADT_LOG_LEVEL=DEBUG

# Set for single command
ADT_CONFIG_CHOICE=1 asciidoc-dita-toolkit docs/
```

### Path issues

**Problem**: Toolkit finds wrong files or directories.

**Solutions**:
```bash
# Use absolute paths
asciidoc-dita-toolkit /full/path/to/docs/

# Check current working directory
pwd

# List contents to verify
ls -la docs/

# Use explicit current directory
asciidoc-dita-toolkit ./docs/
```

## 🆘 Getting Help

### Debug output

Enable detailed logging to understand what's happening:

```bash
# Maximum verbosity
export ADT_LOG_LEVEL=DEBUG
asciidoc-dita-toolkit docs/ --verbose

# Dry run with verbose output
asciidoc-dita-toolkit docs/ --dry-run --verbose
```

### Minimal reproduction

Create a minimal test case:

```bash
# Create test directory
mkdir test-case
cd test-case

# Create simple test file
echo "= Test Document

This is a test." > test.adoc

# Test with minimal setup
asciidoc-dita-toolkit . --dry-run --verbose
```

### System information

Gather system information for bug reports:

```bash
# Operating system
uname -a

# Python version
python --version

# Toolkit version
asciidoc-dita-toolkit --version

# Docker version (if using containers)
docker --version

# Available disk space
df -h .

# Available memory
free -h  # Linux
vm_stat  # macOS
```

## 📞 Support Resources

If you're still having issues:

1. **Check the [GitHub Issues](https://github.com/rolfedh/asciidoc-dita-toolkit/issues)** for similar problems
2. **Create a new issue** with:
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Debug output (with `--verbose`)
3. **Use [GitHub Discussions](https://github.com/rolfedh/asciidoc-dita-toolkit/discussions)** for questions

## 🔗 Related Documentation

- [Installation Guide](installation.md) - Setup instructions
- [Getting Started](getting-started.md) - Basic usage
- [CLI Reference](cli-reference.md) - Command options
- [Container Usage](containers.md) - Docker-specific issues
