# Documentation Structure

This directory contains the organized documentation for the AsciiDoc DITA Toolkit, designed for GitHub Pages deployment and optimal user experience.

## 📁 Directory Structure

```
docs/
├── _config.yml                 # GitHub Pages configuration
├── index.md                    # Main documentation landing page
├── user-guides/               # End-user documentation
│   ├── installation.md        # Installation methods and setup
│   ├── getting-started.md     # Quick start and basic usage
│   ├── cli-reference.md       # Complete command-line reference
│   ├── containers.md          # Docker/container usage guide
│   └── troubleshooting.md     # Common issues and solutions
├── development/               # Developer and contributor docs
│   ├── contributing.md        # Development setup and workflow
│   ├── plugin-development.md  # Creating custom plugins
│   ├── testing.md            # Testing strategies and tools
│   └── release-process.md     # Release management process
├── reference/                 # Technical reference materials
│   ├── plugins.md            # Available plugins and their behavior
│   ├── architecture.md       # System design and components
│   └── configuration.md      # Configuration options and files
├── design/                    # Design documents and patterns
│   ├── plugin-development-pattern.md  # Technical plugin patterns
│   ├── container-distribution.md      # Container design decisions
│   └── contenttype-ui-design.md       # UI/UX design specifications
└── archive/                   # Historical/legacy documentation
    ├── BETA_TESTING.md        # Legacy beta testing docs
    ├── BETA_TESTING_GUIDE.md  # Legacy testing guide
    ├── agentic-review-prompts.md       # AI review prompts
    └── github_issue_template.md       # Issue template archive
```

## 🎯 Documentation Principles

### Organization
- **User-focused**: Primary navigation follows user journey (install → learn → use → troubleshoot)
- **Progressive disclosure**: Basic concepts first, advanced topics in appropriate sections
- **Cross-linking**: Comprehensive internal links between related topics
- **Searchable**: Clear headings and keywords for easy discovery

### Content Guidelines
- **Practical examples**: Real-world usage patterns and code samples
- **Consistent formatting**: Standardized templates and markdown structure
- **Up-to-date**: Regular review and updates with software changes
- **Accessible**: Clear language and logical information hierarchy

### Maintenance
- **Link validation**: Regular checks for broken internal/external links
- **Content review**: Quarterly review of documentation accuracy
- **User feedback**: Incorporate feedback from GitHub issues and discussions
- **Version alignment**: Keep docs synchronized with software releases

## 🚀 GitHub Pages Configuration

The documentation is configured for GitHub Pages deployment:

- **Theme**: Minima (Jekyll default)
- **URL**: https://rolfedh.github.io/asciidoc-dita-toolkit/
- **Base URL**: /asciidoc-dita-toolkit
- **Build**: Automatic on push to main branch
- **Navigation**: Configured in `_config.yml`

### Local Development

To test documentation changes locally:

```bash
# Install Jekyll (macOS)
brew install ruby
gem install bundler jekyll

# In docs directory
bundle install
bundle exec jekyll serve

# View at http://localhost:4000/asciidoc-dita-toolkit/
```

## 📝 Adding New Documentation

### New User Guide
1. Create file in `user-guides/`
2. Add to navigation in `_config.yml`
3. Link from `index.md`
4. Cross-link from related guides

### New Reference Document
1. Create file in `reference/`
2. Follow existing structure patterns
3. Update cross-references
4. Add to appropriate index pages

### New Development Guide
1. Create file in `development/`
2. Link from contributing guide
3. Add to development section navigation
4. Include practical examples

## 🔗 Link Management

### Internal Links
- Use relative paths: `../reference/plugins.md`
- Include section anchors: `#plugin-name`
- Test all links before committing

### External Links
- Use HTTPS when available
- Prefer permanent URLs (not redirects)
- Check link stability regularly

## 📊 Analytics and Improvement

Track documentation effectiveness:
- GitHub Pages analytics (if enabled)
- User feedback via GitHub issues
- Documentation-related support requests
- Search patterns and common queries

Regular improvement cycle:
1. **Monthly**: Review new issues for documentation gaps
2. **Quarterly**: Comprehensive link and content audit
3. **Release cycle**: Update docs for new features/changes
4. **Annually**: Major reorganization if needed

## 🤝 Contributing to Documentation

See the [Contributing Guide](development/contributing.md) for:
- Documentation style guidelines
- Review process for documentation changes
- Tools and workflows for documentation development
- Testing documentation changes locally

---

**Last Updated**: 2025-01-15  
**Structure Version**: 1.0  
**GitHub Pages URL**: https://rolfedh.github.io/asciidoc-dita-toolkit/
