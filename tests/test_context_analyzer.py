"""
Test suite for the ContextAnalyzer plugin.

This script tests the context analysis functionality including:
- ID detection and analysis
- Xref and link usage tracking
- Collision detection
- Report generation

To run: python3 -m pytest tests/test_context_analyzer.py -v
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
    from asciidoc_dita_toolkit.asciidoc_dita.plugins.ContextAnalyzer import (
        ContextAnalyzer, IDWithContext, XrefUsage, CollisionReport, 
        FileAnalysis, AnalysisReport, format_text_report
    )
except ImportError as e:
    print(f"Warning: Could not import ContextAnalyzer plugin: {e}")
    ContextAnalyzer = None


@unittest.skipIf(ContextAnalyzer is None, "ContextAnalyzer plugin could not be imported")
class TestContextAnalyzer(unittest.TestCase):
    """Test cases for the ContextAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ContextAnalyzer()

    def test_analyzer_initialization(self):
        """Test that analyzer initializes with correct regex patterns."""
        self.assertIsNotNone(self.analyzer.id_with_context_regex)
        self.assertIsNotNone(self.analyzer.xref_regex)
        self.assertIsNotNone(self.analyzer.link_regex)
        self.assertIsNotNone(self.analyzer.context_attr_regex)
        self.assertEqual(len(self.analyzer.all_ids), 0)
        self.assertEqual(len(self.analyzer.all_xrefs), 0)
        self.assertEqual(len(self.analyzer.all_links), 0)
        self.assertEqual(len(self.analyzer.file_analyses), 0)

    def test_id_with_context_regex(self):
        """Test ID with context regex pattern matching."""
        test_cases = [
            ('[id="topic_banana"]', ('topic', 'banana')),
            ('[id="installing-edge_ocp4"]', ('installing-edge', 'ocp4')),
            ('[id="section_test-context"]', ('section', 'test-context')),
            ('[id="simple_id"]', ('simple', 'id')),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                match = self.analyzer.id_with_context_regex.search(input_text)
                self.assertIsNotNone(match)
                self.assertEqual(match.group(1), expected[0])
                self.assertEqual(match.group(2), expected[1])

    def test_xref_regex(self):
        """Test xref regex pattern matching."""
        test_cases = [
            ('xref:topic_id[Link Text]', ('topic_id', None, '[Link Text]')),
            ('xref:file.adoc#section_id[Section]', ('file.adoc', 'section_id', '[Section]')),
            ('See xref:overview[Overview]', ('overview', None, '[Overview]')),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                match = self.analyzer.xref_regex.search(input_text)
                self.assertIsNotNone(match)
                self.assertEqual(match.group(1), expected[0])
                self.assertEqual(match.group(2), expected[1])
                self.assertEqual(match.group(3), expected[2])

    def test_link_regex(self):
        """Test link regex pattern matching."""
        test_cases = [
            ('link:https://example.com#section[Link]', ('https://example.com', 'section', '[Link]')),
            ('link:file.html#anchor[Text]', ('file.html', 'anchor', '[Text]')),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                match = self.analyzer.link_regex.search(input_text)
                self.assertIsNotNone(match)
                self.assertEqual(match.group(1), expected[0])
                self.assertEqual(match.group(2), expected[1])
                self.assertEqual(match.group(3), expected[2])

    def test_context_attr_regex(self):
        """Test context attribute regex pattern matching."""
        test_cases = [
            (':context: banana', 'banana'),
            (':context: ocp4', 'ocp4'),
            (':context: test-context', 'test-context'),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                match = self.analyzer.context_attr_regex.search(input_text)
                self.assertIsNotNone(match)
                self.assertEqual(match.group(1), expected)

    def test_analyze_file_with_context_ids(self):
        """Test analyzing a file with context IDs."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
            f.write("""= Test Document

:context: banana

[id="topic_banana"]
== Topic

Some content here.

[id="section_banana"]
=== Section

More content.

See xref:other_topic[Other Topic].
""")
            f.flush()
            
            try:
                result = self.analyzer.analyze_file(f.name)
                
                # Check file analysis results
                self.assertEqual(result.filepath, f.name)
                self.assertEqual(len(result.context_attributes), 1)
                self.assertEqual(result.context_attributes[0], 'banana')
                self.assertEqual(len(result.ids_with_context), 2)
                self.assertEqual(len(result.xref_usages), 1)
                
                # Check ID analysis
                ids = result.ids_with_context
                self.assertEqual(ids[0].id_value, 'topic_banana')
                self.assertEqual(ids[0].base_id, 'topic')
                self.assertEqual(ids[0].context_value, 'banana')
                self.assertEqual(ids[1].id_value, 'section_banana')
                self.assertEqual(ids[1].base_id, 'section')
                self.assertEqual(ids[1].context_value, 'banana')
                
                # Check xref analysis
                xref = result.xref_usages[0]
                self.assertEqual(xref.target_id, 'other_topic')
                self.assertEqual(xref.full_match, 'xref:other_topic[Other Topic]')
                
            finally:
                os.unlink(f.name)

    def test_analyze_file_without_context_ids(self):
        """Test analyzing a file without context IDs."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
            f.write("""= Test Document

[id="simpletopic"]
== Topic

Some content here.

See xref:other_topic[Other Topic].
""")
            f.flush()
            
            try:
                result = self.analyzer.analyze_file(f.name)
                
                # Check file analysis results
                self.assertEqual(result.filepath, f.name)
                self.assertEqual(len(result.context_attributes), 0)
                self.assertEqual(len(result.ids_with_context), 0)
                self.assertEqual(len(result.xref_usages), 1)
                
            finally:
                os.unlink(f.name)

    def test_detect_id_collisions(self):
        """Test ID collision detection."""
        # Add some test IDs that would collide
        self.analyzer.all_ids = {
            'topic': [
                IDWithContext('topic_banana', 'topic', 'banana', 'file1.adoc', 1),
                IDWithContext('topic_apple', 'topic', 'apple', 'file2.adoc', 1),
            ],
            'section': [
                IDWithContext('section_banana', 'section', 'banana', 'file1.adoc', 5),
                IDWithContext('section_apple', 'section', 'apple', 'file1.adoc', 10),
            ],
            'unique': [
                IDWithContext('unique_banana', 'unique', 'banana', 'file1.adoc', 15),
            ]
        }
        
        collisions = self.analyzer.detect_id_collisions()
        
        # Should find 2 collisions (topic and section)
        self.assertEqual(len(collisions), 2)
        
        # Check collision details
        topic_collision = next(c for c in collisions if c.base_id == 'topic')
        self.assertEqual(len(topic_collision.conflicting_files), 2)
        self.assertIn('file1.adoc', topic_collision.conflicting_files)
        self.assertIn('file2.adoc', topic_collision.conflicting_files)
        
        section_collision = next(c for c in collisions if c.base_id == 'section')
        self.assertEqual(len(section_collision.conflicting_files), 1)
        self.assertIn('file1.adoc', section_collision.conflicting_files)

    def test_generate_report(self):
        """Test report generation."""
        # Add some test data
        self.analyzer.file_analyses = [
            FileAnalysis(
                filepath='file1.adoc',
                context_attributes=['banana'],
                ids_with_context=[
                    IDWithContext('topic_banana', 'topic', 'banana', 'file1.adoc', 1)
                ],
                xref_usages=[
                    XrefUsage('other_topic', '', 'file1.adoc', 5, 'xref:other_topic[Other]')
                ],
                link_usages=[]
            )
        ]
        
        self.analyzer.all_ids = {
            'topic': [
                IDWithContext('topic_banana', 'topic', 'banana', 'file1.adoc', 1)
            ]
        }
        
        self.analyzer.all_xrefs = [
            XrefUsage('other_topic', '', 'file1.adoc', 5, 'xref:other_topic[Other]')
        ]
        
        report = self.analyzer.generate_report()
        
        # Check report contents
        self.assertEqual(report.total_files_scanned, 1)
        self.assertEqual(report.files_with_context_ids, 1)
        self.assertEqual(report.total_context_ids, 1)
        self.assertEqual(report.total_xrefs, 1)
        self.assertEqual(report.total_links, 0)
        self.assertEqual(len(report.potential_collisions), 0)
        self.assertEqual(len(report.file_analyses), 1)

    def test_format_text_report(self):
        """Test text report formatting."""
        # Create a test report
        report = AnalysisReport(
            total_files_scanned=2,
            files_with_context_ids=1,
            total_context_ids=3,
            total_xrefs=5,
            total_links=2,
            potential_collisions=[
                CollisionReport(
                    base_id='topic',
                    conflicting_files=['file1.adoc', 'file2.adoc'],
                    suggested_resolution='Consider renaming to topic-1, topic-2, etc.'
                )
            ],
            file_analyses=[
                FileAnalysis(
                    filepath='file1.adoc',
                    context_attributes=['banana'],
                    ids_with_context=[
                        IDWithContext('topic_banana', 'topic', 'banana', 'file1.adoc', 1)
                    ],
                    xref_usages=[],
                    link_usages=[]
                )
            ]
        )
        
        # Test basic report
        text_report = format_text_report(report)
        self.assertIn('=== Context Migration Analysis Report ===', text_report)
        self.assertIn('Files Scanned: 2', text_report)
        self.assertIn('Files with Context IDs: 1', text_report)
        self.assertIn('Total IDs with _{context}: 3', text_report)
        self.assertIn('Total xrefs found: 5', text_report)
        self.assertIn('Total links found: 2', text_report)
        self.assertIn('Base ID \'topic\'', text_report)
        
        # Test detailed report
        detailed_report = format_text_report(report, detailed=True)
        self.assertIn('=== Files Requiring Migration ===', detailed_report)
        self.assertIn('file1.adoc:', detailed_report)
        self.assertIn('[id="topic_banana"] → [id="topic"] (line 1)', detailed_report)
        
        # Test collisions-only report
        collisions_report = format_text_report(report, collisions_only=True)
        self.assertIn('=== Context Migration Collision Analysis ===', collisions_report)
        self.assertIn('Base ID \'topic\'', collisions_report)
        self.assertNotIn('Files Scanned:', collisions_report)


@unittest.skipIf(ContextAnalyzer is None, "ContextAnalyzer plugin could not be imported")
class TestDataStructures(unittest.TestCase):
    """Test cases for the data structures used by ContextAnalyzer."""

    def test_id_with_context_creation(self):
        """Test IDWithContext data structure."""
        id_obj = IDWithContext(
            id_value='topic_banana',
            base_id='topic',
            context_value='banana',
            filepath='test.adoc',
            line_number=1
        )
        
        self.assertEqual(id_obj.id_value, 'topic_banana')
        self.assertEqual(id_obj.base_id, 'topic')
        self.assertEqual(id_obj.context_value, 'banana')
        self.assertEqual(id_obj.filepath, 'test.adoc')
        self.assertEqual(id_obj.line_number, 1)

    def test_xref_usage_creation(self):
        """Test XrefUsage data structure."""
        xref_obj = XrefUsage(
            target_id='section_id',
            target_file='file.adoc',
            filepath='test.adoc',
            line_number=5,
            full_match='xref:file.adoc#section_id[Link]'
        )
        
        self.assertEqual(xref_obj.target_id, 'section_id')
        self.assertEqual(xref_obj.target_file, 'file.adoc')
        self.assertEqual(xref_obj.filepath, 'test.adoc')
        self.assertEqual(xref_obj.line_number, 5)
        self.assertEqual(xref_obj.full_match, 'xref:file.adoc#section_id[Link]')

    def test_collision_report_creation(self):
        """Test CollisionReport data structure."""
        collision_obj = CollisionReport(
            base_id='topic',
            conflicting_files=['file1.adoc', 'file2.adoc'],
            suggested_resolution='Consider renaming'
        )
        
        self.assertEqual(collision_obj.base_id, 'topic')
        self.assertEqual(collision_obj.conflicting_files, ['file1.adoc', 'file2.adoc'])
        self.assertEqual(collision_obj.suggested_resolution, 'Consider renaming')

    def test_file_analysis_creation(self):
        """Test FileAnalysis data structure."""
        file_analysis = FileAnalysis(
            filepath='test.adoc',
            context_attributes=['banana'],
            ids_with_context=[],
            xref_usages=[],
            link_usages=[]
        )
        
        self.assertEqual(file_analysis.filepath, 'test.adoc')
        self.assertEqual(file_analysis.context_attributes, ['banana'])
        self.assertEqual(len(file_analysis.ids_with_context), 0)
        self.assertEqual(len(file_analysis.xref_usages), 0)
        self.assertEqual(len(file_analysis.link_usages), 0)

    def test_analysis_report_creation(self):
        """Test AnalysisReport data structure."""
        analysis_report = AnalysisReport(
            total_files_scanned=10,
            files_with_context_ids=5,
            total_context_ids=15,
            total_xrefs=30,
            total_links=8,
            potential_collisions=[],
            file_analyses=[]
        )
        
        self.assertEqual(analysis_report.total_files_scanned, 10)
        self.assertEqual(analysis_report.files_with_context_ids, 5)
        self.assertEqual(analysis_report.total_context_ids, 15)
        self.assertEqual(analysis_report.total_xrefs, 30)
        self.assertEqual(analysis_report.total_links, 8)
        self.assertEqual(len(analysis_report.potential_collisions), 0)
        self.assertEqual(len(analysis_report.file_analyses), 0)


@unittest.skipIf(ContextAnalyzer is None, "ContextAnalyzer plugin could not be imported")
class TestIntegration(unittest.TestCase):
    """Integration tests for the ContextAnalyzer plugin."""

    def test_analyze_directory_with_multiple_files(self):
        """Test analyzing a directory with multiple files."""
        # Create temporary directory within current working directory
        import tempfile
        temp_dir = tempfile.mkdtemp(dir='.')
        
        try:
            # Create test files
            file1_path = os.path.join(temp_dir, 'file1.adoc')
            file2_path = os.path.join(temp_dir, 'file2.adoc')
            
            with open(file1_path, 'w') as f:
                f.write("""= File 1

:context: banana

[id="topic_banana"]
== Topic

See xref:section_apple[Section].
""")
            
            with open(file2_path, 'w') as f:
                f.write("""= File 2

:context: apple

[id="section_apple"]
== Section

See xref:topic_banana[Topic].
""")
            
            analyzer = ContextAnalyzer()
            report = analyzer.analyze_directory(temp_dir)
            
            # Check results
            self.assertEqual(report.total_files_scanned, 2)
            self.assertEqual(report.files_with_context_ids, 2)
            self.assertEqual(report.total_context_ids, 2)
            self.assertEqual(report.total_xrefs, 2)
            self.assertEqual(len(report.potential_collisions), 0)
            
        finally:
            # Clean up
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_analyze_directory_with_collisions(self):
        """Test analyzing a directory with ID collisions."""
        # Create temporary directory within current working directory
        import tempfile
        temp_dir = tempfile.mkdtemp(dir='.')
        
        try:
            # Create test files with colliding IDs
            file1_path = os.path.join(temp_dir, 'file1.adoc')
            file2_path = os.path.join(temp_dir, 'file2.adoc')
            
            with open(file1_path, 'w') as f:
                f.write("""= File 1

:context: banana

[id="topic_banana"]
== Topic
""")
            
            with open(file2_path, 'w') as f:
                f.write("""= File 2

:context: apple

[id="topic_apple"]
== Topic
""")
            
            analyzer = ContextAnalyzer()
            report = analyzer.analyze_directory(temp_dir)
            
            # Check for collision detection
            self.assertEqual(len(report.potential_collisions), 1)
            collision = report.potential_collisions[0]
            self.assertEqual(collision.base_id, 'topic')
            self.assertEqual(len(collision.conflicting_files), 2)
            
        finally:
            # Clean up
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()