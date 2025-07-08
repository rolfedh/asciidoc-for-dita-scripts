"""
Test suite for the AttributeReference plugin.

This script tests the transformation logic using fixtures from
tests/fixtures/AttributeReference/.

For each .adoc file, it expects a corresponding .expected file in the same directory.
"""

import os
import sys
import unittest

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from asciidoc_dita_toolkit.asciidoc_dita.plugins.AttributeReference import transform_line, process_file
from tests.asciidoc_testkit import run_linewise_test, get_same_dir_fixture_pairs, run_file_based_test

FIXTURE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures', 'AttributeReference'))


class TestAttributeReference(unittest.TestCase):
    
    def test_basic_functionality(self):
        """Test basic transformation functionality."""
        # TODO: Add specific test cases
        input_text = "example input"
        expected = "example input"  # TODO: Update with expected output
        result = transform_line(input_text)
        self.assertEqual(result, expected)
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        # TODO: Add edge case tests
        pass
    
    def test_fixture_based_tests(self):
        """Run tests based on fixture files if they exist."""
        if os.path.exists(FIXTURE_DIR):
            fixture_count = 0
            for input_path, expected_path in get_same_dir_fixture_pairs(FIXTURE_DIR):
                fixture_count += 1
                with self.subTest(fixture=os.path.basename(input_path)):
                    fixture_name = os.path.basename(input_path)
                    
                    # TODO: Choose appropriate test method
                    # Use run_linewise_test for simple transformations
                    # Use run_file_based_test for state-dependent transformations
                    success = run_linewise_test(input_path, expected_path, transform_line)
                    self.assertTrue(success, f"Fixture test failed for {input_path}")
            
            if fixture_count > 0:
                print(f"Ran {fixture_count} fixture-based tests")
        else:
            self.skipTest(f"Fixture directory not found: {FIXTURE_DIR}")


if __name__ == '__main__':
    unittest.main()
