# ADT Plugin Examples

This directory contains example scripts demonstrating how to use the AsciiDoc DITA Toolkit (ADT) plugins.

## Files

- **demo_example_block.py** - Basic demonstration of ExampleBlock plugin usage
- **demo_example_block_clean.py** - Clean version of ExampleBlock plugin demonstration

## Purpose

These example scripts show:

- How to import and initialize ADT plugins
- Basic plugin configuration and usage patterns
- Simple file processing workflows
- Plugin output and result handling

## Usage

Run these scripts to see how the ExampleBlock plugin works:

```bash
# Basic demo
python docs/examples/demo_example_block.py

# Clean demo version
python docs/examples/demo_example_block_clean.py
```

{: .note }
**ValeFlagger Configuration Examples**: Configuration examples and usage guides are now included in the [user-guide documentation](../../user-guide/plugins/ValeFlagger.md#configuration-examples) for technical writers.
cp docs/examples/vscode-tasks.json .vscode/tasks.json

# Access via Command Palette: Ctrl+Shift+P -> "Tasks: Run Task"
```

## Learning Path

1. **Start here** - Use these demos to understand basic plugin usage
2. **Study the code** - See how plugins are initialized and configured
3. **Check test files** - Review `tests/` directory for comprehensive examples
4. **Read documentation** - See `docs/user-guide/` for detailed plugin documentation

## Integration

These examples can be:

- Modified for your specific use cases
- Used as templates for new plugin demonstrations
- Referenced in documentation and tutorials
- Extended with additional features and configurations

## Status

These examples are maintained as part of the documentation and are updated when plugin APIs change.
