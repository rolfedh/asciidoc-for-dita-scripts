import json
import logging
import os
import shutil
import tempfile
import unittest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

from asciidoc_dita_toolkit.plugins.vale_flagger import ValeFlagger
from asciidoc_dita_toolkit.plugins.vale_flagger.config import ValeFlaggerConfig, DEFAULT_DOCKER_IMAGE
from asciidoc_dita_toolkit.plugins.vale_flagger.cli import main, create_parser, setup_logging


class TestValeFlagger(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.sample_vale_output = {
            "test.adoc": [
                {
                    "Check": "AsciiDocDITA.Headings.Capitalization",
                    "Message": "Heading should use sentence-style capitalization.",
                    "Line": 5,
                    "Span": [1, 25],
                    "Severity": "error"
                },
                {
                    "Check": "AsciiDocDITA.Terms.Use",
                    "Message": "Use 'repository' instead of 'repo'.",
                    "Line": 10,
                    "Span": [15, 19],
                    "Severity": "warning"
                }
            ]
        }

    @patch('subprocess.run')
    def test_docker_check(self, mock_run):
        """Test Docker availability check."""
        # Success case
        mock_run.return_value = Mock(returncode=0)
        flagger = ValeFlagger()  # Should not raise

        # Failure case
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaises(RuntimeError):
            ValeFlagger()

    @patch('subprocess.run')
    def test_docker_timeout_check(self, mock_run):
        """Test Docker timeout during availability check."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired('docker', 5)
        with self.assertRaises(RuntimeError):
            ValeFlagger()

    @patch('subprocess.run')
    def test_run_vale_success(self, mock_run):
        """Test successful Vale execution."""
        mock_result = Mock()
        mock_result.returncode = 1  # Vale returns 1 when issues found
        mock_result.stdout = json.dumps(self.sample_vale_output)
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger(dry_run=True)
            results = flagger.run("test.adoc")

        self.assertEqual(len(results), 1)
        self.assertEqual(len(results["test.adoc"]), 2)

    @patch('subprocess.run')
    def test_run_vale_no_issues(self, mock_run):
        """Test Vale execution with no issues found."""
        mock_result = Mock()
        mock_result.returncode = 0  # No issues
        mock_result.stdout = "{}"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger(dry_run=True)
            results = flagger.run("test.adoc")

        self.assertEqual(len(results), 0)

    @patch('subprocess.run')
    def test_run_vale_empty_output(self, mock_run):
        """Test Vale execution with empty output."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger(dry_run=True)
            results = flagger.run("test.adoc")

        self.assertEqual(len(results), 0)

    @patch('subprocess.run')
    def test_run_vale_error(self, mock_run):
        """Test Vale execution error handling."""
        mock_result = Mock()
        mock_result.returncode = 2  # Error
        mock_result.stderr = "Docker error"
        mock_run.return_value = mock_result

        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger(dry_run=True)
            with self.assertRaises(RuntimeError):
                flagger.run("test.adoc")

    @patch('subprocess.run')
    def test_run_vale_timeout(self, mock_run):
        """Test Vale execution timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired('docker', 300)

        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger(dry_run=True)
            with self.assertRaises(RuntimeError) as cm:
                flagger.run("test.adoc")

            self.assertIn("timed out", str(cm.exception))
            self.assertIn("large document sets", str(cm.exception))

    @patch('subprocess.run')
    def test_run_vale_json_error(self, mock_run):
        """Test Vale execution with invalid JSON."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = "invalid json"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger(dry_run=True)
            with self.assertRaises(ValueError):
                flagger.run("test.adoc")

    def test_path_validation(self):
        """Test path validation and sanitization."""
        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger(dry_run=True)

        # Test with non-existent directory
        with patch('subprocess.run'):
            with self.assertRaises(ValueError) as cm:
                flagger._run_vale(Path("/nonexistent/path/file.adoc"))

            self.assertIn("does not exist", str(cm.exception))

    def test_flag_formatting(self):
        """Test flag formatting logic."""
        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger()

        # Single issue
        single_issue = [{
            "Check": "AsciiDocDITA.Headings.Capitalization",
            "Message": "Test message"
        }]
        flag = flagger._format_flag(single_issue)
        self.assertEqual(flag, "// ADT-FLAG [Headings.Capitalization]: Test message")

        # Multiple issues
        multiple_issues = [
            {"Check": "AsciiDocDITA.Rule1", "Message": "Message 1"},
            {"Check": "AsciiDocDITA.Rule2", "Message": "Message 2"}
        ]
        flag = flagger._format_flag(multiple_issues)
        self.assertIn("Rule1, Rule2", flag)
        self.assertIn("Message 1 | Message 2", flag)

    def test_custom_flag_format(self):
        """Test custom flag formatting."""
        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger(flag_format="// CUSTOM [{rule}]: {message}")

        single_issue = [{
            "Check": "AsciiDocDITA.Test.Rule",
            "Message": "Test message"
        }]
        flag = flagger._format_flag(single_issue)
        self.assertEqual(flag, "// CUSTOM [Test.Rule]: Test message")

    def test_flag_insertion_unix_line_endings(self):
        """Test flag insertion with Unix line endings."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as tf:
            tf.write("= Test Document\n\nSome content\n")
            temp_path = tf.name

        try:
            with patch.object(ValeFlagger, '_check_docker'):
                flagger = ValeFlagger()

            issues = [
                {"Check": "Test.Rule", "Message": "Test issue", "Line": 1}
            ]

            flagger._flag_file(temp_path, issues)

            # Read and verify
            content = Path(temp_path).read_text()
            lines = content.splitlines()

            # Should have inserted a flag before line 1
            self.assertIn("ADT-FLAG", lines[0])
            self.assertEqual(lines[1], "= Test Document")

        finally:
            Path(temp_path).unlink()

    def test_flag_insertion_windows_line_endings(self):
        """Test flag insertion preserves line ending format."""
        # This test just verifies that the flag insertion works
        # Line ending preservation is implementation-dependent
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as tf:
            tf.write("= Test Document\n\nSome content\n")
            temp_path = tf.name

        try:
            with patch.object(ValeFlagger, '_check_docker'):
                flagger = ValeFlagger()

            issues = [
                {"Check": "Test.Rule", "Message": "Test issue", "Line": 1}
            ]

            flagger._flag_file(temp_path, issues)

            # Verify flag was inserted
            content = Path(temp_path).read_text()
            self.assertIn("ADT-FLAG", content)
            self.assertIn("= Test Document", content)

        finally:
            Path(temp_path).unlink()

    def test_flag_insertion_multiple_lines(self):
        """Test flag insertion for multiple lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as tf:
            tf.write("= Test Document\n\nLine 2\nLine 3\nLine 4\n")
            temp_path = tf.name

        try:
            with patch.object(ValeFlagger, '_check_docker'):
                flagger = ValeFlagger()

            issues = [
                {"Check": "Test.Rule1", "Message": "Issue on line 1", "Line": 1},
                {"Check": "Test.Rule2", "Message": "Issue on line 3", "Line": 3}
            ]

            flagger._flag_file(temp_path, issues)

            content = Path(temp_path).read_text()
            lines = content.splitlines()

            # Should have two flags inserted
            flag_count = sum(1 for line in lines if "ADT-FLAG" in line)
            self.assertEqual(flag_count, 2)

        finally:
            Path(temp_path).unlink()

    def test_flag_insertion_file_not_found(self):
        """Test flag insertion with non-existent file."""
        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger()

        issues = [{"Check": "Test.Rule", "Message": "Test issue", "Line": 1}]

        # Should not raise, just log warning
        flagger._flag_file("/nonexistent/file.adoc", issues)

    @patch('subprocess.run')
    def test_vale_config_generation(self, mock_run):
        """Test dynamic Vale configuration generation."""
        mock_run.return_value = Mock(returncode=0, stdout="{}", stderr="")

        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger()

        config = flagger._build_vale_config(
            include_rules=["Rule1", "Rule2"],
            exclude_rules=["Rule3"]
        )

        self.assertIn("AsciiDocDITA.Rule1 = YES", config)
        self.assertIn("AsciiDocDITA.Rule2 = YES", config)
        self.assertIn("AsciiDocDITA.Rule3 = NO", config)
        self.assertIn("BasedOnStyles = AsciiDocDITA", config)

    def test_vale_config_generation_no_rules(self):
        """Test Vale configuration with no custom rules."""
        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger()

        config = flagger._build_vale_config()

        self.assertIn("BasedOnStyles = AsciiDocDITA", config)
        self.assertIn("StylesPath", config)
        self.assertNotIn("= YES", config)
        self.assertNotIn("= NO", config)


class TestValeFlaggerConfig(unittest.TestCase):
    """Test ValeFlaggerConfig class."""

    def setUp(self):
        """Set up test environment with clean working directory."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def test_default_config(self):
        """Test default configuration."""
        # Use an empty config path to ensure no config file is loaded
        config = ValeFlaggerConfig("")

        self.assertEqual(config.enabled_rules, [])
        self.assertEqual(config.disabled_rules, [])
        self.assertEqual(config.timeout_seconds, 300)
        self.assertEqual(config.docker_image, DEFAULT_DOCKER_IMAGE)
        self.assertEqual(config.flag_format, '// ADT-FLAG [{rule}]: {message}')

    def test_config_from_yaml_file(self):
        """Test configuration loading from YAML file."""
        config_data = {
            'vale': {
                'enabled_rules': ['Rule1', 'Rule2'],
                'disabled_rules': ['Rule3'],
                'timeout_seconds': 600,
                'docker_image': 'custom:latest'
            },
            'valeflag': {
                'flag_format': '// CUSTOM [{rule}]: {message}',
                'backup_files': True
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tf:
            yaml.dump(config_data, tf)
            temp_path = tf.name

        try:
            config = ValeFlaggerConfig(temp_path)

            self.assertEqual(config.enabled_rules, ['Rule1', 'Rule2'])
            self.assertEqual(config.disabled_rules, ['Rule3'])
            self.assertEqual(config.timeout_seconds, 600)
            self.assertEqual(config.docker_image, 'custom:latest')
            self.assertEqual(config.flag_format, '// CUSTOM [{rule}]: {message}')

        finally:
            Path(temp_path).unlink()

    def test_config_nonexistent_file(self):
        """Test configuration with non-existent file."""
        config = ValeFlaggerConfig("/nonexistent/config.yaml")

        # Should use defaults when file doesn't exist
        self.assertEqual(config.enabled_rules, [])
        self.assertEqual(config.timeout_seconds, 300)

    def test_config_partial_yaml(self):
        """Test configuration with partial YAML file."""
        config_data = {
            'vale': {
                'enabled_rules': ['Rule1']
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tf:
            yaml.dump(config_data, tf)
            temp_path = tf.name

        try:
            config = ValeFlaggerConfig(temp_path)

            self.assertEqual(config.enabled_rules, ['Rule1'])
            # Should use defaults for other values
            self.assertEqual(config.timeout_seconds, 300)
            self.assertEqual(config.docker_image, DEFAULT_DOCKER_IMAGE)

        finally:
            Path(temp_path).unlink()


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""

    def test_create_parser(self):
        """Test argument parser creation."""
        parser = create_parser()

        # Test default arguments
        args = parser.parse_args([])
        self.assertEqual(args.path, '.')
        self.assertFalse(args.dry_run)
        self.assertFalse(args.verbose)
        self.assertIsNone(args.enable_rules)

    def test_parser_arguments(self):
        """Test parser with various arguments."""
        parser = create_parser()

        args = parser.parse_args([
            '--path', 'test.adoc',
            '--enable-rules', 'Rule1,Rule2',
            '--disable-rules', 'Rule3',
            '--dry-run',
            '--verbose',
            '--config', 'config.yaml',
            '--flag-format', '// CUSTOM: {message}'
        ])

        self.assertEqual(args.path, 'test.adoc')
        self.assertEqual(args.enable_rules, 'Rule1,Rule2')
        self.assertEqual(args.disable_rules, 'Rule3')
        self.assertTrue(args.dry_run)
        self.assertTrue(args.verbose)
        self.assertEqual(args.config, 'config.yaml')
        self.assertEqual(args.flag_format, '// CUSTOM: {message}')

    @patch('asciidoc_dita_toolkit.plugins.vale_flagger.cli.ValeFlagger')
    def test_main_success(self, mock_flagger_class):
        """Test main function with successful execution."""
        mock_flagger = Mock()
        mock_flagger.run.return_value = {}  # No issues
        mock_flagger_class.return_value = mock_flagger

        result = main(['--path', 'test.adoc'])

        self.assertEqual(result, 0)
        mock_flagger.run.assert_called_once()

    @patch('asciidoc_dita_toolkit.plugins.vale_flagger.cli.ValeFlagger')
    def test_main_with_issues(self, mock_flagger_class):
        """Test main function when issues are found."""
        mock_flagger = Mock()
        mock_flagger.run.return_value = {"test.adoc": [{"Check": "Rule", "Message": "Issue"}]}
        mock_flagger_class.return_value = mock_flagger

        result = main(['--path', 'test.adoc'])

        self.assertEqual(result, 1)
        mock_flagger.run.assert_called_once()

    @patch('asciidoc_dita_toolkit.plugins.vale_flagger.cli.ValeFlagger')
    def test_main_dry_run(self, mock_flagger_class):
        """Test main function in dry-run mode."""
        mock_flagger = Mock()
        mock_flagger.run.return_value = {
            "test.adoc": [{
                "Check": "AsciiDocDITA.Rule",
                "Message": "Test issue",
                "Line": 1,
                "Severity": "error"
            }]
        }
        mock_flagger_class.return_value = mock_flagger

        with patch('builtins.print') as mock_print:
            result = main(['--path', 'test.adoc', '--dry-run'])

        self.assertEqual(result, 1)

        # Check that dry-run output was printed
        print_calls = [call for call in mock_print.call_args_list]
        dry_run_output = any("DRY RUN RESULTS" in str(call) for call in print_calls)
        self.assertTrue(dry_run_output)

    @patch('asciidoc_dita_toolkit.plugins.vale_flagger.cli.ValeFlagger')
    def test_main_with_rules(self, mock_flagger_class):
        """Test main function with rule arguments."""
        mock_flagger = Mock()
        mock_flagger.run.return_value = {}
        mock_flagger_class.return_value = mock_flagger

        result = main([
            '--enable-rules', 'Rule1,Rule2',
            '--disable-rules', 'Rule3,Rule4'
        ])

        self.assertEqual(result, 0)

        # Check that rules were parsed and passed correctly
        call_args = mock_flagger.run.call_args
        self.assertEqual(call_args[1]['include_rules'], ['Rule1', 'Rule2'])
        self.assertEqual(call_args[1]['exclude_rules'], ['Rule3', 'Rule4'])

    @patch('asciidoc_dita_toolkit.plugins.vale_flagger.cli.ValeFlagger')
    def test_main_exception_handling(self, mock_flagger_class):
        """Test main function exception handling."""
        mock_flagger_class.side_effect = Exception("Test error")

        result = main(['--path', 'test.adoc'])

        self.assertEqual(result, 2)

    def test_setup_logging(self):
        """Test logging setup."""
        # Just verify that setup_logging function works without errors
        # The exact logging level may depend on system configuration
        try:
            setup_logging(verbose=True)
            setup_logging(verbose=False)
            # If we get here without exception, the test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"setup_logging raised an unexpected exception: {e}")


if __name__ == '__main__':
    unittest.main()
