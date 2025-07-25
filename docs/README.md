# Developer Documentation

This directory contains documentation for developers and maintainers of the AsciiDoc DITA Toolkit.

## Documentation Structure

### 🚀 Getting Started
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Main developer guide with setup instructions
- **[RELEASE_MANAGEMENT.md](RELEASE_MANAGEMENT.md)** - Release workflows and `make publish` usage (maintainers only)
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common installation and runtime issues

### 🔧 Development Guides
- **[development/](development/)** - Specialized development documentation
  - `CONTAINER_DISTRIBUTION.md` - Container build and distribution
  - `PLUGIN_DEVELOPMENT_PATTERN.md` - How to develop new plugins
  - `adt_module_personas_guide.md` - Module development patterns

### 📚 User Documentation
- **[DirectoryConfig.md](DirectoryConfig.md)** - DirectoryConfig plugin documentation
- **[CONTEXT_MIGRATION_GUIDE.md](CONTEXT_MIGRATION_GUIDE.md)** - Context migration guide
- **[BETA_TESTING.md](BETA_TESTING.md)** - Beta testing procedures

{: .note }
**ValeFlagger User Documentation**: See [user-guide/plugins/ValeFlagger.md](../user-guide/plugins/ValeFlagger.md) for technical writer documentation (published via GitHub Pages)

### 🛡️ ValeFlagger Developer Documentation
- **[design/ValeFlagger/](design/ValeFlagger/)** - Design documents and specifications

### 🗄️ Archives
- **[archive/](archive/)** - Historical documentation and completed phase reports
- **[design/](design/)** - Design documents and specifications
- **[development-notes/](development-notes/)** - Implementation notes and fixes
- **[examples/](examples/)** - Code examples and samples

## Quick Links

- **User Documentation**: See [../user-guide/](../user-guide/) (published to GitHub Pages)
- **Source Code**: See [../asciidoc_dita_toolkit/](../asciidoc_dita_toolkit/)
- **Tests**: See [../tests/](../tests/)
- **GitHub Actions**: See [../.github/workflows/](../.github/workflows/)

## Documentation Guidelines

### For New Contributors
1. Start with [CONTRIBUTING.md](CONTRIBUTING.md)
2. Set up development environment with `make setup`
3. Run tests with `make test`
4. Follow the development workflow in the contributing guide

### For Maintainers
1. Use [RELEASE_MANAGEMENT.md](RELEASE_MANAGEMENT.md) for releases
2. One-command release: `make publish`
3. Monitor container builds in GitHub Actions
4. Keep user documentation updated in `user-guide/`

### Adding Documentation
- **User docs**: Add to `../user-guide/` (gets published)
- **Developer docs**: Add to this `docs/` folder
- **Design docs**: Add to `design/` subdirectory
- **Historical**: Move to `archive/` when no longer current
