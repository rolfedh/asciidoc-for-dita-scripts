"""
Test suite for the EntityReference plugin.

This script tests the entity replacement logic using fixtures from
tests/fixtures/EntityReference/.

For each .adoc file, it expects a corresponding .expected file in the same directory.

To run: python3 tests/test_EntityReference.py

Recommended: Integrate this script into CI to catch regressions.
"""

import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import (
    process_file, replace_entities)
from tests.asciidoc_testkit import (get_same_dir_fixture_pairs,
                                    run_file_based_test, run_linewise_test)

FIXTURE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fixtures", "EntityReference")
)


class TestEntityReference(unittest.TestCase):
    """Test cases for the EntityReference plugin."""

    def test_basic_entity_replacement(self):
        """Test basic entity replacement functionality."""
        test_cases = [
            ("A &hellip; B", "A {hellip} B"),
            ("Copyright &copy; 2024", "Copyright {copy} 2024"),
            ("&mdash; em dash", "{mdash} em dash"),
            ("&ndash; en dash", "{ndash} en dash"),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = replace_entities(input_text)
                self.assertEqual(result, expected)

    def test_supported_entities_unchanged(self):
        """Test that supported XML entities are not replaced."""
        supported_cases = [
            "This &amp; that",
            "Less than &lt; symbol",
            "Greater than &gt; symbol",
            "Quote &quot; mark",
            "Apostrophe &apos; mark",
        ]

        for text in supported_cases:
            with self.subTest(text=text):
                result = replace_entities(text)
                self.assertEqual(result, text)

    def test_unknown_entity_warning(self):
        """Test that unknown entities generate warnings but remain unchanged."""
        with patch("builtins.print") as mock_print:
            result = replace_entities("Unknown &unknown; entity")
            mock_print.assert_called_with("Warning: No AsciiDoc attribute for &unknown;")
            self.assertEqual(result, "Unknown &unknown; entity")

    def test_multiple_entities_in_line(self):
        """Test handling of multiple entities in a single line."""
        input_text = "Test &copy; and &trade; symbols"
        expected = "Test {copy} and {trade} symbols"
        result = replace_entities(input_text)
        self.assertEqual(result, expected)

    def test_mixed_supported_and_unsupported(self):
        """Test lines with both supported and unsupported entities."""
        input_text = "Mix &amp; match &copy; symbols"
        expected = "Mix &amp; match {copy} symbols"
        result = replace_entities(input_text)
        self.assertEqual(result, expected)

    def test_no_entities(self):
        """Test that lines without entities are unchanged."""
        text = "Plain text with no entities"
        result = replace_entities(text)
        self.assertEqual(result, text)

    def test_fixture_based_tests(self):
        """Run tests based on fixture files if they exist."""
        if os.path.exists(FIXTURE_DIR):
            fixture_count = 0
            for input_path, expected_path in get_same_dir_fixture_pairs(FIXTURE_DIR):
                fixture_count += 1
                with self.subTest(fixture=os.path.basename(input_path)):
                    # Use file-based test for fixtures that contain comments
                    # (ignore_* fixtures need comment handling)
                    fixture_name = os.path.basename(input_path)
                    if fixture_name.startswith("ignore_"):
                        success = run_file_based_test(input_path, expected_path, process_file)
                    else:
                        success = run_linewise_test(input_path, expected_path, replace_entities)
                    self.assertTrue(success, f"Fixture test failed for {input_path}")

            if fixture_count > 0:
                print(f"Ran {fixture_count} fixture-based tests")
        else:
            self.skipTest(f"Fixture directory not found: {FIXTURE_DIR}")


def main():
    """Run tests with optional fixture-based testing."""
    # First run unit tests
    unittest.main(verbosity=2, exit=False)

    # Then run fixture-based tests if available
    if os.path.exists(FIXTURE_DIR):
        print("\nRunning fixture-based tests...")
        any_failed = False
        test_count = 0

        for input_path, expected_path in get_same_dir_fixture_pairs(FIXTURE_DIR):
            test_count += 1
            if not run_linewise_test(input_path, expected_path, replace_entities):
                any_failed = True

        if test_count == 0:
            print("No fixture files found.")
        elif any_failed:
            print(f"\nSome fixture tests failed out of {test_count} tests.")
            sys.exit(1)
        else:
            print(f"All {test_count} EntityReference fixture tests passed.")
    else:
        print(f"Fixture directory not found: {FIXTURE_DIR}")
        print("Skipping fixture-based tests.")


if __name__ == "__main__":
    main()
