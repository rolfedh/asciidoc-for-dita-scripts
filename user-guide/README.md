# AsciiDoc DITA Toolkit Documentation

This directory contains user-facing documentation for the AsciiDoc DITA Toolkit, designed for technical writers preparing content for DITA migration.

## Documentation Structure

- `index.md` - Main user guide homepage (published via GitHub Pages)
- `plugins/` - Individual plugin documentation
  - `ExampleBlock.md` - ExampleBlock plugin user guide
  - (Additional plugin documentation will be added here)
- `_config.yml` - Jekyll configuration for GitHub Pages

## GitHub Pages Publishing

This documentation is published using **GitHub Actions** (not the classic "Deploy from a branch" strategy).

### Configuration
- **Workflow file**: `.github/workflows/pages.yml`
- **Base URL**: `https://rolfedh.github.io/asciidoc-dita-toolkit/user-guide/`
- **Source directory**: `/user-guide/`

### Enabling GitHub Pages
1. Go to your repository Settings → Pages
2. Confirm source is set to "GitHub Actions"
3. The workflow will automatically deploy on pushes to main branch

## Local Development

### Prerequisites
- Python 3.7+ (for simple server)
- Ruby 2.7+ and Bundler (for Jekyll preview)

### Preview Documentation Locally

#### Using Python (Simple)
```bash
cd user-guide
python -m http.server 8000
# Visit http://localhost:8000
```

#### Using Jekyll (Full Features)
```bash
cd user-guide
bundle install
bundle exec jekyll serve
# Visit http://localhost:4000/asciidoc-dita-toolkit/user-guide/
```

### Testing Changes
1. Preview locally before committing
2. Check all internal links work
3. Verify code examples are accurate
4. Test responsive layout on different screen sizes

## Contributing to Documentation

### Adding New Plugin Documentation

1. **Create plugin documentation file:**
   ```bash
   touch plugins/YourPluginName.md
   ```

2. **Follow the established structure:**
   - Purpose and overview
   - Installation/usage instructions
   - Configuration options
   - Examples with expected output
   - Troubleshooting section

3. **Update the main index:**
   - Add plugin to the "Available Plugins" section in `index.md`
   - Include brief description and link to detailed docs

4. **Test the documentation:**
   - Verify all examples work as documented
   - Check cross-references and internal links
   - Preview locally before submitting PR

### Documentation Style Guide

- **Tone**: Professional but approachable; assume technical writing background
- **Code blocks**: Always specify language for syntax highlighting
- **Links**: Use descriptive link text, not "click here"
- **Examples**: Include both command and expected output when relevant
- **Headings**: Use sentence case, maintain consistent hierarchy

### Content Review Process

1. **Technical accuracy**: Verify all commands and examples work
2. **User experience**: Test instructions with fresh eyes
3. **Consistency**: Maintain consistent terminology and formatting
4. **Completeness**: Ensure all features are documented

## Deployment Pipeline

The documentation is automatically deployed when:
1. Changes are pushed to the `main` branch
2. The GitHub Actions workflow (`pages.yml`) runs successfully
3. Jekyll builds the site from the `/user-guide/` directory
4. The built site is deployed to the `gh-pages` branch

### Troubleshooting Deployment

- **Build failures**: Check the Actions tab for error logs
- **Broken links**: Use Jekyll's link checker in local development
- **Missing pages**: Verify file paths and Jekyll front matter
- **Styling issues**: Test with Jekyll locally before deploying

## Maintenance Tasks

### Regular Updates
- [ ] Keep plugin list current as new plugins are added
- [ ] Update installation instructions if requirements change
- [ ] Refresh examples when ADT CLI interface changes
- [ ] Review and update broken external links

### Quality Assurance
- [ ] Quarterly review of all documentation for accuracy
- [ ] User feedback integration from GitHub Issues
- [ ] Performance monitoring of page load times
- [ ] Accessibility compliance checking

---

*This README is for contributors and maintainers. End users should visit the [published documentation](https://rolfedh.github.io/asciidoc-dita-toolkit/user-guide/).*
