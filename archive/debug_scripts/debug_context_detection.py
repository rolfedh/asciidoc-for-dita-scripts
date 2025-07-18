#!/usr/bin/env python3
"""Debug why blocks in lists/blocks aren't detected as violations."""

import sys
from pathlib import Path
sys.path.insert(0, '.')

from asciidoc_dita_toolkit.asciidoc_dita.plugins.ExampleBlock import ExampleBlockDetector

def debug_block_context(filename, expected_violations):
    print(f"\n=== Debugging {filename} ===")
    content = Path(f'tests/fixtures/ExampleBlock/{filename}').read_text()
    lines = content.split('\n')
    
    detector = ExampleBlockDetector()
    blocks = detector.find_example_blocks(content)
    
    print(f"Expected {expected_violations} violations, found {len(blocks)} blocks")
    
    for i, block in enumerate(blocks):
        print(f"\nBlock {i}:")
        print(f"  Type: {block['type']}")
        print(f"  Lines: {block['start_line']}-{block['end_line']}")
        print(f"  Content: {repr(block['content'][:50])}")
        
        # Check what the plugin thinks about this block's context
        print(f"  Context checks:")
        print(f"    Is in main body: {detector.is_in_main_body(block, content)}")
        print(f"    Is in list: {detector.is_in_list(block, content)}")
        print(f"    Is in block: {detector.is_in_block(block, content)}")

# Test the problematic files
debug_block_context('report_example_in_list.adoc', 3)
debug_block_context('report_example_in_block.adoc', 2)
