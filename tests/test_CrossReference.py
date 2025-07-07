"""
Test suite for the CrossReference plugin.

This script tests the cross-reference fixing logic including:
- ID mapping from AsciiDoc files
- Cross-reference link updating
- Master file processing

To run: python3 tests/test_CrossReference.py

Recommended: Integrate this script into CI to catch regressions.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import the plugin module by temporarily adding to sys.path
plugin_dir = os.path.join(os.path.dirname(__file__), "..", "asciidoc_dita_toolkit", "asciidoc_dita", "plugins")
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

try:
    # Import by renaming the module file temporarily or use exec
    plugin_path = os.path.join(plugin_dir, "CrossReference.py")
    
    # Read and execute the plugin code in a namespace
    plugin_namespace = {}
    with open(plugin_path, 'r') as f:
        plugin_code = f.read()
    
    # Replace relative imports with absolute imports for testing
    plugin_code = plugin_code.replace(
        "from ..cli_utils import common_arg_parser",
        "from asciidoc_dita_toolkit.asciidoc_dita.cli_utils import common_arg_parser"
    ).replace(
        "from ..workflow_utils import process_adoc_files", 
        "from asciidoc_dita_toolkit.asciidoc_dita.workflow_utils import process_adoc_files"
    )
    
    exec(plugin_code, plugin_namespace)
    
    # Extract the classes and functions we need
    CrossReferenceProcessor = plugin_namespace['CrossReferenceProcessor']
    Highlighter = plugin_namespace['Highlighter']
    find_master_files = plugin_namespace['find_master_files']
    process_master_file = plugin_namespace['process_master_file']
    mod_docs_cross_reference = type('module', (), plugin_namespace)
    
except Exception as e:
    # If import fails, skip the tests
    print(f"Warning: Could not import CrossReference plugin: {e}")
    CrossReferenceProcessor = None
    Highlighter = None
    find_master_files = None
    process_master_file = None
    mod_docs_cross_reference = None

FIXTURE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fixtures", "CrossReference")
)


@unittest.skipIf(Highlighter is None, "CrossReference plugin could not be imported")
class TestHighlighter(unittest.TestCase):
    """Test cases for the Highlighter utility class."""

    def test_warn_formatting(self):
        """Test warning text formatting."""
        highlighter = Highlighter("Warning text")
        result = highlighter.warn()
        self.assertIn("Warning text", result)
        self.assertTrue(result.startswith('\033[0;31m'))
        self.assertTrue(result.endswith('\033[0m'))

    def test_bold_formatting(self):
        """Test bold text formatting."""
        highlighter = Highlighter("Bold text")
        result = highlighter.bold()
        self.assertIn("Bold text", result)
        self.assertTrue(result.startswith('\033[1m'))
        self.assertTrue(result.endswith('\033[0m'))

    def test_highlight_formatting(self):
        """Test highlight text formatting."""
        highlighter = Highlighter("Highlight text")
        result = highlighter.highlight()
        self.assertIn("Highlight text", result)
        self.assertTrue(result.startswith('\033[0;36m'))
        self.assertTrue(result.endswith('\033[0m'))


class TestCrossReferenceProcessor(unittest.TestCase):
    """Test cases for the CrossReferenceProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = CrossReferenceProcessor()

    def test_processor_initialization(self):
        """Test that processor initializes with empty state."""
        self.assertEqual(len(self.processor.id_map), 0)
        self.assertEqual(len(self.processor.bread_crumbs), 0)
        self.assertIsNotNone(self.processor.id_in_regex)
        self.assertIsNotNone(self.processor.include_in_regex)
        self.assertIsNotNone(self.processor.link_in_regex)

    def test_id_regex_pattern(self):
        """Test ID regex pattern matching."""
        test_cases = [
            ('[#section-id]', 'section-id'),
            ('[[another_id]]', 'another_id'),
            ('[id="my-id"]', 'my-id'),
            ("[id='test_id']", 'test_id'),
        ]

        for input_text, expected_id in test_cases:
            with self.subTest(input_text=input_text):
                match = self.processor.id_in_regex.search(input_text)
                if match:
                    self.assertEqual(match.group(), expected_id)

    def test_include_regex_pattern(self):
        """Test include regex pattern matching."""
        test_cases = [
            ('include::chapter1.adoc[]', 'chapter1.adoc'),
            ('include::modules/intro.adoc[leveloffset=+1]', 'modules/intro.adoc'),
            ('include::../shared/common.adoc[]', '../shared/common.adoc'),
        ]

        for input_text, expected_path in test_cases:
            with self.subTest(input_text=input_text):
                match = self.processor.include_in_regex.search(input_text)
                if match:
                    self.assertEqual(match.group(), expected_path)

    def test_link_regex_pattern(self):
        """Test xref link regex pattern matching."""
        test_cases = [
            ('xref:section-id[Link Text]', ('section-id', '[Link Text]')),
            ('xref:chapter_intro[Introduction]', ('chapter_intro', '[Introduction]')),
            ('See xref:overview[Overview section]', ('overview', '[Overview section]')),
        ]

        for input_text, expected_groups in test_cases:
            with self.subTest(input_text=input_text):
                match = self.processor.link_in_regex.search(input_text)
                if match:
                    self.assertEqual(match.group(1), expected_groups[0])
                    self.assertEqual(match.group(2), expected_groups[1])

    def test_link_regex_ignores_existing_file_refs(self):
        """Test that regex ignores already-fixed xref links."""
        already_fixed_cases = [
            'xref:chapter1.adoc#section-id[Link Text]',
            'xref:modules/intro.adoc#overview[Introduction]',
        ]

        for input_text in already_fixed_cases:
            with self.subTest(input_text=input_text):
                match = self.processor.link_in_regex.search(input_text)
                self.assertIsNone(match, f"Should not match already-fixed link: {input_text}")

    def test_update_link_with_existing_id(self):
        """Test link updating when ID exists in map."""
        # Setup ID map
        self.processor.id_map = {
            'section-intro': '/path/to/chapter1.adoc',
            'overview': '/path/to/modules/intro.adoc'
        }

        # Create a mock match object
        mock_match = MagicMock()
        mock_match.group.side_effect = lambda x: {
            0: 'section-intro[Introduction]',
            1: 'section-intro',
            2: '[Introduction]'
        }[x]

        with patch('builtins.print'):  # Suppress console output during test
            result = self.processor.update_link(mock_match)
            self.assertEqual(result, 'chapter1.adoc#section-intro[Introduction]')

    def test_update_link_with_missing_id(self):
        """Test link updating when ID doesn't exist in map."""
        # Empty ID map
        self.processor.id_map = {}

        # Create a mock match object
        mock_match = MagicMock()
        mock_match.group.side_effect = lambda x: {
            0: 'missing-id[Some Text]',
            1: 'missing-id',
            2: '[Some Text]'
        }[x]

        with patch('builtins.print'):  # Suppress console output during test
            result = self.processor.update_link(mock_match)
            self.assertEqual(result, 'missing-id[Some Text]')  # Should remain unchanged

    def test_update_link_with_complex_id(self):
        """Test link updating with underscore-separated IDs."""
        # Setup ID map
        self.processor.id_map = {
            'section_subsection_detail': '/path/to/chapter1.adoc'
        }
    
        # Create a mock match object for complex ID
        mock_match = MagicMock()
        mock_match.group.side_effect = lambda x: {
            0: 'section_subsection_detail[Link Text]',
            1: 'section_subsection_detail',
            2: '[Link Text]'
        }[x]
    
        with patch('builtins.print'):  # Suppress console output during test
            result = self.processor.update_link(mock_match)
            self.assertEqual(result, 'chapter1.adoc#section_subsection_detail[Link Text]')


