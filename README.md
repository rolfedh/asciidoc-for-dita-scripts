# AsciiDoc DITA Toolkit

Scripts to review and fix AsciiDoc content for DITA-based publishing workflows, based on rules from the [asciidoctor-dita-vale](https://github.com/jhradilek/asciidoctor-dita-vale) project.

## What is this?

The AsciiDoc DITA Toolkit is a command-line tool for technical writers and editors. It helps you:
- Find and fix common issues in `.adoc` files before publishing.
- Apply automated checks and transformations using a plugin system.

## Installation (Recommended: PyPI)

Install the toolkit using pip:

```sh
python3 -m pip install asciidoc-dita-toolkit
```

### Upgrading

To upgrade to the latest version:

```sh
python3 -m pip install --upgrade asciidoc-dita-toolkit
```

## Usage

### List available plugins

```sh
asciidoc-dita-toolkit --list-plugins
```

### Run a plugin

```sh
asciidoc-dita-toolkit <plugin> [options]
```
- `<plugin>`: Name of the plugin to run (e.g., `EntityReference`)
- `[options]`: Plugin-specific options (e.g., `-f` for a file, `-r` for recursive)

#### Examples

Fix unsupported HTML character entity references in a file:
```sh
asciidoc-dita-toolkit EntityReference -f path/to/file.adoc
```

Process all `.adoc` files recursively in the current directory:
```sh
asciidoc-dita-toolkit EntityReference -r
```

> **Tip:** For plugin-specific details, see the [available rules](https://github.com/jhradilek/asciidoctor-dita-vale?tab=readme-ov-file#available-rules) in the `asciidoctor-dita-vale` repository.

## Troubleshooting
- Make sure you are using Python 3.7 or newer.
- If you need to use a local clone (for development or custom plugins), see the [contributor guide](docs/CONTRIBUTING.md).

## Related resources

- **[`asciidoctor-dita-vale`](https://github.com/jhradilek/asciidoctor-dita-vale)**: Vale style rules and test fixtures for validating AsciiDoc content.

## Contributing

Want to add new plugins or help improve the toolkit? See [CONTRIBUTING.md](docs/CONTRIBUTING.md).