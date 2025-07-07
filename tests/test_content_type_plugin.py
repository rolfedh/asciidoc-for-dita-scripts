"""
Unit tests for the ContentType plugin.

Tests the refactored components with proper separation of concerns.
"""

import unittest
from unittest.mock import Mock, patch
import tempfile
import os

from asciidoc_dita_toolkit.asciidoc_dita.plugins.content_type_detector import (
    ContentTypeDetector, ContentTypeConfig, ContentTypeAttribute, DetectionResult
)
from asciidoc_dita_toolkit.asciidoc_dita.plugins.ui_interface import (
    UIInterface, ConsoleUI, BatchUI, MockUI, MinimalistConsoleUI, QuietModeUI
)
from asciidoc_dita_toolkit.asciidoc_dita.plugins.content_type_processor import (
    ContentTypeProcessor
)


class TestContentTypeDetector(unittest.TestCase):
    """Test the ContentTypeDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = ContentTypeDetector()
    
    def test_detect_from_filename_procedure(self):
        """Test filename detection for procedure files."""
        result = self.detector.detect_from_filename("proc_install_software.adoc")
        self.assertEqual(result, "PROCEDURE")
    
    def test_detect_from_filename_concept(self):
        """Test filename detection for concept files."""
        result = self.detector.detect_from_filename("con_understanding_concepts.adoc")
        self.assertEqual(result, "CONCEPT")
    
    def test_detect_from_filename_no_match(self):
        """Test filename detection when no pattern matches."""
        result = self.detector.detect_from_filename("random_file.adoc")
        self.assertIsNone(result)
    
    def test_detect_existing_attribute_current(self):
        """Test detection of current format attribute."""
        lines = [
            (":_mod-docs-content-type: PROCEDURE", "\n"),
            ("", "\n"),
            ("= Installing Software", "\n")
        ]
        result = self.detector.detect_existing_attribute(lines)
        self.assertIsNotNone(result)
        self.assertEqual(result.value, "PROCEDURE")
        self.assertEqual(result.line_index, 0)
        self.assertEqual(result.attribute_type, "current")
    
    def test_detect_existing_attribute_deprecated(self):
        """Test detection of deprecated format attribute."""
        lines = [
            (":_content-type: CONCEPT", "\n"),
            ("", "\n"),
            ("= Understanding Concepts", "\n")
        ]
        result = self.detector.detect_existing_attribute(lines)
        self.assertIsNotNone(result)
        self.assertEqual(result.value, "CONCEPT")
        self.assertEqual(result.attribute_type, "deprecated_content")
    
    def test_detect_existing_attribute_commented(self):
        """Test detection of commented attribute."""
        lines = [
            ("//:_mod-docs-content-type: REFERENCE", "\n"),
            ("", "\n"),
            ("= API Reference", "\n")
        ]
        result = self.detector.detect_existing_attribute(lines)
        self.assertIsNotNone(result)
        self.assertEqual(result.value, "REFERENCE")
        self.assertEqual(result.attribute_type, "commented")
    
    def test_detect_from_title_procedure(self):
        """Test title-based detection for procedure."""
        result = self.detector.detect_from_title("Installing Red Hat Enterprise Linux")
        self.assertEqual(result.suggested_type, "PROCEDURE")
        self.assertGreater(result.confidence, 0.5)
    
    def test_detect_from_title_reference(self):
        """Test title-based detection for reference."""
        result = self.detector.detect_from_title("Command Line Reference")
        self.assertEqual(result.suggested_type, "REFERENCE")
        self.assertGreater(result.confidence, 0.5)
    
    def test_detect_from_content_assembly(self):
        """Test content-based detection for assembly."""
        content = """
        = Getting Started Guide
        
        include::modules/overview.adoc[]
        include::modules/installation.adoc[]
        """
        result = self.detector.detect_from_content(content)
        self.assertEqual(result.suggested_type, "ASSEMBLY")
        self.assertGreater(result.confidence, 0.8)
    
    def test_detect_from_content_procedure(self):
        """Test content-based detection for procedure."""
        content = """= Installing Software

