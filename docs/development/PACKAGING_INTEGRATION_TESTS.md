# Packaging Integration Tests

## Overview

The packaging integration tests in `tests/test_packaging_integration.py` provide comprehensive coverage for packaging and distribution issues that unit tests cannot catch. These tests were created in response to the v2.0.11 packaging failure where the `modules/` directory was not included in the wheel distribution.

## Why These Tests Are Needed

Unit tests run against source code, but users install packages from wheels distributed via PyPI. This creates a gap where:

1. **All unit tests can pass** while using source code imports
2. **The packaged distribution can be broken** due to missing files
3. **Users get "No module named 'modules'" errors** after installing via pip

The v2.0.11 bug exemplified this perfectly - all 334 unit tests passed, but the package was broken for end users.

## Test Coverage

### 1. `test_wheel_contains_required_modules`
- Verifies that both `asciidoc_dita_toolkit/` and `modules/` directories are present in the wheel
- Checks for specific critical files that were missing in v2.0.11
- Validates top-level directory structure

### 2. `test_entry_points_defined_correctly`
- Ensures all CLI scripts (adt, adg, valeflag) are properly defined
- Verifies plugin entry points are present in wheel metadata
- Catches missing or malformed entry point configurations

### 3. `test_fresh_install_and_import`
- **Most Important Test**: Installs the wheel in a clean virtual environment
- Tests actual import statements that would fail for end users
- Specifically tests `from modules.entity_reference import EntityReferenceModule`
- This test would have caught the v2.0.11 bug immediately

### 4. `test_cli_commands_accessible`
- Verifies that CLI commands can be executed after installation
- Ensures commands don't crash with module import errors
- Tests the complete installation → execution workflow

### 5. `test_plugin_discovery_works`
- Tests that plugin entry points can be discovered and loaded
- Uses modern `importlib.metadata` instead of deprecated `pkg_resources`
- Verifies the plugin architecture works in packaged form

### 6. `test_version_consistency`
- Ensures version is consistent between `pyproject.toml` and wheel metadata
- Catches version mismatch issues

### 7. `test_packaging_config_includes_modules`
- **Configuration Guard**: Explicitly checks that `pyproject.toml` includes "modules*"
- Prevents accidental removal of the fix
- Fast test that catches configuration regressions immediately

## Running the Tests

```bash
# Run all packaging integration tests
python3 -m pytest tests/test_packaging_integration.py -v

# Run only integration tests (includes packaging tests)
python3 -m pytest -m integration

# Run only slow tests (packaging tests take time due to wheel building)
python3 -m pytest -m slow

# Skip slow tests for faster development
python3 -m pytest -m "not slow"
```

## Test Execution Time

These tests are marked as `@pytest.mark.slow` because they:
- Build wheels (5-10 seconds each)
- Create virtual environments (5-10 seconds each)
- Install packages in clean environments (5-15 seconds each)

Total runtime: ~45-50 seconds for the full suite.

## When to Run These Tests

### Always Run
- Before any release (especially patch releases)
- After modifying `pyproject.toml`
- When changing package structure or imports

### Consider Running
- After significant refactoring
- When adding new CLI commands or plugins
- Before merging packaging-related PRs

### CI Integration
These tests should be part of the release pipeline but can be optional for development builds due to their execution time.

## Historical Context

The v2.0.11 incident taught us that:

1. **Unit test coverage ≠ packaging coverage**
2. **setuptools behavior can be non-obvious** (automatic package discovery vs explicit inclusion)
3. **Dual architecture creates complexity** (top-level `modules/` + `asciidoc_dita_toolkit/` structure)
4. **Integration testing is essential** for user-facing functionality

These tests ensure we never ship a broken package again.

## Future Improvements

Potential enhancements to consider:

1. **Matrix testing**: Test across Python versions and operating systems
2. **Performance testing**: Measure wheel size and import times
3. **Dependency testing**: Verify all dependencies are correctly specified
4. **Uninstall testing**: Ensure clean uninstallation
5. **Upgrade testing**: Test package upgrades don't break existing installations

## Technical Notes

### Virtual Environment Strategy
Tests create isolated virtual environments to ensure clean testing conditions. This prevents interference from development dependencies or source code.

### Modern Python Compatibility
The plugin discovery test uses `importlib.metadata` (Python 3.8+) with fallback to `importlib_metadata` for older versions, avoiding deprecated `pkg_resources`.

### Wheel Building
Tests use the standard `python3 -m build` approach rather than setuptools directly, matching real-world distribution workflows.
