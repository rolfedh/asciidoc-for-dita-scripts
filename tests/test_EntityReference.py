"""
Test suite for the EntityReference plugin.

This script tests the entity replacement logic using fixtures from
asciidoctor-dita-vale/fixtures/EntityReference/.

For each .adoc file, it expects a corresponding .expected file with the same basename.

To run: python3 -m pytest tests/test_EntityReference.py
Or: python3 tests/test_EntityReference.py

Recommended: Integrate this script into CI to catch regressions.
"""
import os
import sys
import unittest

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import replace_entities
from asciidoc_testkit import get_fixture_path, get_fixture_pairs, run_linewise_test


class TestEntityReference(unittest.TestCase):
    """Test cases for the EntityReference plugin."""
    
    def test_basic_entity_replacement(self):
        """Test basic entity replacement functionality."""
        self.assertEqual(replace_entities("A &hellip; B"), "A {hellip} B")
        self.assertEqual(replace_entities("&copy; 2023"), "{copy} 2023")
        self.assertEqual(replace_entities("&mdash;"), "{mdash}")
    
    def test_supported_entities_unchanged(self):
        """Test that supported XML entities are not changed."""
        self.assertEqual(replace_entities("&amp; &lt; &gt;"), "&amp; &lt; &gt;")
        self.assertEqual(replace_entities("&apos; &quot;"), "&apos; &quot;")
    
    def test_unknown_entities_unchanged(self):
        """Test that unknown entities trigger warnings but remain unchanged."""
        # This should print a warning but return the original
        result = replace_entities("&unknownentity;")
        self.assertEqual(result, "&unknownentity;")
    
    def test_fixture_based_tests(self):
        """Run tests based on fixture files."""
        fixture_dir = get_fixture_path("EntityReference")
        
        if not os.path.isdir(fixture_dir):
            self.skipTest(f"Fixture directory not found: {fixture_dir}")
        
        any_tests_run = False
        any_failed = False
        
        for input_path, expected_path in get_fixture_pairs(fixture_dir, warn_missing=False):
            any_tests_run = True
            with self.subTest(fixture=os.path.basename(input_path)):
                success = run_linewise_test(input_path, expected_path, replace_entities)
                if not success:
                    any_failed = True
        
        if not any_tests_run:
            self.skipTest("No fixture files found for testing")
        
        self.assertFalse(any_failed, "Some fixture-based tests failed")


def main():
    """Main function for running tests when called as a script."""
    # Run fixture-based tests in addition to unittest
    fixture_dir = get_fixture_path("EntityReference")
    
    if os.path.isdir(fixture_dir):
        print("Running fixture-based tests...")
        any_failed = False
        any_tests_run = False
        
        for input_path, expected_path in get_fixture_pairs(fixture_dir):
            any_tests_run = True
            if not run_linewise_test(input_path, expected_path, replace_entities):
                any_failed = True
        
        if any_tests_run:
            if any_failed:
                print("\nSome fixture tests failed.")
            else:
                print("All fixture-based EntityReference tests passed.")
        else:
            print("No fixture files found for testing.")
    else:
        print(f"Fixture directory not found: {fixture_dir}")
    
    # Run unittest tests
    print("\nRunning unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    main()
