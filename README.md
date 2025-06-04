# AsciiDoc DITA Toolkit

Scripts that fix or flag issues identified by the [jhradilek/asciidoctor-dita-vale](https://github.com/jhradilek/asciidoctor-dita-vale) project.

## Quick start

The AsciiDoc DITA Toolkit is a command-line interface (CLI) that supports DITA-based publishing workflows. Each plugin in the toolkit performs a specific check or transformation on AsciiDoc content.

### Step 1: Clone the repository

If you are a user:

```sh
git clone https://github.com/rolfedh/asciidoc-dita-toolkit.git
````

If you are a contributor, first fork the repository to your own GitHub account, then clone it:

```sh
git clone https://github.com/<your-org>/asciidoc-dita-toolkit.git
```

### Step 2: Change to your documentation directory

```sh
cd /path/to/your/docs
```

### Step 3: List available plugins

```sh
python3 ~/asciidoc-dita-toolkit/asciidoc_toolkit.py --list-plugins
```

> **Note**: For plugin-specific details, see the [available rules](https://github.com/jhradilek/asciidoctor-dita-vale?tab=readme-ov-file#available-rules) in the `asciidoctor-dita-vale` repository.

> **Note**: Plugins added to the `plugins/` directory are automatically available as subcommands.

### Step 4: Run a plugin

```sh
python3 ~/asciidoc-dita-toolkit/asciidoc_toolkit.py <plugin> [options]
```

* `<plugin>` is the name of the plugin to run (for example, `EntityReference`)
* `[options]` include:

  * `-f` to target a specific file
  * `-r` to recursively process a directory
  * `-h` to display help for the plugin

#### Examples

To fix unsupported HTML character entity references in a file:

```sh
python3 ~/asciidoc-dita-toolkit/asciidoc_toolkit.py EntityReference -f path/to/file.adoc
```

To process all `.adoc` files recursively in the current directory:

```sh
python3 ~/asciidoc-dita-toolkit/asciidoc_toolkit.py EntityReference -r
```

## Toolkit components

* **`asciidoc_toolkit.py`**
  Entry point for the CLI. Automatically discovers and runs plugins from the `plugins/` directory.

* **`plugins/`**
  Contains individual plugin scripts. Each plugin performs a specific transformation or validation on `.adoc` files.

* **`file_utils.py`**
  Shared utility functions for file discovery, I/O with preserved line endings, and argument parsing.

* **`tests/`**
  Automated tests and fixtures that validate plugin behavior and prevent regressions.

* **`requirements.txt`**
  Lists Python dependencies for development and use.

* **`README.md`**
  Provides setup instructions, usage examples, and contribution guidelines.

## Related resources

* **[`asciidoctor-dita-vale`](https://github.com/jhradilek/asciidoctor-dita-vale)**
  A collection of Vale style rules and test fixtures for validating AsciiDoc content.

## Contributing

Want to contribute? Contributions are welcome and the project is designed for ease of onboarding.

* Add new functionality as plugins in the `plugins/` directory.
* Place shared logic in `file_utils.py` or `asciidoc_testkit.py`.
* Include tests for new plugins in the `tests/` directory.

For setup and contribution details, see the [contributor guide](docs/CONTRIBUTING.md).

### Why contribute?

* The project uses modern Python and robust testing practices.
* You’ll help improve publishing workflows in the AsciiDoc and DITA communities.
* Contributions are actively reviewed and maintained.

## Running Tests

To run all tests:

```sh
~/asciidoc-dita-toolkit main$ python3 -m unittest discover -s tests
```

This command finds and runs all test files in the `tests/` directory that match the pattern `test_*.py`.