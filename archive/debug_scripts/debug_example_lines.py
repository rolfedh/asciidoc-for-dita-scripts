#!/usr/bin/env python3
"""Debug the actual [example] lines that are being processed."""

import sys
from pathlib import Path

sys.path.insert(0, '.')

from asciidoc_dita_toolkit.asciidoc_dita.plugins.ExampleBlock import (
    ExampleBlockDetector,
)

content = Path('tests/fixtures/ExampleBlock/ignore_code_blocks.adoc').read_text()
lines = content.split('\n')

detector = ExampleBlockDetector()

# Check the actual [example] lines that are being processed
print("Checking line 6 ([example] that should be ignored):")
print(f"Line 6: {repr(lines[5])}")  # line 6 is index 5
print(f"Is in code block: {detector._is_in_code_block_or_comment(lines, 5)}")

print("\nChecking line 19 ([example] that should be ignored):")
print(f"Line 19: {repr(lines[18])}")  # line 19 is index 18
print(f"Is in code block: {detector._is_in_code_block_or_comment(lines, 18)}")

print("\nShowing context around line 6:")
for i in range(max(0, 5 - 2), min(len(lines), 5 + 3)):
    marker = " -> " if i == 5 else "    "
    print(f"{marker}{i+1}: {repr(lines[i])}")

print("\nShowing context around line 19:")
for i in range(max(0, 18 - 2), min(len(lines), 18 + 3)):
    marker = " -> " if i == 18 else "    "
    print(f"{marker}{i+1}: {repr(lines[i])}")
