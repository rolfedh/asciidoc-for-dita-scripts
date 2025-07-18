# Archived Test Scripts

This directory contains test scripts that were moved from the project root during code cleanup.

## Files

- **test_example_block.py** - Basic ExampleBlock plugin test with fixture testing
- **test_interactive_flow.py** - Simple interactive flow test for ExampleBlock plugin

## Why Archived

These test files were archived rather than deleted because:

1. **test_example_block.py** - Redundant with the comprehensive fixture testing already available in `tests/fixtures/ExampleBlock/`
2. **test_interactive_flow.py** - Too simple (only 51 lines) to provide significant value

## Status

These files are functional but not actively maintained. The comprehensive test coverage for these features is provided by:

- **ExampleBlock testing**: `tests/fixtures/ExampleBlock/` (comprehensive fixture-based tests)
- **Advanced testing**: `tests/test_example_block_dual.py` (sophisticated dual testing strategy)

## Preservation Rationale

Kept for historical reference and potential future insights rather than deletion to preserve development effort and context.
