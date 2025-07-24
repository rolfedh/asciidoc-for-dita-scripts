#!/usr/bin/env python3
"""Debug what blocks are actually found in code blocks file."""

import sys
from pathlib import Path

sys.path.insert(0, '.')

from asciidoc_dita_toolkit.modules.example_block import (
    ExampleBlockDetector,
)

content = Path('tests/fixtures/ExampleBlock/ignore_code_blocks.adoc').read_text()
detector = ExampleBlockDetector()
blocks = detector.find_example_blocks(content)

print(f"Found {len(blocks)} blocks in ignore_code_blocks.adoc")
for i, block in enumerate(blocks):
    print(
        f"Block {i}: {block['type']} at lines {block['start_line']}-{block['end_line']}"
    )
    print(f"Content: {repr(block['content'])}")
    print()
