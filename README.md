# AsciiDoc DITA Toolkit
Scripts to fix or flag issues in that have been identified by [jhradilek/asciidoctor-dita-vale](https://github.com/jhradilek/asciidoctor-dita-vale)

## Quick Start: How to Use the Toolkit

The AsciiDoc DITA Toolkit provides a command-line interface (CLI) for processing AsciiDoc files in DITA-based publishing workflows. Each plugin performs a specific transformation or check on your AsciiDoc files.

1. **Clone the repository to your local machine:**

```sh
git clone https://github.com/your-org/asciidoc-dita-toolkit.git
```

2. **Change to your documentation directory:**

```sh
cd /path/to/your/docs
```

3. **Get a list of the available plugins:**

```sh
python3 ~/asciidoc-dita-toolkit/asciidoc_toolkit.py --list-plugins
```

NOTE: For additional information about any plugin, look it up at https://github.com/jhradilek/asciidoctor-dita-vale?tab=readme-ov-file#available-rules

NOTE: As new plugins are added to the `plugins/` directory, they automatically become available as subcommands.

4. **Run the desired plugin:**

```sh
python3 ~/asciidoc-dita-toolkit/asciidoc_toolkit.py <plugin> [options]
```

- `<plugin>` is the name of the plugin you want to run (e.g., `entity-reference`).
- `[options]` are plugin-specific arguments (use `-h` after the plugin name to see available options).

**Examples:**

To fix unsupported HTML character entity references in your `.adoc` files:

```sh
python3 ~/asciidoc-dita-toolkit/asciidoc_toolkit.py entity-reference -f path/to/file.adoc
```

Or to process all `.adoc` files recursively in a directory:

```sh
python3 ~/asciidoc-dita-toolkit/asciidoc_toolkit.py entity-reference -r
```



## Key Components

- **asciidoc_toolkit.py**  
  The main CLI entry point. It dynamically discovers and runs processing plugins from the plugins directory, allowing for a modular, extensible command-line interface.

- **plugins/**  
  Contains individual processing scripts as plugins (e.g., EntityReference.py). Each plugin implements a specific transformation or check for AsciiDoc files and can be invoked as a CLI subcommand.

- **file_utils.py**  
  Shared utility functions for file discovery, reading/writing with preserved line endings, and argument parsing. Used by all plugins to avoid code duplication.

- **tests/**  
  Contains automated test scripts and reusable test utilities (`asciidoc_testkit.py`). Tests use fixtures to ensure plugins work as expected and to prevent regressions.

- **requirements.txt**  
  Lists Python dependencies for development and running the toolkit.

- **README.md**  
  Project documentation, including setup instructions, usage examples, and contribution guidelines.

## Related Resources

- **asciidoctor-dita-vale/**  
  Contains Vale style rules and a comprehensive set of test fixtures for AsciiDoc/DITA processing. Useful for both linting and plugin test development.

---

## Contributing

Interested in contributing? The project is designed for maintainability, scalability, and easy onboarding.

- New features or checks should be added as plugins in the plugins directory.
- Shared logic should go in file_utils.py or `asciidoc_testkit.py`.
- All new plugins should include automated tests in the tests directory, using the provided testkit and fixtures.
- See README.md for setup and contribution details.

### Why Volunteer?

- The project is actively maintained and designed for easy onboarding.
- You’ll work with modern Python, robust testing, and a plugin-based architecture.
- Your contributions will help improve open-source publishing workflows for the AsciiDoc and DITA communities.
