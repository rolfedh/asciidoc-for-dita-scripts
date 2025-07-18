#!/usr/bin/env python3
"""Test the interactive flow of the ExampleBlock plugin."""

import sys
from pathlib import Path

sys.path.insert(0, '.')

from asciidoc_dita_toolkit.asciidoc_dita.plugins.ExampleBlock import (
    ExampleBlockDetector,
    ExampleBlockProcessor,
)


def test_interactive_flow():
    content = """// Test file with example blocks in various locations
== Section title

[example]
An example in a section.

* List item
+
====
An example in a list.
====

****
An example in a block.
====
Example content
====
****
"""

    detector = ExampleBlockDetector()
    processor = ExampleBlockProcessor(detector, interactive=True)

    print("Testing interactive flow...")
    print("Original content:")
    print(content)
    print("=" * 50)

    modified_content, issues = processor.process_content(content)

    print("\nModified content:")
    print(modified_content)
    print("=" * 50)

    print(f"\nIssues found: {len(issues)}")
    for issue in issues:
        print(f"  - {issue}")


if __name__ == "__main__":
    test_interactive_flow()
