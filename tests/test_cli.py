"""
Test suite for the CLI interface of the AsciiDoc DITA toolkit.
"""
import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from asciidoc_dita_toolkit.asciidoc_dita import toolkit


class TestCLI(unittest.TestCase):
    """Test cases for the CLI interface."""

    def test_discover_plugins(self):
        """Test that plugin discovery works correctly."""
        plugins = toolkit.discover_plugins()
        self.assertIsInstance(plugins, list)
        self.assertIn('EntityReference', plugins)
        self.assertIn('ContentType', plugins)

    @patch('sys.stdout', new_callable=StringIO)
    def test_list_plugins(self, mock_stdout):
        """Test the --list-plugins functionality."""
        toolkit.print_plugin_list()
        output = mock_stdout.getvalue()
        self.assertIn('Available plugins:', output)
        self.assertIn('EntityReference', output)
        self.assertIn('ContentType', output)

    @patch('sys.argv', ['toolkit', '--list-plugins'])
    @patch('sys.exit')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_list_plugins(self, mock_stdout, mock_exit):
        """Test main function with --list-plugins argument."""
        toolkit.main()
        mock_exit.assert_called_once_with(0)
        output = mock_stdout.getvalue()
        self.assertIn('Available plugins:', output)

    @patch('sys.argv', ['toolkit'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_no_args(self, mock_stdout):
        """Test main function with no arguments shows help."""
        toolkit.main()
        output = mock_stdout.getvalue()
        self.assertIn('usage:', output)

    def test_plugin_loading_with_missing_function(self):
        """Test handling of plugins missing register_subcommand function."""
        with patch('sys.argv', ['toolkit']), \
             patch('sys.stderr', new_callable=StringIO) as mock_stderr, \
             patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
             patch('asciidoc_dita_toolkit.asciidoc_dita.toolkit.discover_plugins') as mock_discover, \
             patch('importlib.import_module') as mock_import:
            
            mock_discover.return_value = ['test_plugin']
            mock_module = MagicMock()
            del mock_module.register_subcommand  # Remove the function
            mock_import.return_value = mock_module
            
            toolkit.main()
            error_output = mock_stderr.getvalue()
            self.assertIn("missing register_subcommand function", error_output)

    def test_plugin_loading_with_import_error(self):
        """Test handling of plugin import errors."""
        with patch('sys.argv', ['toolkit']), \
             patch('sys.stderr', new_callable=StringIO) as mock_stderr, \
             patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
             patch('asciidoc_dita_toolkit.asciidoc_dita.toolkit.discover_plugins') as mock_discover, \
             patch('importlib.import_module', side_effect=ImportError("Test import error")):
            
            mock_discover.return_value = ['broken_plugin']
            
            toolkit.main()
            error_output = mock_stderr.getvalue()
            self.assertIn("Error loading plugin", error_output)

    @patch('sys.argv', ['toolkit', 'EntityReference', '--help'])
    def test_plugin_help(self):
        """Test that plugin help works correctly."""

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with self.assertRaises(SystemExit) as cm:
                toolkit.main()
        # argparse exits with code 0 for --help
        self.assertEqual(cm.exception.code, 0)


class TestEntityReferencePlugin(unittest.TestCase):
    """Test cases for the EntityReference plugin."""

    def setUp(self):
        """Set up test fixtures."""
        from asciidoc_dita_toolkit.asciidoc_dita.plugins import EntityReference
        self.plugin = EntityReference

    def test_replace_entities_supported(self):
        """Test that supported entities are not replaced."""
        input_line = "This &amp; that &lt; other"
        result = self.plugin.replace_entities(input_line)
        self.assertEqual(result, input_line)

    def test_replace_entities_unsupported(self):
        """Test that unsupported entities are replaced."""
        input_line = "Copyright &copy; 2024"
        result = self.plugin.replace_entities(input_line)
        self.assertEqual(result, "Copyright {copy} 2024")

    def test_replace_entities_unknown(self):
        """Test handling of unknown entities."""
        input_line = "Unknown &unknown; entity"
        with patch('builtins.print') as mock_print:
            result = self.plugin.replace_entities(input_line)
            mock_print.assert_called_with("Warning: No AsciiDoc attribute for &unknown;")
            self.assertEqual(result, input_line)


class TestContentTypePlugin(unittest.TestCase):
    """Test cases for the ContentType plugin."""

    def setUp(self):
        """Set up test fixtures."""
        from asciidoc_dita_toolkit.asciidoc_dita.plugins import ContentType
        self.plugin = ContentType

    def test_get_content_type_from_filename(self):
        """Test content type detection from filename."""
        test_cases = [
            ('assembly_test.adoc', 'ASSEMBLY'),
            ('assembly-test.adoc', 'ASSEMBLY'),
            ('con_test.adoc', 'CONCEPT'),
            ('con-test.adoc', 'CONCEPT'),
            ('proc_test.adoc', 'PROCEDURE'),
            ('proc-test.adoc', 'PROCEDURE'),
            ('ref_test.adoc', 'REFERENCE'),
            ('ref-test.adoc', 'REFERENCE'),
            ('snip_test.adoc', 'SNIPPET'),
            ('snip-test.adoc', 'SNIPPET'),
            ('other_test.adoc', None),
        ]

        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.plugin.get_content_type_from_filename(filename)
                self.assertEqual(result, expected)

    def test_add_content_type_label_new_file(self):
        """Test adding content type label to a file without one."""
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.adoc', delete=False) as tmp:
            tmp.write("= Test Document\n\nContent here.\n")
            tmp.flush()
            
            try:
                with patch('builtins.print') as mock_print:
                    self.plugin.add_content_type_label(tmp.name, 'CONCEPT')
                
                with open(tmp.name, 'r') as f:
                    content = f.read()
                
                self.assertIn(':_mod-docs-content-type: CONCEPT', content)
                mock_print.assert_called()
            finally:
                os.unlink(tmp.name)

    def test_add_content_type_label_existing_label(self):
        """Test that existing labels are not overwritten."""
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.adoc', delete=False) as tmp:
            tmp.write(":_mod-docs-content-type: PROCEDURE\n= Test Document\n\nContent here.\n")
            tmp.flush()
            
            try:
                with patch('builtins.print') as mock_print:
                    self.plugin.add_content_type_label(tmp.name, 'CONCEPT')
                
                with open(tmp.name, 'r') as f:
                    content = f.read()
                
                # Should still have the original label
                self.assertIn(':_mod-docs-content-type: PROCEDURE', content)
                # Should not have the new label
                self.assertNotIn(':_mod-docs-content-type: CONCEPT', content)
                mock_print.assert_called_with(f"Skipping {tmp.name}, label already present")
            finally:
                os.unlink(tmp.name)


if __name__ == '__main__':
    unittest.main()
