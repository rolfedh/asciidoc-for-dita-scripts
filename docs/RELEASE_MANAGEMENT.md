# Release Management Guide

## Overview

This project provides automated release workflows for maintainers. The `make publish` command provides a complete "one-command release" that handles everything from version bumping to container publishing.

## Prerequisites

The `make publish` command now **automatically handles most prerequisites**:

✅ **Automated (handled by `make publish`)**:
- Virtual environment creation (`.venv`)
- Development dependencies installation (including twine)
- Build environment cleanup
- Git state validation

⚠️ **Manual setup required**:
1. **GitHub CLI authenticated**: `gh auth login`
2. **PyPI credentials**: Either `PYPI_API_TOKEN` environment variable or `~/.pypirc` file

That's it! Everything else is automated.

## Release Commands

### Quick Release (Recommended)

```bash
# Auto-increment patch version and release everything
make publish

# Use specific version
make publish VERSION=3.0.0
```

### What `make publish` Does

1. **Environment Setup**: Automatically creates `.venv` virtual environment if missing
2. **Dependencies**: Installs development dependencies (twine, build tools) if missing
3. **Git Validation**: Checks that working directory is clean (fails if uncommitted changes)
4. **Environment Cleanup**: Removes old build artifacts  
5. **Version Management**: Auto-increments patch version (2.0.4 → 2.0.5) or uses VERSION= if specified
6. **File Updates**: Modifies both `pyproject.toml` and `src/adt_core/__init__.py`
7. **Package Build**: Clean build with new version using `python -m build`
8. **PyPI Publishing**: Uploads package to PyPI using twine
9. **Git Operations**: Creates and pushes git tag (e.g., `v2.0.5`)
10. **GitHub Release**: Creates GitHub release with changelog notes (if available)
11. **Container Publishing**: Automatically triggers GitHub Actions to build and publish containers

### Alternative Release Commands

```bash
# Just create a GitHub release for current version
make github-release

# Create release for specific version
make github-release VERSION=2.1.0

# Full release workflow with branch management (complex)
make release
```

## Release Workflow Details

### Version Strategy

- **Auto-increment**: Bumps patch version (X.Y.Z → X.Y.Z+1)
- **Manual override**: Use `VERSION=x.y.z` to specify exact version
- **Semantic versioning**: Follow semver principles for version numbers

### Container Publishing

Container images are automatically built and published to GitHub Container Registry when git tags are pushed. Replace `<GITHUB_USERNAME>` in the URLs below with your GitHub username:

- **Development image**: `ghcr.io/<GITHUB_USERNAME>/asciidoc-dita-toolkit:latest`
- **Production image**: `ghcr.io/<GITHUB_USERNAME>/asciidoc-dita-toolkit-prod:latest`  
- **Version-specific**: `ghcr.io/<GITHUB_USERNAME>/asciidoc-dita-toolkit:v2.0.5`

Monitor container builds at: https://github.com/<GITHUB_USERNAME>/asciidoc-dita-toolkit/actions

### Release Notes

The system automatically extracts release notes from `CHANGELOG.md` if available. Format your changelog entries like:

```markdown
## [2.0.5]

### Added
- New feature description

### Fixed  
- Bug fix description
```

## Troubleshooting

### Common Issues

**"No PyPI credentials found"**
```bash
export PYPI_API_TOKEN="pypi-your-token-here"
# OR configure ~/.pypirc file
```

**"GitHub CLI not authenticated"**
```bash
gh auth login
```

**"Working directory is not clean"**
```bash
git status  # Check uncommitted changes
git add . && git commit -m "Prepare for release"
```

**Virtual environment or dependency issues**
- The system automatically handles these, but if issues persist:
```bash
rm -rf .venv  # Remove existing venv
make publish  # Will recreate and setup automatically
```

### Validation Commands

```bash
# Check prerequisites before releasing
make publish-check

# Test version increment logic
current_version=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Current: $current_version"

# Validate GitHub CLI access
gh auth status
gh repo view
```

## For Contributors

Contributors should **not** use the `make publish` command. Instead:

1. Create feature branches
2. Submit pull requests
3. Let maintainers handle releases

## Emergency Procedures

If a release fails partway through:

1. **Check git tags**: `git tag -l` to see if tag was created
2. **Check PyPI**: Verify if package was uploaded 
3. **Check GitHub**: See if release was created
4. **Clean up**: Delete problematic tags/releases if needed
5. **Retry**: Fix issues and run `make publish` again

The system is designed to be idempotent - it won't duplicate tags or releases that already exist.
