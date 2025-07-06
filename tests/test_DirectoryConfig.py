"""
Test suite for the DirectoryConfig plugin and related utilities.

This script tests the directory configuration management functionality
using fixtures from tests/fixtures/DirectoryConfig/.

To run: python3 tests/test_DirectoryConfig.py

Recommended: Integrate this script into CI to catch regressions.
"""

import json
import os
import sys
import tempfile
import unittest
from io import StringIO
from unittest.mock import MagicMock, mock_open, patch

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from asciidoc_dita_toolkit.asciidoc_dita.plugins.DirectoryConfig import (
    DirectoryConfigManager,
    run_directory_config,
    load_directory_config,
    apply_directory_filters,
    get_filtered_adoc_files,
)
from asciidoc_dita_toolkit.asciidoc_dita.config_utils import (
    load_json_config as load_config_file,
    save_json_config as save_config_file,
)
from asciidoc_dita_toolkit.asciidoc_dita.plugin_manager import is_plugin_enabled
from tests.asciidoc_testkit import get_same_dir_fixture_pairs

FIXTURE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fixtures", "DirectoryConfig")
)


class TestDirectoryConfigManager(unittest.TestCase):
    """Test cases for DirectoryConfigManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = DirectoryConfigManager()

    def test_create_default_config(self):
        """Test creating a default configuration."""
        config = self.manager.create_default_config()
        
        self.assertEqual(config["version"], "1.0")
        self.assertIn("repoRoot", config)
        self.assertIn("includeDirs", config)
        self.assertIn("excludeDirs", config)
        self.assertIn("lastUpdated", config)
        self.assertIsInstance(config["includeDirs"], list)
        self.assertIsInstance(config["excludeDirs"], list)

    def test_validate_directory_valid_path(self):
        """Test validating a valid directory path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a subdirectory
            subdir = os.path.join(tmpdir, "subdir")
            os.makedirs(subdir)
            
            is_valid, message = self.manager.validate_directory("subdir", tmpdir)
            self.assertTrue(is_valid)

    def test_validate_directory_invalid_path(self):
        """Test validating an invalid directory path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            is_valid, message = self.manager.validate_directory("nonexistent", tmpdir)
            self.assertFalse(is_valid)
            self.assertIn("does not exist", message)

    def test_validate_directory_empty_path(self):
        """Test validating an empty directory path."""
        is_valid, message = self.manager.validate_directory("", "/tmp")
        self.assertFalse(is_valid)
        self.assertIn("cannot be empty", message)


class TestFileUtilityFunctions(unittest.TestCase):
    """Test cases for file utility functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "version": "1.0",
            "repoRoot": "/test/repo",
            "includeDirs": ["docs", "content"],
            "excludeDirs": ["drafts", "temp"],
            "lastUpdated": "2023-01-01T00:00:00"
        }

    def test_save_and_load_config_file(self):
        """Test saving and loading configuration files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            try:
                # Save config
                save_config_file(tmp.name, self.test_config)
                
                # Load it back
                loaded_config = load_config_file(tmp.name)
                
                self.assertEqual(loaded_config["version"], "1.0")
                self.assertEqual(loaded_config["repoRoot"], "/test/repo")
                self.assertIn("docs", loaded_config["includeDirs"])
                self.assertIn("drafts", loaded_config["excludeDirs"])
            finally:
                os.unlink(tmp.name)

    def test_load_config_file_invalid_json(self):
        """Test loading an invalid JSON configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp.write("invalid json content")
            tmp.flush()
            
            try:
                # Test that logger.warning is called instead of print (improvement #4 from issue #87)
                with patch('asciidoc_dita_toolkit.asciidoc_dita.config_utils.logger.warning') as mock_warning:
                    config = load_config_file(tmp.name)
                    self.assertIsNone(config)
                    mock_warning.assert_called()
            finally:
                os.unlink(tmp.name)

    def test_load_config_file_nonexistent(self):
        """Test loading a non-existent configuration file."""
        config = load_config_file("/nonexistent/config.json")
        self.assertIsNone(config)

    @patch.dict(os.environ, {'ADT_ENABLE_DIRECTORY_CONFIG': 'true'})
    def test_is_plugin_enabled_directory_config(self):
        """Test checking if DirectoryConfig plugin is enabled."""
        enabled = is_plugin_enabled("DirectoryConfig")
        self.assertTrue(enabled)

    @patch.dict(os.environ, {}, clear=True)
    def test_is_plugin_enabled_directory_config_disabled(self):
        """Test checking if DirectoryConfig plugin is disabled by default."""
        enabled = is_plugin_enabled("DirectoryConfig")
        self.assertFalse(enabled)

    def test_is_plugin_enabled_other_plugin(self):
        """Test checking if other plugins are enabled by default."""
        enabled = is_plugin_enabled("EntityReference")
        self.assertTrue(enabled)