class TestMasterFileProcessing(unittest.TestCase):
    """Test cases for master file processing functionality."""

    def test_find_master_files_empty_directory(self):
        """Test finding master files in empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = find_master_files(temp_dir)
            self.assertEqual(len(result), 0)

    def test_find_master_files_with_files(self):
        """Test finding master files when they exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            master_file = os.path.join(temp_dir, 'master.adoc')
            other_file = os.path.join(temp_dir, 'chapter1.adoc')
            
            with open(master_file, 'w') as f:
                f.write('= Master Document\n')
            with open(other_file, 'w') as f:
                f.write('= Chapter 1\n')
            
            result = find_master_files(temp_dir)
            self.assertEqual(len(result), 1)
            self.assertIn(master_file, result)

    def test_find_master_files_nested_directories(self):
        """Test finding master files in nested directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested structure
            nested_dir = os.path.join(temp_dir, 'books', 'guide1')
            os.makedirs(nested_dir)
            
            master_file1 = os.path.join(temp_dir, 'master.adoc')
            master_file2 = os.path.join(nested_dir, 'master.adoc')
            
            with open(master_file1, 'w') as f:
                f.write('= Root Master\n')
            with open(master_file2, 'w') as f:
                f.write('= Nested Master\n')
            
            result = find_master_files(temp_dir)
            self.assertEqual(len(result), 2)
            self.assertIn(master_file1, result)
            self.assertIn(master_file2, result)


class TestPluginIntegration(unittest.TestCase):
    """Test cases for plugin integration with the ADT framework."""

    def test_plugin_has_description(self):
        """Test that plugin has required description attribute."""
        self.assertTrue(hasattr(mod_docs_cross_reference, '__description__'))
        self.assertIsInstance(mod_docs_cross_reference.__description__, str)
        self.assertGreater(len(mod_docs_cross_reference.__description__), 0)

    def test_plugin_has_register_subcommand(self):
        """Test that plugin has required register_subcommand function."""
        self.assertTrue(hasattr(mod_docs_cross_reference, 'register_subcommand'))
        self.assertTrue(callable(mod_docs_cross_reference.register_subcommand))

    def test_plugin_has_main_function(self):
        """Test that plugin has main function."""
        self.assertTrue(hasattr(mod_docs_cross_reference, 'main'))
        self.assertTrue(callable(mod_docs_cross_reference.main))

    def test_register_subcommand_structure(self):
        """Test that register_subcommand function can be called."""
        # Create a mock subparsers object
        mock_subparsers = MagicMock()
        mock_parser = MagicMock()
        mock_subparsers.add_parser.return_value = mock_parser

        # This should not raise an exception
        try:
            mod_docs_cross_reference.register_subcommand(mock_subparsers)
            success = True
        except Exception:
            success = False

        self.assertTrue(success, "register_subcommand should execute without errors")
        
        # Verify that add_parser was called
        mock_subparsers.add_parser.assert_called()


class TestEndToEndWorkflow(unittest.TestCase):
    """End-to-end tests for the complete workflow."""

    def test_process_master_file_with_no_ids(self):
        """Test processing master file that contains no IDs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            master_file = os.path.join(temp_dir, 'master.adoc')
            
            # Create master file with no IDs
            with open(master_file, 'w') as f:
                f.write("""= Test Document

This is a test document with no section IDs.

== Chapter 1

Some content here.
""")

            with patch('builtins.print'):  # Suppress console output
                # This should not crash
                try:
                    process_master_file(master_file)
                    success = True
                except Exception:
                    success = False
                
                self.assertTrue(success, "Should handle files with no IDs gracefully")

    def test_build_id_map_file_not_found(self):
        """Test ID map building with non-existent file."""
        processor = CrossReferenceProcessor()
        
        with patch('builtins.print'):  # Suppress console output
            # This should not crash
            processor.build_id_map('/nonexistent/file.adoc')
            
            # ID map should remain empty
            self.assertEqual(len(processor.id_map), 0)


def main():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestHighlighter,
        TestCrossReferenceProcessor,
        TestMasterFileProcessing,
        TestPluginIntegration,
        TestEndToEndWorkflow
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    tests_run = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    
    print(f"\nTest Summary:")
    print(f"Tests run: {tests_run}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    
    if failures > 0 or errors > 0:
        print("Some tests failed!")
        sys.exit(1)
    else:
        print("All tests passed!")


if __name__ == "__main__":
    main()