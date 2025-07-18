#!/usr/bin/env python3
"""Debug code block detection."""

import sys
from pathlib import Path
sys.path.insert(0, '.')

from asciidoc_dita_toolkit.asciidoc_dita.plugins.ExampleBlock import ExampleBlockDetector

content = Path('tests/fixtures/ExampleBlock/ignore_code_blocks.adoc').read_text()
detector = ExampleBlockDetector()
lines = content.split('\n')

print("=== DEBUGGING CODE BLOCK DETECTION ===")
for i, line in enumerate(lines):
    if '====' in line or '[example]' in line:
        print(f"Line {i}: {repr(line)}")
        is_in_code = detector._is_in_code_block_or_comment(lines, i)
        print(f"  Is in code block: {is_in_code}")
        
        # Manual check - count delimiters
        print("  Manual delimiter count:")
        for delimiter in ['----', '....', '```']:
            count = 0
            for j in range(i):
                if lines[j].strip() == delimiter:
                    count += 1
            print(f"    {delimiter}: {count} ({'inside' if count % 2 == 1 else 'outside'})")
        print()
