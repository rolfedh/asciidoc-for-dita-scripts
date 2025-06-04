# CONTRIBUTING: How to create plugins, test fixtures, and tests in asciidoc-dita-toolkit

## Contributor Workflow: Creating Plugins, Test Fixtures, and Tests

Here’s the recommended workflow for creating test artifacts, plugins, and tests in your current folder structure. 

**Important:** Use the established rule name when creating all files and directories, such as `ExampleBlock`, `EntityReference`, etc. This ensures consistency and makes it easier to manage tests and plugins.

### 1. Importing and Organizing Test Fixtures
- For the rule you're working on, download or sync the relevant fixture directory (e.g., `ExampleBlock/`) from the upstream repo (e.g., `asciidoctor-dita-vale/fixtures/ExampleBlock/`).
- Place it in your repo at `asciidoc-dita-toolkit/tests/fixtures/<rulename>/`.
- For each `.adoc` fixture, create a corresponding `.expected` file in the same directory.

### 2. Creating or Updating Plugins
- Add new plugins to `asciidoc-dita-toolkit/plugins/` (e.g., `ExampleBlock.py`).
- Follow the structure and docstring conventions used in `EntityReference.py`.
- Each plugin should have a `register_subcommand` function and a clear `__description__`.

### 3. Writing or Updating Tests
- Add or update the test file in `asciidoc-dita-toolkit/tests/`. The filename _must_ have a `test_` prefix (e.g., `test_ExampleBlock.py`).
- Use `unittest` and the shared testkit (`asciidoc_testkit.py`) for fixture-based and direct function tests.
- Point your test code to `tests/fixtures/<rulename>/` for fixture discovery.

### 4. CI Integration
- Ensure your `ci.yml` downloads the latest fixtures (if needed) and runs all tests using:
  ```sh
  python3 -m unittest discover -s tests
  ```

### 5. Review and Merge
- Open a pull request for your changes.
- Request review from relevant maintainers (e.g., @jhradilek for `.expected` files).
- Address feedback, ensure CI passes, and merge when approved.

## Summary Table for Contributors

| Task Type         | Location                                      | Notes                                 |
|-------------------|-----------------------------------------------|---------------------------------------|
| Test fixtures     | `tests/fixtures/<PluginName>/`                | `.adoc` and `.expected` pairs         |
| Plugin            | `plugins/`                                    | Use `register_subcommand`, docstring  |
| Test scripts      | `tests/test_<PluginName>.py`                  | Use `unittest`, point to fixtures     |
| Shared test utils | `tests/asciidoc_testkit.py`                   | For fixture discovery, assertions     |
| CI config         | `.github/workflows/ci.yml`                    | Download fixtures, run all tests      |

