# asciidoc-for-dita-scripts
Scripts to fix or flag issues in that have been identified by [jhradilek/asciidoctor-dita-vale](https://github.com/jhradilek/asciidoctor-dita-vale)

## Quick Start: How to Use the Toolkit

The AsciiDoc-for-DITA toolkit provides a command-line interface (CLI) for processing AsciiDoc files in DITA-based publishing workflows. Each module (plugin) performs a specific transformation or check on your AsciiDoc files.

**Basic usage:**

```sh
python3 asciidoc_toolkit.py <module> [options]
```

- `<module>` is the name of the plugin you want to run (e.g., `fix-entities`).
- `[options]` are module-specific arguments (use `-h` after the module name to see available options).

**Example:**

To fix unsupported HTML character entity references in your `.adoc` files:

```sh
python3 asciidoc_toolkit.py fix-entities -f path/to/file.adoc
```

Or to process all `.adoc` files recursively in a directory:

```sh
python3 asciidoc_toolkit.py fix-entities -r
```

**List available modules:**

```sh
python3 asciidoc_toolkit.py --list-plugins
```

As new modules are added to the `plugins/` directory, they will automatically become available as subcommands.

## Key Components

- **asciidoc_toolkit.py**  
  The main CLI entry point. It dynamically discovers and runs processing plugins from the plugins directory, allowing for a modular, extensible command-line interface.

- **plugins/**  
  Contains individual processing scripts as plugins (e.g., fix_entity_references.py). Each plugin implements a specific transformation or check for AsciiDoc files and can be invoked as a CLI subcommand.

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
