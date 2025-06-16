# Create test artifacts and implement plugin for TaskExample

## Overview
This issue is optimized for GitHub Copilot Agent Mode. It provides all the context and requirements needed for the agent to assist with implementation, testing, and integration.

## Context
- Upstream Vale fixtures: `asciidoctor-dita-vale/fixtures/TaskExample/`
- Test artifacts to be created: `./tests/fixtures/TaskExample/*.expected`
- Plugin to be implemented: `asciidoc_dita_toolkit/asciidoc_dita/plugins/TaskExample.py`
- Test file to be created/updated: `tests/test_TaskExample.py`

## Tasks for Copilot Agent
1. Analyze upstream `.adoc` fixtures in `asciidoctor-dita-vale/fixtures/TaskExample/` to determine expected output.
2. Create a `.expected` file in `./tests/fixtures/TaskExample/` for each upstream fixture, matching the expected output.
3. Implement the `TaskExample` plugin in `plugins/TaskExample.py` following the conventions used in `ContentType.py` and `EntityReference.py`.
4. Add or update `tests/test_TaskExample.py` to use the new fixtures and ensure coverage of plugin logic and CLI integration.
5. Use `unittest` and the shared testkit for fixture-based testing.
6. Ensure the plugin is auto-discovered by the CLI and appears in `asciidoc-dita --list-plugins`.
7. Confirm all tests pass locally and in CI.
8. Request review from @jhradilek for validation of `.expected` files and implementation.
9. Address all review comments and update files as needed.
10. Update README.md if new options or usage are introduced.

## Definition of Done
- [ ] A pull request adds a `.expected` file for each upstream fixture in `./tests/fixtures/TaskExample/`.
- [ ] Each `.expected` file accurately reflects the expected output for its matching `.adoc` fixture.
- [ ] The `TaskExample` plugin is implemented in `plugins/TaskExample.py` and follows project conventions.
- [ ] The test file `tests/test_TaskExample.py` uses the new fixtures and covers plugin and CLI behavior.
- [ ] All tests pass locally and in CI.
- [ ] The plugin is auto-discovered by the CLI.
- [ ] The pull request requests review from @jhradilek and addresses all feedback.
- [ ] Documentation is updated if needed.

---
*This issue is formatted for GitHub Copilot Agent Mode. Use `@agent` to get AI assistance with implementation.*
