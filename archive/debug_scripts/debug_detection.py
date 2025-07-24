#!/usr/bin/env python3
"""Simple debug test for ExampleBlock detection."""

import sys
from pathlib import Path

sys.path.insert(0, '.')

try:
    from asciidoc_dita_toolkit.modules.example_block import (
        ExampleBlockDetector,
    )

    print("Import successful")

    # Test detection
    content = Path('tests/fixtures/ExampleBlock/ignore_admonitions.adoc').read_text()
    detector = ExampleBlockDetector()
    blocks = detector.find_example_blocks(content)
    print(f"Found {len(blocks)} blocks in ignore_admonitions.adoc")

    for i, block in enumerate(blocks):
        print(f"Block {i}: {block['content'][:50]}...")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
