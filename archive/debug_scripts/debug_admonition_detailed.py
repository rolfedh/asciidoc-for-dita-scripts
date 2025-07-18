#!/usr/bin/env python3
"""Debug admonition detection in detail."""

import sys
import re
from pathlib import Path
sys.path.insert(0, '.')

from asciidoc_dita_toolkit.asciidoc_dita.plugins.ExampleBlock import ExampleBlockDetector

def debug_admonition_detection():
    content = Path('tests/fixtures/ExampleBlock/ignore_admonitions.adoc').read_text()
    detector = ExampleBlockDetector()
    lines = content.split('\n')
    
    print("=== DEBUGGING ADMONITION DETECTION ===\n")
    
    # Find all ==== blocks
    for i, line in enumerate(lines):
        if line.strip() == '====':
            print(f"Found ==== at line {i}")
            print("Context around block:")
            for j in range(max(0, i-5), min(len(lines), i+3)):
                marker = '>>>' if j == i else '   '
                print(f"{marker} {j:2d}: {repr(lines[j])}")
            
            # Test the admonition detection
            is_admonition = detector._is_admonition_block(lines, i)
            print(f"Is admonition: {is_admonition}")
            
            # Manual check - look backwards for admonition markers
            print("Manual scan backwards:")
            for k in range(i - 1, max(0, i - 10), -1):
                check_line = lines[k].strip()
                print(f"  Line {k}: {repr(check_line)}")
                if re.match(r'^\[(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', check_line):
                    print(f"    ✓ Found admonition marker!")
                    break
                elif check_line != '' and not check_line.startswith('.') and check_line != '+':
                    print(f"    ✗ Stopped at non-empty line")
                    break
            
            print("-" * 50)

if __name__ == "__main__":
    debug_admonition_detection()
