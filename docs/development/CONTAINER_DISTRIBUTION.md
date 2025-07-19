# Container Distribution Strategy for AsciiDoc DITA Toolkit

## Overview

The AsciiDoc DITA Toolkit is automatically distributed as container images through GitHub Container Registry (ghcr.io) using GitHub Actions. This provides seamless, authenticated builds and distribution without external dependencies.

## Automated Container Distribution

### GitHub Container Registry (Primary)

All container images are automatically built and published to GitHub Container Registry when:
- Tags matching `v*` are pushed (releases)
- Pushes are made to the `main` branch
- Manual workflow dispatch is triggered

**Available Images:**
- `ghcr.io/rolfedh/asciidoc-dita-toolkit:latest` - Development build with all tools
- `ghcr.io/rolfedh/asciidoc-dita-toolkit-prod:latest` - Production optimized build
- `ghcr.io/rolfedh/asciidoc-dita-toolkit:v1.2.3` - Version-specific tags

### Usage

```bash
# Run with current directory mounted as workspace
docker run --rm -v $(pwd):/workspace ghcr.io/rolfedh/asciidoc-dita-toolkit:latest ContentType --help

# Interactive shell for development
docker run --rm -it -v $(pwd):/workspace ghcr.io/rolfedh/asciidoc-dita-toolkit:latest /bin/bash

# Production optimized version
docker run --rm -v $(pwd):/workspace ghcr.io/rolfedh/asciidoc-dita-toolkit-prod:latest ContentType src/
```

## Automated Build Process

The container build process is fully automated through GitHub Actions (`.github/workflows/container-build.yml`):

1. **Triggers**: Git tags, main branch pushes, or manual dispatch
2. **Multi-platform**: Builds for `linux/amd64` and `linux/arm64`
3. **Caching**: Uses GitHub Actions cache for faster builds
4. **Testing**: Automated container functionality tests
5. **Publishing**: Automatic push to GitHub Container Registry

### Build Matrix

Two container variants are built:
- **Development** (`Dockerfile`): Full development environment
- **Production** (`Dockerfile.production`): Optimized multi-stage build

## Authentication

GitHub Container Registry authentication is handled automatically:
- **GitHub Actions**: Uses `GITHUB_TOKEN` (built-in)
- **Local development**: Use `gh auth token` or personal access token

```bash
# Authenticate locally (if needed)
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin
```

## Benefits of Automated Distribution

- ✅ **No external dependencies** - No Docker Hub authentication issues
- ✅ **Integrated with GitHub** - Same permissions as repository access  
- ✅ **Free for public projects** - No cost for open source distribution
- ✅ **Automatic builds** - No manual intervention required
- ✅ **Multi-platform support** - Works on Intel and ARM architectures
- ✅ **Version tracking** - Automatic semantic version tagging

## Migration from Docker Hub

Previously, containers were distributed via Docker Hub. This has been migrated to GitHub Container Registry for better integration and reliability. All Docker Hub references have been updated to use `ghcr.io/rolfedh/asciidoc-dita-toolkit`.

## Troubleshooting
