#!/usr/bin/env python3
"""Test script for ExampleBlock plugin."""

import sys
from pathlib import Path
import tempfile
import shutil

# Add the package to Python path
package_root = Path(__file__).parent
sys.path.insert(0, str(package_root))

from asciidoc_dita_toolkit.modules.example_block import (
    ExampleBlockDetector,
    ExampleBlockProcessor,
    process_example_block_file,
)


def test_fixture(fixture_name: str):
    """Test a specific fixture."""
    fixture_dir = Path("tests/fixtures/ExampleBlock")

    adoc_file = fixture_dir / f"{fixture_name}.adoc"
    expected_file = fixture_dir / f"{fixture_name}.expected"

    if not adoc_file.exists():
        print(f"❌ Fixture not found: {adoc_file}")
        return False

    if not expected_file.exists():
        print(f"❌ Expected file not found: {expected_file}")
        return False

    # Read original content
    with open(adoc_file, 'r') as f:
        original_content = f.read()

    # Read expected content
    with open(expected_file, 'r') as f:
        expected_content = f.read()

    # Create temp file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as tmp:
        tmp.write(original_content)
        tmp_path = tmp.name

    try:
        # Process the file
        detector = ExampleBlockDetector()
        processor = ExampleBlockProcessor(detector, interactive=False)

        if fixture_name.startswith("ignore_"):
            # For ignore fixtures, content should remain unchanged
            success = process_example_block_file(tmp_path, processor)

            with open(tmp_path, 'r') as f:
                result_content = f.read()

            if result_content == original_content:
                print(f"✅ {fixture_name}: Correctly ignored")
                return True
            else:
                print(f"❌ {fixture_name}: Should have been ignored but was modified")
                return False

        else:
            # For report fixtures, content should match expected
            # Use non-interactive mode to add comments by default
            processor = ExampleBlockProcessor(detector, interactive=False)
            success = process_example_block_file(tmp_path, processor)

            with open(tmp_path, 'r') as f:
                result_content = f.read()

            if result_content.strip() == expected_content.strip():
                print(f"✅ {fixture_name}: Correctly processed")
                return True
            else:
                print(f"❌ {fixture_name}: Output doesn't match expected")
                print(f"Expected:\n{expected_content}")
                print(f"Got:\n{result_content}")
                return False

    finally:
        # Clean up temp file
        Path(tmp_path).unlink()


def main():
    """Run all fixture tests."""
    fixture_dir = Path("tests/fixtures/ExampleBlock")

    if not fixture_dir.exists():
        print(f"❌ Fixture directory not found: {fixture_dir}")
        return

    # Find all .adoc files
    adoc_files = list(fixture_dir.glob("*.adoc"))

    if not adoc_files:
        print(f"❌ No .adoc files found in {fixture_dir}")
        return

    print(f"Testing {len(adoc_files)} fixtures...")

    passed = 0
    failed = 0

    for adoc_file in sorted(adoc_files):
        fixture_name = adoc_file.stem
        if test_fixture(fixture_name):
            passed += 1
        else:
            failed += 1

    print(f"\n📊 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
