#!/usr/bin/env python3
"""Test what the plugin actually does with report files."""

import sys
from pathlib import Path

sys.path.insert(0, '.')

from asciidoc_dita_toolkit.asciidoc_dita.plugins.ExampleBlock import (
    ExampleBlockDetector,
    ExampleBlockProcessor,
)


def test_file(filename):
    print(f"\n=== Testing {filename} ===")
    content = Path(f'tests/fixtures/ExampleBlock/{filename}').read_text()

    # Show original content
    print("Original content:")
    print(content)
    print("-" * 50)

    # Show detected blocks
    detector = ExampleBlockDetector()
    blocks = detector.find_example_blocks(content)
    print(f"Detected {len(blocks)} blocks:")
    for i, block in enumerate(blocks):
        print(
            f"  Block {i}: {block['type']} at lines {block['start_line']}-{block['end_line']}"
        )

    # Show plugin output
    processor = ExampleBlockProcessor(detector, interactive=False)
    modified_content, issues = processor.process_content(content)
    print("\nPlugin output:")
    print(modified_content)
    print("-" * 50)

    print(f"Issues reported: {len(issues)}")
    for issue in issues:
        print(f"  - {issue}")


# Test the three report files
test_file('report_example_in_section.adoc')
test_file('report_example_in_list.adoc')
test_file('report_example_in_block.adoc')
