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

## Usage

### List available plugins

```sh
python3 -m asciidoc_dita_toolkit.asciidoc_dita.toolkit --list-plugins
```

### Run a plugin

```sh
python3 -m asciidoc_dita_toolkit.asciidoc_dita.toolkit <plugin> [options]
```
- `<plugin>`: Name of the plugin to run (e.g., `EntityReference`)
- `[options]`: Plugin-specific options (e.g., `-f` for a file, `-r` for recursive)

#### Examples

Fix unsupported HTML character entity references in a file:
```sh
python3 -m asciidoc_dita_toolkit.asciidoc_dita.toolkit EntityReference -f path/to/file.adoc
```

Process all `.adoc` files recursively in the current directory:
```sh
python3 -m asciidoc_dita_toolkit.asciidoc_dita.toolkit EntityReference -r
```

> **Tip:** If you installed via pip, you can also use the CLI script:
> ```sh
> asciidoc-dita-toolkit --list-plugins
> ```

## Troubleshooting
- Make sure you are using Python 3.7 or newer.
- If you need to use a local clone (for development or custom plugins), see the [contributor guide](docs/CONTRIBUTING.md).

## Related resources

- **[`asciidoctor-dita-vale`](https://github.com/jhradilek/asciidoctor-dita-vale)**: Vale style rules and test fixtures for validating AsciiDoc content.

## Contributing

Want to add new plugins or help improve the toolkit? See [CONTRIBUTING.md](docs/CONTRIBUTING.md).