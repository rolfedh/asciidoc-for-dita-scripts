"""
Test suite for the fix_entity_references plugin.

This script tests the entity replacement logic using fixtures from
asciidoctor-dita-vale/fixtures/EntityReference/.

For each .adoc file, it expects a corresponding .expected file with the same basename.

To run: python3 tests/test_fix_entity_references.py

Recommended: Integrate this script into CI to catch regressions.
"""
import os
import sys
import difflib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../asciidoc-dita-toolkit/plugins')))

from fix_entity_references import replace_entities
from asciidoc_testkit import get_fixture_pairs, run_linewise_test

FIXTURE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../asciidoctor-dita-vale/fixtures/EntityReference'))


def main():
    any_failed = False
    for input_path, expected_path in get_fixture_pairs(FIXTURE_DIR):
        if not run_linewise_test(input_path, expected_path, replace_entities):
            any_failed = True
    if any_failed:
        print("\nSome tests failed.")
        sys.exit(1)
    else:
        print("All fix_entity_references tests passed.")

if __name__ == "__main__":
    main()
