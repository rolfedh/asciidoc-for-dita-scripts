"""
Test suite for the CLI functionality.

Basic tests to ensure the command-line interface works correctly.
"""
import unittest
import sys
import os
from unittest.mock import patch
from io import StringIO

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from asciidoc_dita_toolkit.asciidoc_dita import toolkit


class TestCLI(unittest.TestCase):
    """Test cases for command-line interface."""
    
    def test_list_plugins_option(self):
        """Test that --list-plugins works without error."""
        with patch('sys.argv', ['toolkit', '--list-plugins']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                with patch('sys.exit') as mock_exit:
                    toolkit.main()
                    mock_exit.assert_called_once_with(0)
                    output = mock_stdout.getvalue()
                    self.assertIn('Available plugins:', output)
    
    def test_help_message(self):
        """Test that help message is displayed when no arguments given."""
        with patch('sys.argv', ['toolkit']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                toolkit.main()
                output = mock_stdout.getvalue()
                self.assertIn('AsciiDoc DITA Toolkit', output)
    
    def test_plugin_discovery(self):
        """Test that plugin discovery works."""
        plugins = toolkit.discover_plugins()
        self.assertIsInstance(plugins, list)
        # We should have at least ContentType and EntityReference plugins
        plugin_names = set(plugins)
        expected_plugins = {'ContentType', 'EntityReference'}
        self.assertTrue(expected_plugins.issubset(plugin_names), 
                       f"Expected plugins {expected_plugins} not found in {plugin_names}")


if __name__ == "__main__":
    unittest.main()