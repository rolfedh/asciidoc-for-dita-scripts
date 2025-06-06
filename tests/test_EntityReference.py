"""
Test suite for the EntityReference plugin.

This script tests the entity replacement logic using fixtures from
asciidoctor-dita-vale/fixtures/EntityReference/.

For each .adoc file, it expects a corresponding .expected file with the same basename.

To run: python3 tests/test_EntityReference.py

Recommended: Integrate this script into CI to catch regressions.
"""
import os
import sys
import difflib
import unittest

from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import replace_entities
from asciidoc_testkit import get_fixture_pairs, run_linewise_test

FIXTURE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../asciidoctor-dita-vale/fixtures/EntityReference'))


class TestEntityReference(unittest.TestCase):
    def test_basic_entity(self):
        self.assertEqual(replace_entities("A &hellip; B"), "A {hellip} B")
    # TODO: Add more test methods for edge cases, comments, warnings, etc.


def main():
    any_failed = False
    for input_path, expected_path in get_fixture_pairs(FIXTURE_DIR):
        if not run_linewise_test(input_path, expected_path, replace_entities):
            any_failed = True
    if any_failed:
        print("\nSome tests failed.")
        sys.exit(1)
    else:
        print("All EntityReference tests passed.")

if __name__ == "__main__":
    unittest.main()
