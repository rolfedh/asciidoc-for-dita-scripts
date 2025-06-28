"""
Test suite for the EntityReference plugin.
"""
import unittest
import os

from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import replace_entities
from .asciidoc_testkit import get_fixture_path


class TestEntityReference(unittest.TestCase):
    def run_fixture_test(self, fixture_basename):
        """
        Helper to run a test for a given fixture.
        Skips the test if the .expected file is not found.
        """
        # Correctly construct the full path to the fixture files
        input_path = get_fixture_path(os.path.join("EntityReference", fixture_basename + ".adoc"))
        expected_path = get_fixture_path(os.path.join("EntityReference", fixture_basename + ".expected"))

        if not os.path.exists(expected_path):
            self.skipTest(f"Expected output file not found: {os.path.basename(expected_path)}")

        with open(input_path, "r", encoding="utf-8") as f:
            input_content = f.read()

        with open(expected_path, "r", encoding="utf-8") as f:
            expected_content = f.read()

        # Process the file content line by line, as the original test did.
        output_lines = [replace_entities(line) for line in input_content.splitlines(True)]
        actual_content = "".join(output_lines)

        self.assertEqual(actual_content, expected_content)

    def test_report_entity_references(self):
        self.run_fixture_test("report_entity_references")

    def test_report_multiple_references(self):
        self.run_fixture_test("report_multiple_references")

    def test_ignore_comments(self):
        self.run_fixture_test("ignore_comments")

    def test_ignore_numeric_references(self):
        self.run_fixture_test("ignore_numeric_references")

    def test_ignore_supported_entities(self):
        self.run_fixture_test("ignore_supported_entities")


if __name__ == "__main__":
    unittest.main()
