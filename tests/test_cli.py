"""
Test suite for the CLI interface of the AsciiDoc DITA toolkit.
"""

import os
import re
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from asciidoc_dita_toolkit.asciidoc_dita import toolkit


class TestCLI(unittest.TestCase):
    """Test cases for the CLI interface."""

    def test_discover_plugins(self):
        """Test that plugin discovery works correctly."""
        plugins = toolkit.discover_plugins()
        self.assertIsInstance(plugins, list)
        self.assertGreater(len(plugins), 0, "Should discover at least one plugin")
        # Verify all discovered items are strings (plugin names)
        self.assertTrue(all(isinstance(plugin, str) for plugin in plugins))

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_plugins(self, mock_stdout):
        """Test the --list-plugins functionality."""
        toolkit.print_plugin_list()
        output = mock_stdout.getvalue()
        self.assertIn("Available plugins:", output)
        # Should list at least one plugin
        lines = output.strip().split('\n')
        self.assertGreater(len(lines), 1, "Should list at least the header and one plugin")

    @patch("sys.argv", ["toolkit", "--list-plugins"])
    @patch("sys.exit")
    @patch("sys.stdout", new_callable=StringIO)
    def test_main_list_plugins(self, mock_stdout, mock_exit):
        """Test main function with --list-plugins argument."""
        toolkit.main()
        mock_exit.assert_called_once_with(0)
        output = mock_stdout.getvalue()
        self.assertIn("Available plugins:", output)

    @patch("sys.argv", ["toolkit"])
    @patch("sys.stdout", new_callable=StringIO)
    def test_main_no_args(self, mock_stdout):
        """Test main function with no arguments shows help."""
        toolkit.main()
        output = mock_stdout.getvalue()
        self.assertIn("usage:", output)

    def test_plugin_loading_with_missing_function(self):
        """Test handling of plugins missing register_subcommand function."""
        with patch("sys.argv", ["toolkit"]), patch(
            "sys.stderr", new_callable=StringIO
        ) as mock_stderr, patch("sys.stdout", new_callable=StringIO) as mock_stdout, patch(
            "asciidoc_dita_toolkit.asciidoc_dita.toolkit.discover_plugins"
        ) as mock_discover, patch(
            "importlib.import_module"
        ) as mock_import:

            mock_discover.return_value = ["test_plugin"]
            mock_module = MagicMock()
            del mock_module.register_subcommand  # Remove the function
            mock_import.return_value = mock_module

            toolkit.main()
            error_output = mock_stderr.getvalue()
            self.assertIn("missing register_subcommand function", error_output)

    def test_plugin_loading_with_import_error(self):
        """Test handling of plugin import errors."""
        with patch("sys.argv", ["toolkit"]), patch(
            "sys.stderr", new_callable=StringIO
        ) as mock_stderr, patch("sys.stdout", new_callable=StringIO) as mock_stdout, patch(
            "asciidoc_dita_toolkit.asciidoc_dita.toolkit.discover_plugins"
        ) as mock_discover, patch(
            "importlib.import_module", side_effect=ImportError("Test import error")
        ):

            mock_discover.return_value = ["broken_plugin"]

            toolkit.main()
            error_output = mock_stderr.getvalue()
            self.assertIn("Error loading plugin", error_output)

    def test_plugin_help(self):
        """Test that plugin help works correctly."""
        # Get available plugins from the CLI help output dynamically
        with patch("sys.argv", ["toolkit", "--help"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                try:
                    toolkit.main()
                except SystemExit:
                    pass  # argparse calls sys.exit after showing help
        
        help_output = mock_stdout.getvalue()
        
        # Extract available subcommands from help output using regex
        # Look for the subcommands section in argparse help output
        subcommand_match = re.search(r'\{([^}]+)\}', help_output)
        if not subcommand_match:
            self.skipTest("No subcommands found in CLI help to test help functionality")
        
        # Parse available plugins from the subcommands list
        available_plugins = [plugin.strip() for plugin in subcommand_match.group(1).split(',')]
        
        if not available_plugins:
            self.skipTest("No plugins available in CLI to test help functionality")
        
        # Test with the first available plugin
        test_plugin = available_plugins[0]
        with patch("sys.argv", ["toolkit", test_plugin, "--help"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    toolkit.main()
        # argparse exits with code 0 for --help
        self.assertEqual(cm.exception.code, 0)

    @patch("sys.argv", ["toolkit", "--invalid-option"])
    @patch("sys.stderr", new_callable=StringIO)
    def test_invalid_option_handling(self, mock_stderr):
        """Test handling of invalid command line options."""
        with self.assertRaises(SystemExit) as cm:
            toolkit.main()
        # argparse exits with code 2 for invalid arguments
        self.assertEqual(cm.exception.code, 2)
        error_output = mock_stderr.getvalue()
        self.assertIn("unrecognized arguments", error_output)

    @patch("sys.argv", ["toolkit", "NonExistentPlugin"])
    @patch("sys.stderr", new_callable=StringIO)
    def test_nonexistent_plugin_handling(self, mock_stderr):
        """Test handling of requests for non-existent plugins."""
        with self.assertRaises(SystemExit) as cm:
            toolkit.main()
        # Should exit with error code for invalid subcommand
        self.assertNotEqual(cm.exception.code, 0)

    def test_plugin_discovery_empty_directory(self):
        """Test plugin discovery when plugins directory is empty."""
        with patch("os.listdir", return_value=[]):
            plugins = toolkit.discover_plugins()
            self.assertEqual(plugins, [])


if __name__ == "__main__":
    unittest.main()