.Prerequisites
* System access

.Procedure
1. Download the software
2. Install the package
3. Configure the service
"""
        result = self.detector.detect_from_content(content)
        self.assertEqual(result.suggested_type, "PROCEDURE")
        self.assertGreater(result.confidence, 0.5)
    
    def test_extract_document_title(self):
        """Test document title extraction."""
        lines = [
            ("= Installing Red Hat Enterprise Linux", "\n"),
            ("", "\n"),
            ("This guide covers installation.", "\n")
        ]
        result = self.detector.extract_document_title(lines)
        self.assertEqual(result, "Installing Red Hat Enterprise Linux")
    
    def test_extract_document_title_markdown(self):
        """Test document title extraction from markdown format."""
        lines = [
            ("# Installing Red Hat Enterprise Linux", "\n"),
            ("", "\n"),
            ("This guide covers installation.", "\n")
        ]
        result = self.detector.extract_document_title(lines)
        self.assertEqual(result, "Installing Red Hat Enterprise Linux")
    
    def test_get_comprehensive_suggestion_filename_priority(self):
        """Test comprehensive suggestion prioritizes filename detection."""
        filename = "proc_install_software.adoc"
        title = "Command Reference"  # Would suggest REFERENCE
        content = "This is a procedure guide."
        
        result = self.detector.get_comprehensive_suggestion(filename, title, content)
        self.assertEqual(result.suggested_type, "PROCEDURE")  # Filename wins
        self.assertGreater(result.confidence, 0.9)


class TestUIInterface(unittest.TestCase):
    """Test the UI interface implementations."""
    
    def test_mock_ui_stores_messages(self):
        """Test that MockUI stores messages for verification."""
        ui = MockUI()
        ui.show_message("Test message")
        ui.show_error("Test error")
        ui.show_success("Test success")
        ui.show_warning("Test warning")
        
        self.assertEqual(ui.messages, ["Test message"])
        self.assertEqual(ui.errors, ["Test error"])
        self.assertEqual(ui.successes, ["Test success"])
        self.assertEqual(ui.warnings, ["Test warning"])
    
    def test_mock_ui_prompt_with_responses(self):
        """Test MockUI with pre-configured responses."""
        ui = MockUI(responses=["PROCEDURE", "SKIP", "CONCEPT"])
        
        detection_result = DetectionResult("ASSEMBLY", 0.8, ["test reasoning"])
        
        # First call returns PROCEDURE
        result1 = ui.prompt_content_type(detection_result)
        self.assertEqual(result1, "PROCEDURE")
        
        # Second call returns None (SKIP)
        result2 = ui.prompt_content_type(detection_result)
        self.assertIsNone(result2)
        
        # Third call returns CONCEPT
        result3 = ui.prompt_content_type(detection_result)
        self.assertEqual(result3, "CONCEPT")
    
    def test_batch_ui_uses_suggestion(self):
        """Test BatchUI uses suggestions without prompting."""
        ui = BatchUI()
        detection_result = DetectionResult("ASSEMBLY", 0.8, ["test reasoning"])
        
        result = ui.prompt_content_type(detection_result)
        self.assertEqual(result, "ASSEMBLY")
    
    def test_batch_ui_falls_back_to_default(self):
        """Test BatchUI falls back to default when no suggestion."""
        ui = BatchUI(default_type="CONCEPT")
        detection_result = DetectionResult(None, 0.0, ["no patterns"])
        
        result = ui.prompt_content_type(detection_result)
        self.assertEqual(result, "CONCEPT")
    
    def test_quiet_mode_ui_always_returns_tbd(self):
        """Test QuietModeUI always returns TBD."""
        ui = QuietModeUI()
        detection_result = DetectionResult("ASSEMBLY", 0.8, ["test reasoning"])
        
        result = ui.prompt_content_type(detection_result)
        self.assertEqual(result, "TBD")
    
    def test_quiet_mode_ui_never_exits(self):
        """Test QuietModeUI never exits early."""
        ui = QuietModeUI()
        self.assertFalse(ui.should_exit())
    
    def test_minimalist_console_ui_initialization(self):
        """Test MinimalistConsoleUI initialization."""
        ui = MinimalistConsoleUI()
        self.assertFalse(ui.should_exit())
        self.assertEqual(len(ui.content_type_options), 6)
        
        # Check the content type options format
        expected_options = [
            ("A", "ASSEMBLY"),
            ("C", "CONCEPT"),
            ("P", "PROCEDURE"),
            ("R", "REFERENCE"),
            ("S", "SNIPPET"),
            ("T", "TBD")
        ]
        self.assertEqual(ui.content_type_options, expected_options)


class TestContentTypeProcessor(unittest.TestCase):
    """Test the ContentTypeProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = ContentTypeDetector()
        self.ui = MockUI()
        self.processor = ContentTypeProcessor(self.detector, self.ui)
    
    def test_validate_file_access_missing_file(self):
        """Test file validation for missing file."""
        result = self.processor.validate_file_access("/nonexistent/file.adoc")
        self.assertFalse(result)
        self.assertIn("File not found", self.ui.errors[0])
    
    def test_ensure_blank_line_after_attribute(self):
        """Test ensuring blank line after attribute."""
        lines = [
            (":_mod-docs-content-type: PROCEDURE", "\n"),
            ("= Title", "\n"),
            ("Content", "\n")
        ]
        result = self.processor.ensure_blank_line_after_attribute(lines, 0)
        self.assertEqual(result[1], ("", "\n"))  # Blank line inserted
    
    def test_update_existing_attribute_current_format(self):
        """Test updating existing current format attribute."""
        lines = [
            (":_mod-docs-content-type: OLD_VALUE", "\n"),
            ("", "\n"),
            ("= Title", "\n")
        ]
        attribute = ContentTypeAttribute("OLD_VALUE", 0, "current")
        
        result = self.processor.update_existing_attribute(lines, attribute, "NEW_VALUE")
        self.assertEqual(result[0][0], ":_mod-docs-content-type: NEW_VALUE")
    
    def test_update_existing_attribute_deprecated_format(self):
        """Test updating deprecated format attribute."""
        lines = [
            (":_content-type: OLD_VALUE", "\n"),
            ("", "\n"),
            ("= Title", "\n")
        ]
        attribute = ContentTypeAttribute("OLD_VALUE", 0, "deprecated_content")
        
        result = self.processor.update_existing_attribute(lines, attribute, "NEW_VALUE")
        self.assertEqual(result[0][0], ":_mod-docs-content-type: NEW_VALUE")
    
    def test_add_new_attribute(self):
        """Test adding new attribute to file."""
        lines = [
            ("= Title", "\n"),
            ("Content", "\n")
        ]
        
        result = self.processor.add_new_attribute(lines, "PROCEDURE")
        self.assertEqual(result[0][0], ":_mod-docs-content-type: PROCEDURE")
        self.assertEqual(result[1][0], "")  # Blank line
        self.assertEqual(result[2][0], "= Title")  # Original content shifted
    
    def test_get_file_analysis(self):
        """Test comprehensive file analysis."""
        lines = [
            ("= Installing Software", "\n"),
            ("", "\n"),
            ("This is a procedure guide.", "\n")
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
            f.write('\n'.join([text for text, _ in lines]))
            temp_path = f.name
        
        try:
            analysis = self.processor.get_file_analysis(temp_path, lines)
            
            self.assertIn('filename', analysis)
            self.assertIn('title', analysis)
            self.assertIn('content', analysis)
            self.assertIn('detection_result', analysis)
            self.assertIn('existing_attribute', analysis)
            
            self.assertEqual(analysis['title'], "Installing Software")
            self.assertIsNone(analysis['existing_attribute'])
            
        finally:
            os.unlink(temp_path)
    
    def test_process_file_with_mocked_file_operations(self):
        """Test file processing with mocked file operations."""
        # Mock file reader and writer
        mock_reader = Mock(return_value=[
            (":_mod-docs-content-type: PROCEDURE", "\n"),
            ("", "\n"),
            ("= Installing Software", "\n")
        ])
        mock_writer = Mock()
        
        processor = ContentTypeProcessor(
            self.detector, 
            self.ui, 
            file_reader=mock_reader,
            file_writer=mock_writer
        )
        
        with patch('os.path.exists', return_value=True), \
             patch('os.access', return_value=True):
            
            result = processor.process_file("/mock/path/file.adoc")
            
            self.assertTrue(result)
            mock_reader.assert_called_once_with("/mock/path/file.adoc")
            mock_writer.assert_called_once()


class TestContentTypeConfig(unittest.TestCase):
    """Test the ContentTypeConfig class."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = ContentTypeConfig.get_default()
        
        self.assertIn(("proc_", "proc-"), config.filename_prefixes)
        self.assertEqual(config.filename_prefixes[("proc_", "proc-")], "PROCEDURE")
        
        self.assertIn("PROCEDURE", config.title_patterns)
        self.assertIn("REFERENCE", config.content_patterns)
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = ContentTypeConfig(
            filename_prefixes={("custom_",): "CUSTOM_TYPE"},
            title_patterns={"CUSTOM_TYPE": [r"custom pattern"]},
            content_patterns={"CUSTOM_TYPE": [r"custom content"]}
        )
        
        detector = ContentTypeDetector(config)
        result = detector.detect_from_filename("custom_file.adoc")
        self.assertEqual(result, "CUSTOM_TYPE")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def test_full_workflow_new_file(self):
        """Test complete workflow for a new file."""
        # Create test UI with predetermined responses
        ui = MockUI(responses=["PROCEDURE"])
        detector = ContentTypeDetector()
        processor = ContentTypeProcessor(detector, ui)
        
        # Mock file operations
        mock_reader = Mock(return_value=[
            ("= Installing Software", "\n"),
            ("", "\n"),
            ("This is a procedure guide.", "\n")
        ])
        mock_writer = Mock()
        processor.file_reader = mock_reader
        processor.file_writer = mock_writer
        
        with patch('os.path.exists', return_value=True), \
             patch('os.access', return_value=True):
            
            result = processor.process_file("/test/proc_install.adoc")
            
            self.assertTrue(result)
            # Verify file was read and written
            mock_reader.assert_called_once()
            mock_writer.assert_called_once()
            
            # Verify content was processed
            written_lines = mock_writer.call_args[0][1]
            self.assertEqual(written_lines[0][0], ":_mod-docs-content-type: PROCEDURE")
    
    def test_full_workflow_existing_deprecated_attribute(self):
        """Test complete workflow for file with deprecated attribute."""
        ui = MockUI()
        detector = ContentTypeDetector()
        processor = ContentTypeProcessor(detector, ui)
        
        # Mock file operations
        mock_reader = Mock(return_value=[
            (":_content-type: OLD_CONCEPT", "\n"),
            ("", "\n"),
            ("= Understanding Concepts", "\n")
        ])
        mock_writer = Mock()
        processor.file_reader = mock_reader
        processor.file_writer = mock_writer
        
        with patch('os.path.exists', return_value=True), \
             patch('os.access', return_value=True):
            
            result = processor.process_file("/test/concept_file.adoc")
            
            self.assertTrue(result)
            # Verify content was updated
            written_lines = mock_writer.call_args[0][1]
            self.assertEqual(written_lines[0][0], ":_mod-docs-content-type: OLD_CONCEPT")


if __name__ == '__main__':
    unittest.main()