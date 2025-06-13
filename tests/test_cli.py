"""
CLI-based tests for the AsciiDoc DITA Toolkit

Tests the unified CLI interface and plugin execution through subprocess calls.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestCLIInterface(unittest.TestCase):
    """Test the main CLI interface functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def run_cli(self, args, cwd=None, input_data=None):
        """Helper to run CLI commands and capture output."""
        cmd = [sys.executable, "-m", "asciidoc_dita_toolkit.asciidoc_dita.cli"] + args
        
        # Set up environment to include project root in PYTHONPATH
        env = os.environ.copy()
        project_root = Path(__file__).parent.parent
        current_pythonpath = env.get('PYTHONPATH', '')
        if current_pythonpath:
            env['PYTHONPATH'] = f"{project_root}:{current_pythonpath}"
        else:
            env['PYTHONPATH'] = str(project_root)
        
        result = subprocess.run(
            cmd,
            cwd=cwd or self.test_dir,
            capture_output=True,
            text=True,
            input=input_data,
            env=env,
        )
        return result

    def test_cli_help(self):
        """Test that CLI shows help when no arguments provided."""
        result = self.run_cli([])
        self.assertEqual(result.returncode, 0)
        self.assertIn("AsciiDoc DITA Toolkit", result.stdout)
        self.assertIn("usage:", result.stdout)

    def test_cli_version(self):
        """Test CLI version display."""
        result = self.run_cli(["--version"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("1.0.0", result.stdout)

    def test_list_plugins(self):
        """Test plugin listing functionality."""
        result = self.run_cli(["--list-plugins"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Available plugins:", result.stdout)
        self.assertIn("EntityReference", result.stdout)
        self.assertIn("ContentType", result.stdout)

    def test_plugin_help(self):
        """Test plugin-specific help."""
        result = self.run_cli(["EntityReference", "--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("EntityReference", result.stdout)
        self.assertIn("--recursive", result.stdout)
        self.assertIn("--file", result.stdout)


class TestEntityReferencePlugin(unittest.TestCase):
    """Test EntityReference plugin through CLI."""

    def setUp(self):
        """Set up test environment with sample files."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

        # Create test file with entity references
        self.test_file = Path(self.test_dir) / "test.adoc"
        self.test_file.write_text(
            """= Test Document

This has an &mdash; entity reference.
Also has &copy; and &trade; entities.
"""
        )

    def run_cli(self, args, cwd=None):
        """Helper to run CLI commands."""
        cmd = [sys.executable, "-m", "asciidoc_dita_toolkit.asciidoc_dita.cli"] + args
        
        # Set up environment to include project root in PYTHONPATH
        env = os.environ.copy()
        project_root = Path(__file__).parent.parent
        current_pythonpath = env.get('PYTHONPATH', '')
        if current_pythonpath:
            env['PYTHONPATH'] = f"{project_root}:{current_pythonpath}"
        else:
            env['PYTHONPATH'] = str(project_root)
        
        result = subprocess.run(
            cmd, cwd=cwd or self.test_dir, capture_output=True, text=True, env=env
        )
        return result

    def test_entity_reference_file_processing(self):
        """Test EntityReference plugin on a specific file."""
        result = self.run_cli(["EntityReference", "-f", str(self.test_file)])
        self.assertEqual(result.returncode, 0)

        # Check that entities were replaced
        content = self.test_file.read_text()
        self.assertIn("{mdash}", content)
        self.assertIn("{copy}", content)
        self.assertIn("{trade}", content)
        self.assertNotIn("&mdash;", content)
        self.assertNotIn("&copy;", content)
        self.assertNotIn("&trade;", content)

    def test_entity_reference_nonexistent_file(self):
        """Test EntityReference plugin with nonexistent file."""
        result = self.run_cli(["EntityReference", "-f", "nonexistent.adoc"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not exist", result.stderr)

    def test_entity_reference_non_adoc_file(self):
        """Test EntityReference plugin with non-AsciiDoc file."""
        txt_file = Path(self.test_dir) / "test.txt"
        txt_file.write_text("Some text")

        result = self.run_cli(["EntityReference", "-f", str(txt_file)])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not an AsciiDoc file", result.stderr)


class TestContentTypePlugin(unittest.TestCase):
    """Test ContentType plugin through CLI."""

    def setUp(self):
        """Set up test environment with sample files."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

        # Create test files with different naming patterns
        files = {
            "proc_example.adoc": "= Procedure Example\n\nSome content.",
            "con_example.adoc": "= Concept Example\n\nSome content.",
            "ref_example.adoc": "= Reference Example\n\nSome content.",
            "assembly_example.adoc": "= Assembly Example\n\nSome content.",
            "regular_file.adoc": "= Regular File\n\nSome content.",
        }

        for filename, content in files.items():
            (Path(self.test_dir) / filename).write_text(content)

    def run_cli(self, args, cwd=None):
        """Helper to run CLI commands."""
        cmd = [sys.executable, "-m", "asciidoc_dita_toolkit.asciidoc_dita.cli"] + args
        
        # Set up environment to include project root in PYTHONPATH
        env = os.environ.copy()
        project_root = Path(__file__).parent.parent
        current_pythonpath = env.get('PYTHONPATH', '')
        if current_pythonpath:
            env['PYTHONPATH'] = f"{project_root}:{current_pythonpath}"
        else:
            env['PYTHONPATH'] = str(project_root)
        
        result = subprocess.run(
            cmd, cwd=cwd or self.test_dir, capture_output=True, text=True, env=env
        )
        return result

    def test_content_type_directory_processing(self):
        """Test ContentType plugin on a directory."""
        result = self.run_cli(["ContentType", "-d", self.test_dir])
        self.assertEqual(result.returncode, 0)

        # Check that content type labels were added
        proc_content = (Path(self.test_dir) / "proc_example.adoc").read_text()
        self.assertIn(":_mod-docs-content-type: PROCEDURE", proc_content)

        con_content = (Path(self.test_dir) / "con_example.adoc").read_text()
        self.assertIn(":_mod-docs-content-type: CONCEPT", con_content)

        ref_content = (Path(self.test_dir) / "ref_example.adoc").read_text()
        self.assertIn(":_mod-docs-content-type: REFERENCE", ref_content)

        assembly_content = (Path(self.test_dir) / "assembly_example.adoc").read_text()
        self.assertIn(":_mod-docs-content-type: ASSEMBLY", assembly_content)

        # Regular file should not have been modified
        regular_content = (Path(self.test_dir) / "regular_file.adoc").read_text()
        self.assertNotIn(":_mod-docs-content-type:", regular_content)

    def test_content_type_nonexistent_directory(self):
        """Test ContentType plugin with nonexistent directory."""
        result = self.run_cli(["ContentType", "-d", "/nonexistent/directory"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not exist", result.stderr)


class TestStandalonePluginCommands(unittest.TestCase):
    """Test legacy standalone plugin functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def test_plugin_import_compatibility(self):
        """Test that plugins can still be imported directly for library usage."""
        try:
            from asciidoc_dita_toolkit.asciidoc_dita.plugins.ContentType import main as content_main
            from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import main as entity_main

            # If we get here without import errors, the plugins are still importable
            self.assertTrue(callable(entity_main))
            self.assertTrue(callable(content_main))
        except ImportError as e:
            self.fail(f"Plugin import failed: {e}")


if __name__ == "__main__":
    unittest.main()
