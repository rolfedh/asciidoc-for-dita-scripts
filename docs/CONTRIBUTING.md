# Contributors: Create plugins, test fixtures, and tests in asciidoc-dita-toolkit

Here’s the recommended workflow for creating test artifacts, plugins, and tests in your current folder structure, and how to update your GitHub issue descriptions to reflect best practices:

### 1. **Creating/Updating Plugins**
- Add new plugins to `asciidoc-dita-toolkit/plugins/` (e.g., `ExampleBlock.py`).
- Follow the structure and docstring conventions used in `EntityReference.py` and `FixContentType.py`.
- Each plugin should have a `register_subcommand` function and a clear `__description__`.

### 2. **Importing and Organizing Test Fixtures**
- Download or sync the relevant fixture directory (e.g., `ExampleBlock/`) from the upstream repo (`asciidoctor-dita-vale/fixtures/ExampleBlock/`).
- Place it in your repo at `asciidoc-dita-toolkit/tests/fixtures/ExampleBlock/`.
- For each `.adoc` fixture, create a corresponding `.expected` file in the same directory.

### 3. **Writing/Updating Tests**
- Add or update test files in `asciidoc-dita-toolkit/tests/` (e.g., `test_ExampleBlock.py`).
- Use `unittest` and the shared testkit (asciidoc_testkit.py) for fixture-based and direct function tests.
- Point your test code to `tests/fixtures/ExampleBlock/` for fixture discovery.

### 4. **CI Integration**
- Ensure your ci.yml downloads the latest fixtures (if needed) and runs all tests using:
  ```sh
  python3 -m unittest discover -s tests
  ```

### 5. **Review and Merge**
- Open a pull request for your changes.
- Request review from relevant maintainers (e.g., @jhradilek for `.expected` files).
- Address feedback, ensure CI passes, and merge when approved.

## **Summary Table for Contributors**

| Task Type         | Location                                      | Notes                                 |
|-------------------|-----------------------------------------------|---------------------------------------|
| Plugin            | plugins                                    | Use `register_subcommand`, docstring  |
| Test fixtures     | `tests/fixtures/<PluginName>/`                | `.adoc` and `.expected` pairs         |
| Test scripts      | `tests/test_<PluginName>.py`                  | Use `unittest`, point to fixtures     |
| Shared test utils | asciidoc_testkit.py                   | For fixture discovery, assertions     |
| CI config         | ci.yml                    | Download fixtures, run all tests      |

