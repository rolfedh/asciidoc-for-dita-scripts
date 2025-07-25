"""
Test suite for the ContentType plugin.
"""

import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestContentTypePlugin(unittest.TestCase):
    """Test cases for the ContentType plugin."""

    def setUp(self):
        """Set up test fixtures."""
        from asciidoc_dita_toolkit.modules.content_type.content_type_detector import (
            ContentTypeDetector,
        )
        from asciidoc_dita_toolkit.modules.content_type.content_type_processor import (
            ContentTypeProcessor,
        )
        from asciidoc_dita_toolkit.modules.content_type.ui_interface import MockUI

        self.detector = ContentTypeDetector()
        self.ui = MockUI()
        self.processor = ContentTypeProcessor(self.detector, self.ui)

    def test_get_content_type_from_filename(self):
        """Test content type detection from filename."""
        test_cases = [
            ("assembly_test.adoc", "ASSEMBLY"),
            ("assembly-test.adoc", "ASSEMBLY"),
            ("con_test.adoc", "CONCEPT"),
            ("con-test.adoc", "CONCEPT"),
            ("proc_test.adoc", "PROCEDURE"),
            ("proc-test.adoc", "PROCEDURE"),
            ("ref_test.adoc", "REFERENCE"),
            ("ref-test.adoc", "REFERENCE"),
            ("snip_test.adoc", "SNIPPET"),
            ("snip-test.adoc", "SNIPPET"),
            ("other_test.adoc", None),
        ]

        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.detector.detect_from_filename(filename)
                self.assertEqual(result, expected)

    def test_detect_existing_content_type(self):
        """Test detection of existing content type attributes."""
        test_cases = [
            (
                [("text", "\n"), (":_mod-docs-content-type: CONCEPT", "\n")],
                ("CONCEPT", 1, "current"),
            ),
            (
                [("text", "\n"), (":_content-type: PROCEDURE", "\n")],
                ("PROCEDURE", 1, "deprecated_content"),
            ),
            (
                [("text", "\n"), (":_module-type: REFERENCE", "\n")],
                ("REFERENCE", 1, "deprecated_module"),
            ),
            (
                [("text", "\n"), ("//:_mod-docs-content-type: ASSEMBLY", "\n")],
                ("ASSEMBLY", 1, "commented"),
            ),
            ([("text", "\n"), ("no content type", "\n")], (None, None, None)),
        ]

        for lines, expected in test_cases:
            with self.subTest(lines=lines):
                result = self.detector.detect_existing_attribute(lines)
                if result:
                    actual = (result.value, result.line_index, result.attribute_type)
                else:
                    actual = (None, None, None)
                self.assertEqual(actual, expected)

    def test_ensure_blank_line_below(self):
        """Test ensuring blank line after content type attribute."""
        # Test case: line at end of file
        lines = [("content", "\n"), (":_mod-docs-content-type: CONCEPT", "\n")]
        result = self.processor.ensure_blank_line_after_attribute(lines, 1)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[2], ("", "\n"))

        # Test case: no blank line after attribute
        lines = [
            ("content", "\n"),
            (":_mod-docs-content-type: CONCEPT", "\n"),
            ("more content", "\n"),
        ]
        result = self.processor.ensure_blank_line_after_attribute(lines, 1)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[2], ("", "\n"))

        # Test case: blank line already exists
        lines = [
            ("content", "\n"),
            (":_mod-docs-content-type: CONCEPT", "\n"),
            ("", "\n"),
            ("more content", "\n"),
        ]
        result = self.processor.ensure_blank_line_after_attribute(lines, 1)
        self.assertEqual(len(result), 4)  # Should not add another blank line



if __name__ == "__main__":
    unittest.main()
