# Container Usage Guide

Learn how to use the AsciiDoc DITA Toolkit with Docker containers for consistent, isolated environments.

## 🐳 Available Container Images

### Production Image (Recommended)
```bash
# Docker Hub
rolfedh/asciidoc-dita-toolkit-prod:latest

# GitHub Container Registry
ghcr.io/rolfedh/asciidoc-dita-toolkit-prod:latest
```
- **Size**: ~50MB
- **Purpose**: Production use, CI/CD
- **Contents**: Toolkit only, optimized for size

### Development Image
```bash
# Docker Hub
rolfedh/asciidoc-dita-toolkit:latest

# GitHub Container Registry  
ghcr.io/rolfedh/asciidoc-dita-toolkit:latest
```
- **Size**: ~200MB
- **Purpose**: Development, debugging
- **Contents**: Toolkit + development tools

## 🚀 Basic Usage

### Quick Start
```bash
# Process current directory
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest .

# Process specific directory
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest docs/

# Dry run to preview changes
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest docs/ --dry-run
```

### Command Structure
```bash
docker run [docker-options] [image] [toolkit-arguments]
```

**Docker options:**
- `--rm` - Remove container after execution
- `-v $(pwd):/workspace` - Mount current directory as workspace
- `-e VAR=value` - Set environment variables

## 📁 Volume Mounting

### Mount Current Directory
```bash
# Linux/macOS
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest docs/

# Windows (PowerShell)
docker run --rm -v ${PWD}:/workspace rolfedh/asciidoc-dita-toolkit-prod:latest docs/

# Windows (CMD)
docker run --rm -v %cd%:/workspace rolfedh/asciidoc-dita-toolkit-prod:latest docs/
```

### Mount Specific Directories
```bash
# Mount specific path
docker run --rm -v /path/to/docs:/workspace rolfedh/asciidoc-dita-toolkit-prod:latest .

# Mount multiple directories (process separately)
docker run --rm -v /path/to/docs:/workspace rolfedh/asciidoc-dita-toolkit-prod:latest .
docker run --rm -v /path/to/examples:/workspace rolfedh/asciidoc-dita-toolkit-prod:latest .
```

### Read-Only Mounting
```bash
# Mount as read-only for safety (use with --dry-run)
docker run --rm -v $(pwd):/workspace:ro rolfedh/asciidoc-dita-toolkit-prod:latest docs/ --dry-run
```

## ⚙️ Configuration and Environment

### Environment Variables
```bash
# Non-interactive mode
docker run --rm -v $(pwd):/workspace -e ADT_CONFIG_CHOICE=1 rolfedh/asciidoc-dita-toolkit-prod:latest docs/

# Debug logging
docker run --rm -v $(pwd):/workspace -e ADT_LOG_LEVEL=DEBUG rolfedh/asciidoc-dita-toolkit-prod:latest docs/ --verbose

# Multiple environment variables
docker run --rm \
  -v $(pwd):/workspace \
  -e ADT_CONFIG_CHOICE=1 \
  -e ADT_LOG_LEVEL=WARNING \
  rolfedh/asciidoc-dita-toolkit-prod:latest docs/
```

### User and Permissions
```bash
# Run as current user (Linux/macOS)
docker run --rm -v $(pwd):/workspace --user $(id -u):$(id -g) rolfedh/asciidoc-dita-toolkit-prod:latest docs/

# Run with specific user ID
docker run --rm -v $(pwd):/workspace --user 1000:1000 rolfedh/asciidoc-dita-toolkit-prod:latest docs/
```

## 🔧 Advanced Usage

### Shell Access (Development Image)
```bash
# Interactive shell for debugging
docker run --rm -it -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:latest bash

# Run toolkit from within container
root@container:/workspace# asciidoc-dita-toolkit docs/ --dry-run
```

### Creating Aliases
```bash
# Create convenient alias (add to ~/.bashrc or ~/.zshrc)
alias adt='docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest'

# Usage with alias
adt docs/ --dry-run
adt docs/ --plugins ContentType
```

### Wrapper Scripts

Create a wrapper script for your team:

