#!/usr/bin/env python3
"""Debug specific lines that are being detected as blocks."""

import sys
from pathlib import Path

sys.path.insert(0, '.')

from asciidoc_dita_toolkit.asciidoc_dita.plugins.ExampleBlock import (
    ExampleBlockDetector,
)

content = Path('tests/fixtures/ExampleBlock/ignore_code_blocks.adoc').read_text()
lines = content.split('\n')

detector = ExampleBlockDetector()

# Check the specific lines that are being detected as blocks
print("Checking line 5 (should be inside .... block):")
print(f"Line 5: {repr(lines[4])}")  # line 5 is index 4
print(f"Is in code block: {detector._is_in_code_block_or_comment(lines, 4)}")

print("\nChecking line 18 (should be inside ---- block):")
print(f"Line 18: {repr(lines[17])}")  # line 18 is index 17
print(f"Is in code block: {detector._is_in_code_block_or_comment(lines, 17)}")

print("\nShowing context around line 5:")
for i in range(max(0, 4 - 2), min(len(lines), 4 + 3)):
    marker = " -> " if i == 4 else "    "
    print(f"{marker}{i+1}: {repr(lines[i])}")

print("\nShowing context around line 18:")
for i in range(max(0, 17 - 2), min(len(lines), 17 + 3)):
    marker = " -> " if i == 17 else "    "
    print(f"{marker}{i+1}: {repr(lines[i])}")
