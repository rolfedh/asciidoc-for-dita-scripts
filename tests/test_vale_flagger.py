import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from asciidoc_dita_toolkit.plugins.vale_flagger import ValeFlagger


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

    def test_flag_insertion(self):
        """Test flag insertion into files."""
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


if __name__ == '__main__':
    unittest.main()
