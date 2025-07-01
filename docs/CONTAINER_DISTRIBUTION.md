# Container Distribution Strategy for AsciiDoc DITA Toolkit

## Overview

This document outlines multiple approaches for distributing the asciidoc-dita-toolkit as a container, complementing the existing PyPI distribution.

## Container Distribution Options

### 1. Docker Hub (Recommended for Public Distribution)

Docker Hub provides free public repositories and is the most widely used container registry.

**Setup:**
```bash
# Build and tag the image
docker build -t rolfedh/asciidoc-dita-toolkit:latest .
docker build -t rolfedh/asciidoc-dita-toolkit:0.1.6 .

# Push to Docker Hub
docker login
docker push rolfedh/asciidoc-dita-toolkit:latest
docker push rolfedh/asciidoc-dita-toolkit:0.1.6
```

**Usage:**
```bash
# Run the container
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:latest ContentType --help

# Interactive shell
docker run --rm -it -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:latest /bin/bash
```

### 2. GitHub Container Registry (GHCR)

GitHub's container registry integrates well with GitHub Actions and provides free hosting for public repositories.

**Setup:**
```bash
# Build and tag for GHCR
docker build -t ghcr.io/rolfedh/asciidoc-dita-toolkit:latest .
docker build -t ghcr.io/rolfedh/asciidoc-dita-toolkit:0.1.6 .

# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u rolfedh --password-stdin

# Push to GHCR
docker push ghcr.io/rolfedh/asciidoc-dita-toolkit:latest
docker push ghcr.io/rolfedh/asciidoc-dita-toolkit:0.1.6
```

### 3. Red Hat Quay.io

Enterprise-focused container registry with advanced security scanning.

**Setup:**
```bash
# Build and tag for Quay
docker build -t quay.io/rolfedh/asciidoc-dita-toolkit:latest .

# Login and push
docker login quay.io
docker push quay.io/rolfedh/asciidoc-dita-toolkit:latest
```

### 4. Multi-Registry Distribution

Distribute to multiple registries for maximum availability:

```bash
# Build once, tag for multiple registries
docker build -t asciidoc-dita-toolkit:0.1.6 .

# Tag for different registries
docker tag asciidoc-dita-toolkit:0.1.6 rolfedh/asciidoc-dita-toolkit:0.1.6
docker tag asciidoc-dita-toolkit:0.1.6 ghcr.io/rolfedh/asciidoc-dita-toolkit:0.1.6
docker tag asciidoc-dita-toolkit:0.1.6 quay.io/rolfedh/asciidoc-dita-toolkit:0.1.6

# Push to all registries
docker push rolfedh/asciidoc-dita-toolkit:0.1.6
docker push ghcr.io/rolfedh/asciidoc-dita-toolkit:0.1.6
docker push quay.io/rolfedh/asciidoc-dita-toolkit:0.1.6
```

## Container Variants

### 1. Standard Container (`Dockerfile`)
- Based on `python:3.11-slim`
- Includes development dependencies
- Good for development and testing
- Size: ~150MB

### 2. Production Container (`Dockerfile.production`)
- Multi-stage build for smaller size
- Only runtime dependencies
- Security-focused with non-root user
- Size: ~100MB

### 3. Alpine-based Container (Ultra-lightweight)

```dockerfile
# Dockerfile.alpine
FROM python:3.11-alpine

RUN adduser -D -s /bin/sh toolkit

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .

USER toolkit
WORKDIR /workspace

ENTRYPOINT ["asciidoc-dita-toolkit"]
CMD ["--help"]
```

Size: ~50MB

## Automation with GitHub Actions

### Container Build and Push Workflow

```yaml
# .github/workflows/container-build.yml
name: Build and Push Container

on:
  push:
    tags: ['v*']
  release:
    types: [published]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Login to GHCR
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: |
          rolfedh/asciidoc-dita-toolkit
          ghcr.io/rolfedh/asciidoc-dita-toolkit
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./Dockerfile.production
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        platforms: linux/amd64,linux/arm64
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

## Usage Examples

### 1. Basic Usage
```bash
# Run on current directory
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:latest ContentType src/

# Check a specific file
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:latest EntityReference myfile.adoc
```

### 2. Development Usage
```bash
# Interactive development
docker run --rm -it -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:latest /bin/bash

# Run tests in container
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:latest python -m pytest
```

### 3. CI/CD Integration
```yaml
# Example CI step
- name: Validate AsciiDoc files
  run: |
    docker run --rm -v ${{ github.workspace }}:/workspace \
      rolfedh/asciidoc-dita-toolkit:latest ContentType docs/
```

### 4. Docker Compose for Documentation Workflows
```yaml
# docker-compose.yml
version: '3.8'
services:
  asciidoc-toolkit:
    image: rolfedh/asciidoc-dita-toolkit:latest
    volumes:
      - ./docs:/workspace
    working_dir: /workspace
    command: ContentType --interactive .
```

## Container Security

### Security Features Implemented
- **Non-root user**: Containers run as user `toolkit` (UID 1000)
- **Minimal base image**: Using `python:3.11-slim` for security updates
- **No unnecessary packages**: Only essential dependencies installed
- **Read-only filesystem**: Can be run with `--read-only` flag
- **No secrets in image**: All configuration via environment variables

### Security Best Practices
```bash
# Run with security constraints
docker run --rm \
  --read-only \
  --security-opt=no-new-privileges:true \
  --cap-drop=ALL \
  -v $(pwd):/workspace:ro \
  rolfedh/asciidoc-dita-toolkit:latest ContentType /workspace
```

## Distribution Recommendations

### For Public Open Source Project:
1. **Primary**: GitHub Container Registry (GHCR) - Free and integrated
2. **Secondary**: Docker Hub - Wide adoption and discoverability
3. **Automation**: GitHub Actions for automated builds

### For Enterprise/Private Use:
1. **Primary**: Private registry (Harbor, Artifactory, etc.)
2. **Secondary**: Red Hat Quay.io for security scanning
3. **Backup**: Cloud provider registry (ECR, ACR, GCR)

### Tagging Strategy:
- `latest` - Latest stable release
- `v1.2.3` - Specific version tags
- `v1.2` - Major.minor tags
- `v1` - Major version tags
- `dev` - Development/nightly builds

This strategy provides multiple distribution options while maintaining security and automation best practices.
