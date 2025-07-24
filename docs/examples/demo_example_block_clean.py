#!/usr/bin/env python3
"""
Clean demo script showing ExampleBlock plugin functionality.
"""

from asciidoc_dita_toolkit.modules.example_block import (
    ExampleBlockProcessor,
    ExampleBlockDetector,
)
import pathlib


def demo_plugin():
    """Demonstrate ExampleBlock plugin on 2 test files."""

    # Initialize plugin
    detector = ExampleBlockDetector()
    processor = ExampleBlockProcessor(detector, interactive=False)

    # Test files
    test_files = [
        (
            'tests/fixtures/ExampleBlock/report_example_in_section.adoc',
            'Example in Section',
        ),
        ('tests/fixtures/ExampleBlock/report_example_in_list.adoc', 'Example in List'),
    ]

    for file_path, description in test_files:
        print(f"\n{'='*60}")
        print(f"TEST: {description}")
        print(f"File: {file_path}")
        print('=' * 60)

        # Read original content
        try:
            content = pathlib.Path(file_path).read_text()
            print("\nORIGINAL CONTENT:")
            print("-" * 40)
            print(content)

            # Process with plugin
            print("\nPROCESSING WITH EXAMPLEBLOCK PLUGIN...")
            result_content, violations = processor.process_content(content)

            print(f"\nVIOLATIONS DETECTED: {len(violations)}")
            for violation in violations:
                print(f"  • {violation}")

            print("\nPROCESSED CONTENT:")
            print("-" * 40)
            print(result_content)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        print(f"\n{'='*60}")


if __name__ == "__main__":
    demo_plugin()
