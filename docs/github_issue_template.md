## Title

Unify file search behavior across plugins: default to current directory, add `-r` for recursion, support `-d` for root directory

## Description

Currently, the `EntityReference` and `ContentType` plugins handle file scope and directory traversal inconsistently. One plugin defaults to searching only the current directory unless `-r` is specified, while the other always searches recursively. This inconsistency can confuse users and complicate documentation.

### Best Practice to Implement

- By default, plugins should process only `.adoc` files in the current directory (non-recursive).
- Add a `-r` or `--recursive` option to enable recursive search into subdirectories.
- Add a `-d DIR` or `--directory DIR` option to specify the root directory for the search (default: current directory).
- All plugins should use this consistent behavior and argument pattern.

### Tasks

- [ ] Refactor or expand the shared `file_utils.py` module to implement this logic.
- [ ] Update both `EntityReference` and `ContentType` plugins to use the shared logic for file discovery and argument parsing.
- [ ] Ensure help messages and documentation reflect the new, unified behavior.
- [ ] Add or update tests to verify correct file selection in all scenarios.

### Acceptance Criteria

- Both plugins accept `-r` and `-d` options and behave identically regarding file scope.
- By default, only the current directory is processed.
- Recursive search and custom root directory are supported via CLI options.
- Documentation and help output are clear and consistent.

**Assignee:**
Code with Copilot Agent Mode