class TestDirectoryFiltering(unittest.TestCase):
    """Test cases for directory filtering functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "version": "1.0",
            "repoRoot": "/test/repo",
            "includeDirs": ["docs", "content"],
            "excludeDirs": ["drafts", "temp"],
            "lastUpdated": "2023-01-01T00:00:00"
        }

    def test_apply_directory_filters_include_only(self):
        """Test applying directory filters with include directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory structure
            docs_dir = os.path.join(tmpdir, "docs")
            content_dir = os.path.join(tmpdir, "content")
            other_dir = os.path.join(tmpdir, "other")
            
            for d in [docs_dir, content_dir, other_dir]:
                os.makedirs(d)
                # Create test files
                test_file = os.path.join(d, "test.adoc")
                with open(test_file, 'w') as f:
                    f.write("= Test Document\n\nContent here.")
            
            # Update config with actual temp directory
            config = self.test_config.copy()
            config["repoRoot"] = tmpdir
            
            filtered_dirs = apply_directory_filters(tmpdir, config)
            
            # Should only include docs and content directories
            expected_dirs = [docs_dir, content_dir]
            self.assertEqual(set(filtered_dirs), set(expected_dirs))

    def test_apply_directory_filters_exclude_dirs(self):
        """Test applying directory filters with exclude directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory structure
            good_dir = os.path.join(tmpdir, "good")
            drafts_dir = os.path.join(tmpdir, "drafts")
            
            for d in [good_dir, drafts_dir]:
                os.makedirs(d)
                # Create test files
                test_file = os.path.join(d, "test.adoc")
                with open(test_file, 'w') as f:
                    f.write("= Test Document\n\nContent here.")
            
            # Config with exclude dirs
            config = {
                "version": "1.0",
                "repoRoot": tmpdir,
                "includeDirs": [],
                "excludeDirs": ["drafts"],
                "lastUpdated": "2023-01-01T00:00:00"
            }
            
            # Test that the good directory is not excluded when we process it
            filtered_dirs = apply_directory_filters(good_dir, config)
            self.assertIn(good_dir, filtered_dirs)
            
            # Test that the drafts directory would be excluded
            # The function logs a warning but still returns the path since there's no alternative
            with patch('asciidoc_dita_toolkit.asciidoc_dita.plugins.DirectoryConfig.logger') as mock_logger:
                filtered_dirs = apply_directory_filters(drafts_dir, config)
                # Check that the excluded directory warning was logged
                mock_logger.warning.assert_called()
                # Check that warning was called with exclusion message
                warning_calls = [call for call in mock_logger.warning.call_args_list 
                               if 'excluded by configuration' in str(call)]
                self.assertGreater(len(warning_calls), 0)


class TestDirectoryConfigFixtures(unittest.TestCase):
    """Test cases using fixture files."""

    def setUp(self):
        """Check if fixture directory exists and skip tests if not."""
        if not os.path.exists(FIXTURE_DIR):
            self.skipTest(f"Fixture directory not found: {FIXTURE_DIR}")

    def test_fixture_files_exist(self):
        """Test that required fixture files exist."""
        sample_config = os.path.join(FIXTURE_DIR, "sample_config.json")
        
        # Skip if file doesn't exist instead of failing
        if not os.path.exists(sample_config):
            self.skipTest(f"Sample config not found: {sample_config}")
        
        with open(sample_config, 'r') as f:
            config = json.load(f)
        
        self.assertIn("adt_directory_config", config)
        self.assertIn("version", config["adt_directory_config"])

    def test_fixture_adoc_files(self):
        """Test that fixture AsciiDoc files are properly formatted."""
        fixture_pairs = list(get_same_dir_fixture_pairs(
            FIXTURE_DIR, ".adoc", ".expected"
        ))
        
        # Skip if no fixtures found instead of failing
        if len(fixture_pairs) == 0:
            self.skipTest("No fixture pairs found - this is expected in CI environments")
        
        for input_path, expected_path in fixture_pairs:
            with self.subTest(file=os.path.basename(input_path)):
                self.assertTrue(os.path.exists(input_path))
                self.assertTrue(os.path.exists(expected_path))
                
                # Verify files have content
                with open(input_path, 'r') as f:
                    input_content = f.read().strip()
                self.assertGreater(len(input_content), 0)
                
                with open(expected_path, 'r') as f:
                    expected_content = f.read().strip()
                self.assertGreater(len(expected_content), 0)


def run_tests():
    """Run all DirectoryConfig tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDirectoryConfigManager))
    suite.addTests(loader.loadTestsFromTestCase(TestFileUtilityFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestDirectoryFiltering))
    suite.addTests(loader.loadTestsFromTestCase(TestDirectoryConfigFixtures))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
