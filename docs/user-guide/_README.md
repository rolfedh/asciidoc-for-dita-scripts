# AsciiDoc DITA Toolkit Documentation

This directory contains user-facing documentation for the AsciiDoc DITA Toolkit, designed for technical writers preparing content for DITA migration.

## Structure

- `README.md` - Main user guide overview
- `plugins/` - Individual plugin documentation
  - `ExampleBlock.md` - ExampleBlock plugin user guide
  - (Additional plugin documentation will be added here)

## GitHub Pages Setup

This documentation is designed to be published as GitHub Pages. To enable:

1. Go to your repository settings
2. Navigate to "Pages" section
3. Set source to "Deploy from a branch"
4. Select branch and `/docs` folder
5. The documentation will be available at `https://rolfedh.github.io/asciidoc-dita-toolkit/user-guide/`

## Local Development

To preview the documentation locally:

```bash
# Using Python's built-in server
cd docs
python -m http.server 8000

# Or using Ruby's Jekyll (if installed)
bundle exec jekyll serve
```

## Contributing

When adding new plugin documentation:

1. Create a new `.md` file in the `plugins/` directory
2. Follow the structure and style of `ExampleBlock.md`
3. Update the main `README.md` to include the new plugin
4. Test the documentation locally before committing
