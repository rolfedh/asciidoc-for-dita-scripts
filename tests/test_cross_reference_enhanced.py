"""
Test suite for the enhanced CrossReference plugin.

This script tests the enhanced cross-reference functionality including:
- Cross-reference fixing and validation
- Migration-aware processing
- Comprehensive reporting
- Validation-only mode
- Broken xref detection

To run: python3 -m pytest tests/test_cross_reference_enhanced.py -v
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import json

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from asciidoc_dita_toolkit.asciidoc_dita.plugins.CrossReference import (
        CrossReferenceProcessor, BrokenXref, XrefFix, ValidationReport,
        Highlighter, find_master_files, process_master_file, format_validation_report
    )
except ImportError as e:
    print(f"Warning: Could not import enhanced CrossReference plugin: {e}")
    CrossReferenceProcessor = None


@unittest.skipIf(CrossReferenceProcessor is None, "Enhanced CrossReference plugin could not be imported")
class TestCrossReferenceProcessor(unittest.TestCase):
    """Test cases for the enhanced CrossReferenceProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = CrossReferenceProcessor()
        self.validation_processor = CrossReferenceProcessor(validation_only=True)
        self.migration_processor = CrossReferenceProcessor(migration_mode=True)

    def test_processor_initialization(self):
        """Test that processor initializes with correct settings."""
        # Standard processor
        self.assertFalse(self.processor.validation_only)
        self.assertFalse(self.processor.migration_mode)
        self.assertEqual(len(self.processor.id_map), 0)
        self.assertEqual(len(self.processor.broken_xrefs), 0)
        self.assertEqual(len(self.processor.fixed_xrefs), 0)
        self.assertEqual(len(self.processor.warnings), 0)
        
        # Validation-only processor
        self.assertTrue(self.validation_processor.validation_only)
        self.assertFalse(self.validation_processor.migration_mode)
        
        # Migration-aware processor
        self.assertFalse(self.migration_processor.validation_only)
        self.assertTrue(self.migration_processor.migration_mode)

    def test_regex_patterns(self):
        """Test regex pattern initialization."""
        self.assertIsNotNone(self.processor.id_regex)
        self.assertIsNotNone(self.processor.include_regex)
        self.assertIsNotNone(self.processor.xref_regex)
        self.assertIsNotNone(self.processor.context_id_regex)

    def test_id_regex_pattern(self):
        """Test ID regex pattern matching."""
        test_cases = [
            ('[id="topic"]', 'topic'),
            ('[id="section-name"]', 'section-name'),
            ('[id="topic_banana"]', 'topic_banana'),
            ('[id="installing-edge_ocp4"]', 'installing-edge_ocp4'),
        ]

        for input_text, expected_id in test_cases:
            with self.subTest(input_text=input_text):
                match = self.processor.id_regex.search(input_text)
                self.assertIsNotNone(match)
                self.assertEqual(match.group(1), expected_id)

    def test_xref_regex_pattern(self):
        """Test xref regex pattern matching."""
        test_cases = [
            ('xref:topic[Link Text]', ('topic', '[Link Text]')),
            ('xref:section-name[Section]', ('section-name', '[Section]')),
            ('See xref:overview[Overview]', ('overview', '[Overview]')),
        ]

        # Should NOT match already-fixed xrefs
        non_matching_cases = [
            'xref:file.adoc#topic[Link Text]',
            'xref:modules/intro.adoc#section[Section]',
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                match = self.processor.xref_regex.search(input_text)
                self.assertIsNotNone(match)
                self.assertEqual(match.group(1), expected[0])
                self.assertEqual(match.group(2), expected[1])

        for input_text in non_matching_cases:
            with self.subTest(input_text=input_text):
                match = self.processor.xref_regex.search(input_text)
                self.assertIsNone(match, f"Should not match already-fixed xref: {input_text}")

    def test_context_id_regex_pattern(self):
        """Test context ID regex pattern matching."""
        test_cases = [
            ('[id="topic_banana"]', ('topic', 'banana')),
            ('[id="installing-edge_ocp4"]', ('installing-edge', 'ocp4')),
            ('[id="section_test-context"]', ('section', 'test-context')),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                match = self.processor.context_id_regex.search(input_text)
                self.assertIsNotNone(match)
                self.assertEqual(match.group(1), expected[0])
                self.assertEqual(match.group(2), expected[1])

    def test_build_id_map(self):
        """Test ID map building functionality."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
            f.write("""= Test Document

[id="topic"]
== Topic

Some content here.

[id="section_banana"]
=== Section

More content.
""")
            f.flush()
            
            try:
                self.processor.build_id_map(f.name)
                
                # Check ID map was built correctly
                self.assertEqual(len(self.processor.id_map), 2)
                self.assertIn('topic', self.processor.id_map)
                self.assertIn('section_banana', self.processor.id_map)
                self.assertEqual(self.processor.id_map['topic'], f.name)
                self.assertEqual(self.processor.id_map['section_banana'], f.name)
                
            finally:
                os.unlink(f.name)

    def test_build_id_map_with_includes(self):
        """Test ID map building with include files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create master file
            master_file = os.path.join(temp_dir, 'master.adoc')
            include_file = os.path.join(temp_dir, 'included.adoc')
            
            with open(master_file, 'w') as f:
                f.write("""= Master Document

[id="master_topic"]
== Master Topic

include::included.adoc[]
""")
            
            with open(include_file, 'w') as f:
                f.write("""[id="included_section"]
=== Included Section

Content from included file.
""")
            
            self.processor.build_id_map(master_file)
            
            # Check that IDs from both files were found
            self.assertEqual(len(self.processor.id_map), 2)
            self.assertIn('master_topic', self.processor.id_map)
            self.assertIn('included_section', self.processor.id_map)
            self.assertEqual(self.processor.id_map['master_topic'], master_file)
            self.assertEqual(self.processor.id_map['included_section'], include_file)

    def test_build_id_map_migration_mode(self):
        """Test ID map building in migration mode."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
            f.write("""= Test Document

[id="topic_banana"]
== Old Style Topic

[id="topic"]
== New Style Topic

[id="section"]
=== Regular Section
""")
            f.flush()
            
            try:
                self.migration_processor.build_id_map(f.name)
                
                # Check ID map and context mappings
                self.assertEqual(len(self.migration_processor.id_map), 3)
                self.assertIn('topic_banana', self.migration_processor.id_map)
                self.assertIn('topic', self.migration_processor.id_map)
                self.assertIn('section', self.migration_processor.id_map)
                
                # Check context mappings
                self.assertIn('topic_banana', self.migration_processor.context_id_mappings)
                self.assertEqual(self.migration_processor.context_id_mappings['topic_banana'], 'topic')
                
            finally:
                os.unlink(f.name)

    def test_prefer_context_free_ids(self):
        """Test context-free ID preference in migration mode."""
        # Set up context mappings
        self.migration_processor.context_id_mappings = {
            'topic_banana': 'topic',
            'section_apple': 'section'
        }
        
        # Test preference for context-free IDs
        preferred = self.migration_processor.prefer_context_free_ids('topic_banana', '')
        self.assertEqual(preferred, 'topic')
        
        preferred = self.migration_processor.prefer_context_free_ids('section_apple', '')
        self.assertEqual(preferred, 'section')
        
        # Test no change for unmapped IDs
        preferred = self.migration_processor.prefer_context_free_ids('unmapped_id', '')
        self.assertEqual(preferred, 'unmapped_id')
        
        # Test standard processor doesn't change anything
        preferred = self.processor.prefer_context_free_ids('topic_banana', '')
        self.assertEqual(preferred, 'topic_banana')

    def test_validate_xref(self):
        """Test xref validation functionality."""
        # Set up ID map
        self.processor.id_map = {
            'topic': 'file1.adoc',
            'section': 'file2.adoc'
        }
        
        # Test valid xref
        result = self.processor.validate_xref('test.adoc', 1, 'xref:topic[Topic]', 'topic', '')
        self.assertTrue(result)
        self.assertEqual(len(self.processor.broken_xrefs), 0)
        
        # Test broken xref (missing ID)
        result = self.processor.validate_xref('test.adoc', 2, 'xref:missing[Missing]', 'missing', '')
        self.assertFalse(result)
        self.assertEqual(len(self.processor.broken_xrefs), 1)
        self.assertEqual(self.processor.broken_xrefs[0].target_id, 'missing')
        self.assertEqual(self.processor.broken_xrefs[0].reason, "Target ID 'missing' not found in documentation")

    def test_update_xref(self):
        """Test xref updating functionality."""
        # Set up ID map
        self.processor.id_map = {
            'topic': '/path/to/file1.adoc',
            'section': '/path/to/file2.adoc'
        }
        
        # Create mock regex match
        mock_match = MagicMock()
        mock_match.group.side_effect = lambda x: {
            0: 'topic[Topic Link]',
            1: 'topic',
            2: '[Topic Link]'
        }[x]
        
        with patch('builtins.print'):  # Suppress console output
            result = self.processor.update_xref('test.adoc', 1, mock_match)
            
            self.assertEqual(result, 'file1.adoc#topic[Topic Link]')
            self.assertEqual(len(self.processor.fixed_xrefs), 1)
            
            fix = self.processor.fixed_xrefs[0]
            self.assertEqual(fix.filepath, 'test.adoc')
            self.assertEqual(fix.line_number, 1)
            self.assertEqual(fix.old_xref, 'topic[Topic Link]')
            self.assertEqual(fix.new_xref, 'file1.adoc#topic[Topic Link]')

    def test_update_xref_migration_mode(self):
        """Test xref updating in migration mode."""
        # Set up ID map and context mappings
        self.migration_processor.id_map = {
            'topic_banana': '/path/to/file1.adoc',
            'topic': '/path/to/file1.adoc'
        }
        self.migration_processor.context_id_mappings = {
            'topic_banana': 'topic'
        }
        
        # Create mock regex match for old-style ID
        mock_match = MagicMock()
        mock_match.group.side_effect = lambda x: {
            0: 'topic_banana[Topic Link]',
            1: 'topic_banana',
            2: '[Topic Link]'
        }[x]
        
        with patch('builtins.print'):  # Suppress console output
            result = self.migration_processor.update_xref('test.adoc', 1, mock_match)
            
            # Should use the context-free ID
            self.assertEqual(result, 'file1.adoc#topic[Topic Link]')
            self.assertEqual(len(self.migration_processor.fixed_xrefs), 1)

    def test_update_xref_missing_id(self):
        """Test xref updating with missing ID."""
        # Empty ID map
        self.processor.id_map = {}
        
        # Create mock regex match
        mock_match = MagicMock()
        mock_match.group.side_effect = lambda x: {
            0: 'missing[Missing Link]',
            1: 'missing',
            2: '[Missing Link]'
        }[x]
        
        with patch('builtins.print'):  # Suppress console output
            result = self.processor.update_xref('test.adoc', 1, mock_match)
            
            # Should return original xref unchanged
            self.assertEqual(result, 'missing[Missing Link]')
            self.assertEqual(len(self.processor.broken_xrefs), 1)
            self.assertEqual(len(self.processor.warnings), 1)

    def test_process_file_validation_only(self):
        """Test file processing in validation-only mode."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
            original_content = """= Test Document

[id="topic"]
== Topic

See xref:missing[Missing Section].
See xref:topic[This Topic].
"""
            f.write(original_content)
            f.flush()
            
            try:
                # Set up ID map
                self.validation_processor.id_map = {'topic': f.name}
                
                self.validation_processor.process_file(f.name)
                
                # Check that file was not modified
                with open(f.name, 'r') as read_f:
                    current_content = read_f.read()
                self.assertEqual(current_content, original_content)
                
                # Check validation results
                self.assertEqual(len(self.validation_processor.all_xrefs), 2)
                self.assertEqual(len(self.validation_processor.broken_xrefs), 1)
                self.assertEqual(self.validation_processor.broken_xrefs[0].target_id, 'missing')
                
            finally:
                os.unlink(f.name)

    def test_process_file_with_fixes(self):
        """Test file processing with xref fixes."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
            f.write("""= Test Document

[id="topic"]
== Topic

See xref:section[Section].
""")
            f.flush()
            
            try:
                # Set up ID map
                self.processor.id_map = {
                    'topic': f.name,
                    'section': f.name
                }
                
                self.processor.process_file(f.name)
                
                # Check that file was modified
                with open(f.name, 'r') as read_f:
                    modified_content = read_f.read()
                
                # Extract filename for expected result
                filename = os.path.basename(f.name)
                expected_xref = f"xref:{filename}#section[Section]"
                self.assertIn(expected_xref, modified_content)
                
                # Check fix tracking
                self.assertEqual(len(self.processor.fixed_xrefs), 1)
                
            finally:
                os.unlink(f.name)

    def test_generate_validation_report(self):
        """Test validation report generation."""
        # Set up test data
        self.processor.processed_files = {'file1.adoc', 'file2.adoc'}
        self.processor.all_xrefs = [
            ('file1.adoc', 1, 'xref:topic[Topic]', 'topic', ''),
            ('file1.adoc', 5, 'xref:missing[Missing]', 'missing', ''),
            ('file2.adoc', 3, 'xref:section[Section]', 'section', '')
        ]
        self.processor.broken_xrefs = [
            BrokenXref('file1.adoc', 5, 'xref:missing[Missing]', 'missing', '', 'ID not found')
        ]
        self.processor.fixed_xrefs = [
            XrefFix('file1.adoc', 1, 'topic[Topic]', 'file1.adoc#topic[Topic]')
        ]
        self.processor.warnings = ['Warning message']
        
        report = self.processor.generate_validation_report()
        
        # Check report contents
        self.assertEqual(report.total_files_processed, 2)
        self.assertEqual(report.total_xrefs_found, 3)
        self.assertEqual(len(report.broken_xrefs), 1)
        self.assertEqual(len(report.fixed_xrefs), 1)
        self.assertEqual(len(report.warnings), 1)
        self.assertFalse(report.validation_successful)  # Has broken xrefs


@unittest.skipIf(CrossReferenceProcessor is None, "Enhanced CrossReference plugin could not be imported")
class TestHighlighter(unittest.TestCase):
    """Test cases for the enhanced Highlighter utility class."""

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

    def test_success_formatting(self):
        """Test success text formatting."""
        highlighter = Highlighter("Success text")
        result = highlighter.success()
        self.assertIn("Success text", result)
        self.assertTrue(result.startswith('\033[0;32m'))
        self.assertTrue(result.endswith('\033[0m'))


@unittest.skipIf(CrossReferenceProcessor is None, "Enhanced CrossReference plugin could not be imported")
class TestDataStructures(unittest.TestCase):
    """Test cases for the data structures used by enhanced CrossReference."""

    def test_broken_xref_creation(self):
        """Test BrokenXref data structure."""
        broken_xref = BrokenXref(
            filepath='test.adoc',
            line_number=5,
            xref_text='xref:missing[Missing]',
            target_id='missing',
            target_file='',
            reason='ID not found'
        )
        
        self.assertEqual(broken_xref.filepath, 'test.adoc')
        self.assertEqual(broken_xref.line_number, 5)
        self.assertEqual(broken_xref.xref_text, 'xref:missing[Missing]')
        self.assertEqual(broken_xref.target_id, 'missing')
        self.assertEqual(broken_xref.target_file, '')
        self.assertEqual(broken_xref.reason, 'ID not found')

    def test_xref_fix_creation(self):
        """Test XrefFix data structure."""
        xref_fix = XrefFix(
            filepath='test.adoc',
            line_number=3,
            old_xref='topic[Topic]',
            new_xref='file.adoc#topic[Topic]'
        )
        
        self.assertEqual(xref_fix.filepath, 'test.adoc')
        self.assertEqual(xref_fix.line_number, 3)
        self.assertEqual(xref_fix.old_xref, 'topic[Topic]')
        self.assertEqual(xref_fix.new_xref, 'file.adoc#topic[Topic]')

    def test_validation_report_creation(self):
        """Test ValidationReport data structure."""
        broken_xref = BrokenXref('test.adoc', 1, 'xref:missing[Missing]', 'missing', '', 'ID not found')
        xref_fix = XrefFix('test.adoc', 2, 'topic[Topic]', 'file.adoc#topic[Topic]')
        
        report = ValidationReport(
            total_files_processed=5,
            total_xrefs_found=10,
            broken_xrefs=[broken_xref],
            fixed_xrefs=[xref_fix],
            warnings=['Warning'],
            validation_successful=False
        )
        
        self.assertEqual(report.total_files_processed, 5)
        self.assertEqual(report.total_xrefs_found, 10)
        self.assertEqual(len(report.broken_xrefs), 1)
        self.assertEqual(len(report.fixed_xrefs), 1)
        self.assertEqual(len(report.warnings), 1)
        self.assertFalse(report.validation_successful)


@unittest.skipIf(CrossReferenceProcessor is None, "Enhanced CrossReference plugin could not be imported")
class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

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

    def test_process_master_file(self):
        """Test processing a master file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
            f.write("""= Master Document

[id="master_topic"]
== Master Topic

See xref:section[Section].

[id="section"]
=== Section

Content here.
""")
            f.flush()
            
            try:
                with patch('builtins.print'):  # Suppress console output
                    report = process_master_file(f.name)
                
                # Check that processing was successful
                self.assertIsInstance(report, ValidationReport)
                self.assertGreater(report.total_files_processed, 0)
                
            finally:
                os.unlink(f.name)

    def test_process_master_file_validation_only(self):
        """Test processing a master file in validation-only mode."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
            original_content = """= Master Document

[id="master_topic"]
== Master Topic

See xref:missing[Missing Section].
"""
            f.write(original_content)
            f.flush()
            
            try:
                with patch('builtins.print'):  # Suppress console output
                    report = process_master_file(f.name, validation_only=True)
                
                # Check that file was not modified
                with open(f.name, 'r') as read_f:
                    current_content = read_f.read()
                self.assertEqual(current_content, original_content)
                
                # Check validation results
                self.assertIsInstance(report, ValidationReport)
                self.assertGreater(len(report.broken_xrefs), 0)
                
            finally:
                os.unlink(f.name)

    def test_process_master_file_migration_mode(self):
        """Test processing a master file in migration mode."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
            f.write("""= Master Document

[id="topic_banana"]
== Old Style Topic

[id="topic"]
== New Style Topic

See xref:topic_banana[Old Reference].
""")
            f.flush()
            
            try:
                with patch('builtins.print'):  # Suppress console output
                    report = process_master_file(f.name, migration_mode=True)
                
                # Check that processing was successful
                self.assertIsInstance(report, ValidationReport)
                
                # In migration mode, the xref should be updated to prefer context-free ID
                with open(f.name, 'r') as read_f:
                    modified_content = read_f.read()
                
                filename = os.path.basename(f.name)
                expected_xref = f"xref:{filename}#topic[Old Reference]"
                self.assertIn(expected_xref, modified_content)
                
            finally:
                os.unlink(f.name)


@unittest.skipIf(CrossReferenceProcessor is None, "Enhanced CrossReference plugin could not be imported")
class TestReportFormatting(unittest.TestCase):
    """Test cases for validation report formatting."""

    def test_format_validation_report(self):
        """Test validation report formatting."""
        # Create test data
        broken_xref = BrokenXref(
            filepath='test.adoc',
            line_number=5,
            xref_text='xref:missing[Missing]',
            target_id='missing',
            target_file='',
            reason='ID not found'
        )
        
        xref_fix = XrefFix(
            filepath='test.adoc',
            line_number=3,
            old_xref='topic[Topic]',
            new_xref='file.adoc#topic[Topic]'
        )
        
        report = ValidationReport(
            total_files_processed=2,
            total_xrefs_found=5,
            broken_xrefs=[broken_xref],
            fixed_xrefs=[xref_fix],
            warnings=['Warning message'],
            validation_successful=False
        )
        
        # Test basic report
        text_report = format_validation_report(report)
        self.assertIn('=== Cross-Reference Validation Report ===', text_report)
        self.assertIn('Files processed: 2', text_report)
        self.assertIn('Total xrefs found: 5', text_report)
        self.assertIn('Broken xrefs: 1', text_report)
        self.assertIn('Fixed xrefs: 1', text_report)
        self.assertIn('Warnings: 1', text_report)
        self.assertIn('Validation successful: No', text_report)
        self.assertIn('test.adoc:5', text_report)
        self.assertIn('Xref: xref:missing[Missing]', text_report)
        self.assertIn('Target ID: missing', text_report)
        self.assertIn('Reason: ID not found', text_report)
        self.assertIn('Warning message', text_report)
        
        # Test detailed report
        detailed_report = format_validation_report(report, detailed=True)
        self.assertIn('=== Fixed Cross-References ===', detailed_report)
        self.assertIn('test.adoc:3', detailed_report)
        self.assertIn('topic[Topic] -> file.adoc#topic[Topic]', detailed_report)


@unittest.skipIf(CrossReferenceProcessor is None, "Enhanced CrossReference plugin could not be imported")
class TestIntegration(unittest.TestCase):
    """Integration tests for the enhanced CrossReference plugin."""

    def test_end_to_end_validation(self):
        """Test complete end-to-end validation process."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            master_file = os.path.join(temp_dir, 'master.adoc')
            include_file = os.path.join(temp_dir, 'included.adoc')
            
            with open(master_file, 'w') as f:
                f.write("""= Master Document

[id="master_topic"]
== Master Topic

See xref:included_section[Included Section].
See xref:missing_section[Missing Section].

include::included.adoc[]
""")
            
            with open(include_file, 'w') as f:
                f.write("""[id="included_section"]
=== Included Section

Content from included file.

See xref:master_topic[Master Topic].
""")
            
            with patch('builtins.print'):  # Suppress console output
                report = process_master_file(master_file, validation_only=True)
            
            # Check validation results
            self.assertEqual(report.total_files_processed, 2)  # master + included
            self.assertGreater(report.total_xrefs_found, 0)
            
            # Should have one broken xref (missing_section)
            self.assertEqual(len(report.broken_xrefs), 1)
            self.assertEqual(report.broken_xrefs[0].target_id, 'missing_section')
            self.assertFalse(report.validation_successful)

    def test_end_to_end_fixing(self):
        """Test complete end-to-end xref fixing process."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            master_file = os.path.join(temp_dir, 'master.adoc')
            include_file = os.path.join(temp_dir, 'included.adoc')
            
            with open(master_file, 'w') as f:
                f.write("""= Master Document

[id="master_topic"]
== Master Topic

See xref:included_section[Included Section].

include::included.adoc[]
""")
            
            with open(include_file, 'w') as f:
                f.write("""[id="included_section"]
=== Included Section

Content from included file.

See xref:master_topic[Master Topic].
""")
            
            with patch('builtins.print'):  # Suppress console output
                report = process_master_file(master_file, validation_only=False)
            
            # Check that files were modified correctly
            with open(master_file, 'r') as f:
                master_content = f.read()
            with open(include_file, 'r') as f:
                include_content = f.read()
            
            # Check for properly formatted xrefs
            self.assertIn('xref:included.adoc#included_section[Included Section]', master_content)
            
            master_filename = os.path.basename(master_file)
            self.assertIn(f'xref:{master_filename}#master_topic[Master Topic]', include_content)
            
            # Check fixing results
            self.assertEqual(len(report.fixed_xrefs), 2)
            self.assertTrue(report.validation_successful)


def main():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()