```bash
#!/bin/bash
# save as 'adt-docker.sh'

# Default image
IMAGE="rolfedh/asciidoc-dita-toolkit-prod:latest"

# Use development image if --dev flag is passed
if [[ "$1" == "--dev" ]]; then
    IMAGE="rolfedh/asciidoc-dita-toolkit:latest"
    shift
fi

# Run container with mounted workspace
docker run --rm \
    -v "$(pwd):/workspace" \
    --user "$(id -u):$(id -g)" \
    -e ADT_CONFIG_CHOICE=1 \
    "$IMAGE" \
    "$@"
```

Usage:
```bash
# Make executable
chmod +x adt-docker.sh

# Use production image
./adt-docker.sh docs/ --dry-run

# Use development image
./adt-docker.sh --dev docs/ --verbose
```

## 🏗️ CI/CD Integration

### GitHub Actions
```yaml
name: AsciiDoc DITA Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate AsciiDoc files
        run: |
          docker run --rm \
            -v ${{ github.workspace }}:/workspace \
            -e ADT_CONFIG_CHOICE=1 \
            rolfedh/asciidoc-dita-toolkit-prod:latest \
            docs/ --dry-run --verbose
```

### GitLab CI
```yaml
validate_asciidoc:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker run --rm 
        -v $PWD:/workspace 
        -e ADT_CONFIG_CHOICE=1 
        rolfedh/asciidoc-dita-toolkit-prod:latest 
        docs/ --dry-run
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Validate AsciiDoc') {
            steps {
                script {
                    docker.image('rolfedh/asciidoc-dita-toolkit-prod:latest').inside('-v $PWD:/workspace') {
                        sh 'asciidoc-dita-toolkit docs/ --dry-run'
                    }
                }
            }
        }
    }
}
```

## 📊 Performance Considerations

### Image Size Comparison
| Image | Size | Use Case |
|-------|------|----------|
| Production | ~50MB | CI/CD, production workflows |
| Development | ~200MB | Local development, debugging |

### Optimization Tips
```bash
# Use production image for automated workflows
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest docs/

# Pre-pull images for faster execution
docker pull rolfedh/asciidoc-dita-toolkit-prod:latest

# Process smaller batches for large repositories
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest docs/section1/
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest docs/section2/
```

## 🔒 Security Considerations

### File Permissions
```bash
# Run as non-root user
docker run --rm -v $(pwd):/workspace --user $(id -u):$(id -g) rolfedh/asciidoc-dita-toolkit-prod:latest docs/

# Use read-only mounts for validation only
docker run --rm -v $(pwd):/workspace:ro rolfedh/asciidoc-dita-toolkit-prod:latest docs/ --dry-run
```

### Network Isolation
```bash
# Disable network access (toolkit doesn't need internet)
docker run --rm --network none -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest docs/
```

## 🐛 Troubleshooting

### Common Issues

**Permission denied errors:**
```bash
# Solution: Run as current user
docker run --rm -v $(pwd):/workspace --user $(id -u):$(id -g) rolfedh/asciidoc-dita-toolkit-prod:latest docs/
```

**Files not found:**
```bash
# Check mount path
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest ls -la

# Verify you're in the right directory
pwd
ls -la docs/
```

**Container won't start:**
```bash
# Check Docker is running
docker version

# Pull latest image
docker pull rolfedh/asciidoc-dita-toolkit-prod:latest
```

### Debug Mode
```bash
# Use development image with shell access
docker run --rm -it -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:latest bash

# Inside container, run toolkit manually
asciidoc-dita-toolkit docs/ --dry-run --verbose
```

## 🚀 Best Practices

1. **Use production image for automation**
2. **Always use `--rm` flag** to clean up containers
3. **Mount only necessary directories** for security
4. **Set user permissions** to avoid file ownership issues
5. **Use environment variables** for non-interactive execution
6. **Create team wrapper scripts** for consistency
7. **Pre-pull images** in CI/CD for faster execution

## 🔗 Related Documentation

- [Installation Guide](installation.md) - Alternative installation methods
- [CLI Reference](cli-reference.md) - Complete command reference
- [Getting Started](getting-started.md) - Basic usage patterns
- [Design: Container Distribution](../design/container-distribution.md) - Technical details
