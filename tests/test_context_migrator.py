"""
Test suite for the ContextMigrator plugin.

This script tests the context migration functionality including:
- ID migration and collision resolution
- Xref and link updates
- Backup creation and restoration
- Validation and error handling
- Dry-run mode

To run: python3 -m pytest tests/test_context_migrator.py -v
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import shutil
import json

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from asciidoc_dita_toolkit.asciidoc_dita.plugins.ContextMigrator import (
        ContextMigrator, MigrationOptions, IDChange, XrefChange, 
        FileMigrationResult, ValidationResult, MigrationResult,
        format_migration_report
    )
except ImportError as e:
    print(f"Warning: Could not import ContextMigrator plugin: {e}")
    ContextMigrator = None


@unittest.skipIf(ContextMigrator is None, "ContextMigrator plugin could not be imported")
class TestContextMigrator(unittest.TestCase):
    """Test cases for the ContextMigrator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp(dir='.')
        self.options = MigrationOptions(
            dry_run=False,
            create_backups=True,
            backup_dir=os.path.join(self.temp_dir, '.backups'),
            resolve_collisions=True,
            validate_after=False
        )
        self.migrator = ContextMigrator(self.options)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_migrator_initialization(self):
        """Test that migrator initializes with correct options and patterns."""
        self.assertIsNotNone(self.migrator.id_with_context_regex)
        self.assertIsNotNone(self.migrator.xref_regex)
        self.assertIsNotNone(self.migrator.link_regex)
        self.assertIsNotNone(self.migrator.context_attr_regex)
        self.assertEqual(self.migrator.options.dry_run, False)
        self.assertEqual(self.migrator.options.create_backups, True)
        self.assertEqual(self.migrator.options.resolve_collisions, True)
        self.assertEqual(len(self.migrator.id_mappings), 0)
        self.assertEqual(len(self.migrator.file_id_map), 0)

    def test_id_with_context_regex(self):
        """Test ID with context regex pattern matching."""
        test_cases = [
            ('[id="topic_banana"]', ('topic', 'banana')),
            ('[id="installing-edge_ocp4"]', ('installing-edge', 'ocp4')),
            ('[id="section_test-context"]', ('section', 'test-context')),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                match = self.migrator.id_with_context_regex.search(input_text)
                self.assertIsNotNone(match)
                self.assertEqual(match.group(1), expected[0])
                self.assertEqual(match.group(2), expected[1])

    def test_create_backup(self):
        """Test backup creation functionality."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, 'test.adoc')
        with open(test_file, 'w') as f:
            f.write('= Test Document\n\n[id="topic_banana"]\n== Topic\n')

        # Create backup
        backup_path = self.migrator.create_backup(test_file)
        
        # Verify backup was created
        self.assertTrue(os.path.exists(backup_path))
        
        # Verify backup content matches original
        with open(backup_path, 'r') as f:
            backup_content = f.read()
        with open(test_file, 'r') as f:
            original_content = f.read()
        
        self.assertEqual(backup_content, original_content)

    def test_create_backup_disabled(self):
        """Test backup creation when disabled."""
        self.migrator.options.create_backups = False
        
        # Create a test file
        test_file = os.path.join(self.temp_dir, 'test.adoc')
        with open(test_file, 'w') as f:
            f.write('= Test Document\n')

        # Create backup (should return empty string)
        backup_path = self.migrator.create_backup(test_file)
        self.assertEqual(backup_path, "")

    def test_resolve_id_collisions(self):
        """Test ID collision resolution."""
        existing_ids = {'topic', 'section', 'topic-1'}
        
        # Test no collision
        result = self.migrator.resolve_id_collisions('unique', existing_ids)
        self.assertEqual(result, 'unique')
        
        # Test collision resolution
        result = self.migrator.resolve_id_collisions('topic', existing_ids)
        self.assertEqual(result, 'topic-2')  # topic-1 already exists
        
        # Test with collision resolution disabled
        self.migrator.options.resolve_collisions = False
        result = self.migrator.resolve_id_collisions('topic', existing_ids)
        self.assertEqual(result, 'topic')  # Returns original even with collision

    def test_remove_context_from_ids(self):
        """Test context removal from IDs."""
        content = """= Test Document

:context: banana

[id="topic_banana"]
== Topic

Some content here.

[id="section_banana"]
=== Section

More content.
"""
        
        modified_content, changes = self.migrator.remove_context_from_ids(content, 'test.adoc')
        
        # Check that changes were made
        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0].old_id, 'topic_banana')
        self.assertEqual(changes[0].new_id, 'topic')
        self.assertEqual(changes[1].old_id, 'section_banana')
        self.assertEqual(changes[1].new_id, 'section')
        
        # Check that content was modified
        self.assertIn('[id="topic"]', modified_content)
        self.assertIn('[id="section"]', modified_content)
        self.assertNotIn('[id="topic_banana"]', modified_content)
        self.assertNotIn('[id="section_banana"]', modified_content)

    def test_remove_context_from_ids_with_collisions(self):
        """Test context removal with ID collisions."""
        content = """= Test Document

:context: banana

[id="topic_banana"]
== Topic

:context: apple

[id="topic_apple"]
== Another Topic
"""
        
        modified_content, changes = self.migrator.remove_context_from_ids(content, 'test.adoc')
        
        # Check that collisions were resolved
        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0].old_id, 'topic_banana')
        self.assertEqual(changes[0].new_id, 'topic')
        self.assertEqual(changes[1].old_id, 'topic_apple')
        self.assertEqual(changes[1].new_id, 'topic-1')  # Collision resolved
        
        # Check that content was modified with unique IDs
        self.assertIn('[id="topic"]', modified_content)
        self.assertIn('[id="topic-1"]', modified_content)

    def test_update_xrefs_and_links(self):
        """Test xref and link updates."""
        # Set up ID mappings
        self.migrator.id_mappings = {
            'topic_banana': 'topic',
            'section_apple': 'section'
        }
        
        content = """= Test Document

See xref:topic_banana[Topic] and xref:section_apple[Section].

Also link:http://example.com#topic_banana[External Link].
"""
        
        modified_content, changes = self.migrator.update_xrefs_and_links(content, 'test.adoc')
        
        # Check that changes were made (2 xrefs + 1 link = 3 total)
        self.assertEqual(len(changes), 3)
        
        # Find the xref changes
        xref_changes = [c for c in changes if c.old_xref.startswith('xref:')]
        self.assertEqual(len(xref_changes), 2)
        
        # Check specific xref changes
        topic_change = next(c for c in xref_changes if 'topic_banana[Topic]' in c.old_xref)
        self.assertEqual(topic_change.old_xref, 'xref:topic_banana[Topic]')
        self.assertEqual(topic_change.new_xref, 'xref:topic[Topic]')
        
        section_change = next(c for c in xref_changes if 'section_apple[Section]' in c.old_xref)
        self.assertEqual(section_change.old_xref, 'xref:section_apple[Section]')
        self.assertEqual(section_change.new_xref, 'xref:section[Section]')
        
        # Find the link change
        link_changes = [c for c in changes if c.old_xref.startswith('link:')]
        self.assertEqual(len(link_changes), 1)
        self.assertEqual(link_changes[0].old_xref, 'link:http://example.com#topic_banana[External Link]')
        self.assertEqual(link_changes[0].new_xref, 'link:http://example.com#topic[External Link]')
        
        # Check that content was modified
        self.assertIn('xref:topic[Topic]', modified_content)
        self.assertIn('xref:section[Section]', modified_content)
        self.assertIn('link:http://example.com#topic[External Link]', modified_content)
        self.assertNotIn('xref:topic_banana[Topic]', modified_content)
        self.assertNotIn('xref:section_apple[Section]', modified_content)
        self.assertNotIn('link:http://example.com#topic_banana[External Link]', modified_content)

    def test_validate_migration(self):
        """Test migration validation."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, 'test.adoc')
        with open(test_file, 'w') as f:
            f.write("""= Test Document

[id="topic"]
== Topic

See xref:section[Section].
""")
        
        # Set up file ID map
        self.migrator.file_id_map = {
            'topic': test_file,
            'section': test_file
        }
        
        result = self.migrator.validate_migration(test_file)
        
        # Check validation results
        self.assertEqual(result.filepath, test_file)
        self.assertTrue(result.valid)
        self.assertEqual(len(result.broken_xrefs), 0)
        self.assertEqual(len(result.warnings), 0)

    def test_validate_migration_with_broken_xrefs(self):
        """Test migration validation with broken xrefs."""
        # Create a test file with broken xref
        test_file = os.path.join(self.temp_dir, 'test.adoc')
        with open(test_file, 'w') as f:
            f.write("""= Test Document

[id="topic"]
== Topic

See xref:missing_section[Missing Section].
""")
        
        # Set up file ID map (without missing_section)
        self.migrator.file_id_map = {
            'topic': test_file
        }
        
        result = self.migrator.validate_migration(test_file)
        
        # Check validation results
        self.assertEqual(result.filepath, test_file)
        self.assertFalse(result.valid)
        self.assertEqual(len(result.broken_xrefs), 1)
        self.assertEqual(result.broken_xrefs[0], 'missing_section')

    def test_migrate_file_success(self):
        """Test successful file migration."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, 'test.adoc')
        with open(test_file, 'w') as f:
            f.write("""= Test Document

:context: banana

[id="topic_banana"]
== Topic

See xref:section_banana[Section].

[id="section_banana"]
=== Section

Content here.
""")
        
        result = self.migrator.migrate_file(test_file)
        
        # Check migration results
        self.assertTrue(result.success)
        self.assertEqual(result.filepath, test_file)
        self.assertEqual(len(result.id_changes), 2)
        self.assertEqual(len(result.xref_changes), 1)
        self.assertEqual(len(result.errors), 0)
        self.assertNotEqual(result.backup_path, "")
        
        # Check that file was modified
        with open(test_file, 'r') as f:
            modified_content = f.read()
        
        self.assertIn('[id="topic"]', modified_content)
        self.assertIn('[id="section"]', modified_content)
        self.assertIn('xref:section[Section]', modified_content)
        self.assertNotIn('[id="topic_banana"]', modified_content)
        self.assertNotIn('[id="section_banana"]', modified_content)

    def test_migrate_file_dry_run(self):
        """Test file migration in dry-run mode."""
        self.migrator.options.dry_run = True
        
        # Create a test file
        test_file = os.path.join(self.temp_dir, 'test.adoc')
        original_content = """= Test Document

:context: banana

[id="topic_banana"]
== Topic
"""
        
        with open(test_file, 'w') as f:
            f.write(original_content)
        
        result = self.migrator.migrate_file(test_file)
        
        # Check migration results
        self.assertTrue(result.success)
        self.assertEqual(len(result.id_changes), 1)
        
        # Check that file was NOT modified
        with open(test_file, 'r') as f:
            current_content = f.read()
        
        self.assertEqual(current_content, original_content)

    def test_migrate_file_error_handling(self):
        """Test error handling during file migration."""
        # Try to migrate non-existent file
        result = self.migrator.migrate_file('/nonexistent/file.adoc')
        
        # Check error handling
        self.assertFalse(result.success)
        self.assertEqual(len(result.errors), 1)
        self.assertIn('Error migrating', result.errors[0])

    def test_migrate_directory(self):
        """Test directory migration."""
        # Create test files using a subdirectory within current working directory
        test_subdir = os.path.join(self.temp_dir, 'test_subdir')
        os.makedirs(test_subdir, exist_ok=True)
        
        file1 = os.path.join(test_subdir, 'file1.adoc')
        file2 = os.path.join(test_subdir, 'file2.adoc')
        
        with open(file1, 'w') as f:
            f.write("""= File 1

:context: banana

[id="topic_banana"]
== Topic
""")
        
        with open(file2, 'w') as f:
            f.write("""= File 2

:context: apple

[id="section_apple"]
== Section
""")
        
        result = self.migrator.migrate_directory(test_subdir)
        
        # Check migration results
        self.assertEqual(result.total_files_processed, 2)
        self.assertEqual(result.successful_migrations, 2)
        self.assertEqual(result.failed_migrations, 0)
        self.assertEqual(len(result.file_results), 2)


@unittest.skipIf(ContextMigrator is None, "ContextMigrator plugin could not be imported")
class TestMigrationOptions(unittest.TestCase):
    """Test cases for MigrationOptions data structure."""

    def test_default_options(self):
        """Test default migration options."""
        options = MigrationOptions()
        
        self.assertFalse(options.dry_run)
        self.assertTrue(options.create_backups)
        self.assertEqual(options.backup_dir, '.migration_backups')
        self.assertTrue(options.resolve_collisions)
        self.assertTrue(options.validate_after)

    def test_custom_options(self):
        """Test custom migration options."""
        options = MigrationOptions(
            dry_run=True,
            create_backups=False,
            backup_dir='custom_backups',
            resolve_collisions=False,
            validate_after=False
        )
        
        self.assertTrue(options.dry_run)
        self.assertFalse(options.create_backups)
        self.assertEqual(options.backup_dir, 'custom_backups')
        self.assertFalse(options.resolve_collisions)
        self.assertFalse(options.validate_after)


@unittest.skipIf(ContextMigrator is None, "ContextMigrator plugin could not be imported")
class TestDataStructures(unittest.TestCase):
    """Test cases for the data structures used by ContextMigrator."""

    def test_id_change_creation(self):
        """Test IDChange data structure."""
        change = IDChange(
            old_id='topic_banana',
            new_id='topic',
            line_number=5
        )
        
        self.assertEqual(change.old_id, 'topic_banana')
        self.assertEqual(change.new_id, 'topic')
        self.assertEqual(change.line_number, 5)

    def test_xref_change_creation(self):
        """Test XrefChange data structure."""
        change = XrefChange(
            old_xref='topic_banana[Topic]',
            new_xref='topic[Topic]',
            line_number=10
        )
        
        self.assertEqual(change.old_xref, 'topic_banana[Topic]')
        self.assertEqual(change.new_xref, 'topic[Topic]')
        self.assertEqual(change.line_number, 10)

    def test_file_migration_result_creation(self):
        """Test FileMigrationResult data structure."""
        result = FileMigrationResult(
            filepath='test.adoc',
            success=True,
            id_changes=[],
            xref_changes=[],
            errors=[],
            backup_path='/backup/test.adoc'
        )
        
        self.assertEqual(result.filepath, 'test.adoc')
        self.assertTrue(result.success)
        self.assertEqual(len(result.id_changes), 0)
        self.assertEqual(len(result.xref_changes), 0)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(result.backup_path, '/backup/test.adoc')

    def test_validation_result_creation(self):
        """Test ValidationResult data structure."""
        result = ValidationResult(
            filepath='test.adoc',
            valid=True,
            broken_xrefs=[],
            warnings=['Warning message']
        )
        
        self.assertEqual(result.filepath, 'test.adoc')
        self.assertTrue(result.valid)
        self.assertEqual(len(result.broken_xrefs), 0)
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(result.warnings[0], 'Warning message')

    def test_migration_result_creation(self):
        """Test MigrationResult data structure."""
        result = MigrationResult(
            total_files_processed=5,
            successful_migrations=4,
            failed_migrations=1,
            file_results=[],
            validation_results=[],
            backup_directory='/backups'
        )
        
        self.assertEqual(result.total_files_processed, 5)
        self.assertEqual(result.successful_migrations, 4)
        self.assertEqual(result.failed_migrations, 1)
        self.assertEqual(len(result.file_results), 0)
        self.assertEqual(len(result.validation_results), 0)
        self.assertEqual(result.backup_directory, '/backups')


@unittest.skipIf(ContextMigrator is None, "ContextMigrator plugin could not be imported")
class TestReportFormatting(unittest.TestCase):
    """Test cases for migration report formatting."""

    def test_format_migration_report(self):
        """Test migration report formatting."""
        # Create a test migration result
        id_change = IDChange('topic_banana', 'topic', 1)
        xref_change = XrefChange('topic_banana[Topic]', 'topic[Topic]', 5)
        
        file_result = FileMigrationResult(
            filepath='test.adoc',
            success=True,
            id_changes=[id_change],
            xref_changes=[xref_change],
            errors=[],
            backup_path='/backup/test.adoc'
        )
        
        validation_result = ValidationResult(
            filepath='test.adoc',
            valid=True,
            broken_xrefs=[],
            warnings=['Minor warning']
        )
        
        migration_result = MigrationResult(
            total_files_processed=1,
            successful_migrations=1,
            failed_migrations=0,
            file_results=[file_result],
            validation_results=[validation_result],
            backup_directory='/backups'
        )
        
        report = format_migration_report(migration_result)
        
        # Check report contents
        self.assertIn('=== Context Migration Report ===', report)
        self.assertIn('Total files processed: 1', report)
        self.assertIn('Successful migrations: 1', report)
        self.assertIn('Failed migrations: 0', report)
        self.assertIn('Backup directory: /backups', report)
        self.assertIn('test.adoc: SUCCESS', report)
        self.assertIn('ID Changes: 1', report)
        self.assertIn('topic_banana → topic (line 1)', report)
        self.assertIn('Xref Changes: 1', report)
        self.assertIn('topic_banana[Topic] → topic[Topic] (line 5)', report)
        self.assertIn('=== Validation Results ===', report)
        self.assertIn('test.adoc: VALID', report)
        self.assertIn('Minor warning', report)


@unittest.skipIf(ContextMigrator is None, "ContextMigrator plugin could not be imported")
class TestIntegration(unittest.TestCase):
    """Integration tests for the ContextMigrator plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp(dir='.')

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_end_to_end_migration(self):
        """Test complete end-to-end migration process."""
        # Create test files
        file1 = os.path.join(self.temp_dir, 'file1.adoc')
        file2 = os.path.join(self.temp_dir, 'file2.adoc')
        
        with open(file1, 'w') as f:
            f.write("""= File 1

:context: banana

[id="topic_banana"]
== Topic

See xref:section_apple[Section in File 2].
""")
        
        with open(file2, 'w') as f:
            f.write("""= File 2

:context: apple

[id="section_apple"]
== Section

See xref:topic_banana[Topic in File 1].
""")
        
        # Set up migration options
        options = MigrationOptions(
            dry_run=False,
            create_backups=True,
            backup_dir=os.path.join(self.temp_dir, '.backups'),
            resolve_collisions=True,
            validate_after=True
        )
        
        migrator = ContextMigrator(options)
        result = migrator.migrate_directory(self.temp_dir)
        
        # Check migration results
        self.assertEqual(result.total_files_processed, 2)
        self.assertEqual(result.successful_migrations, 2)
        self.assertEqual(result.failed_migrations, 0)
        
        # Check that files were modified correctly
        with open(file1, 'r') as f:
            content1 = f.read()
        with open(file2, 'r') as f:
            content2 = f.read()
        
        self.assertIn('[id="topic"]', content1)
        self.assertIn('[id="section"]', content2)
        self.assertIn('xref:section[Section in File 2]', content1)
        self.assertIn('xref:topic[Topic in File 1]', content2)
        
        # Check that backups were created
        backup_dir = os.path.join(self.temp_dir, '.backups')
        self.assertTrue(os.path.exists(backup_dir))
        self.assertTrue(os.path.exists(os.path.join(backup_dir, 'file1.adoc')))
        self.assertTrue(os.path.exists(os.path.join(backup_dir, 'file2.adoc')))

    def test_migration_with_collisions(self):
        """Test migration with ID collisions."""
        # Create test files with colliding IDs
        file1 = os.path.join(self.temp_dir, 'file1.adoc')
        file2 = os.path.join(self.temp_dir, 'file2.adoc')
        
        with open(file1, 'w') as f:
            f.write("""= File 1

:context: banana

[id="topic_banana"]
== Topic
""")
        
        with open(file2, 'w') as f:
            f.write("""= File 2

:context: apple

[id="topic_apple"]
== Topic
""")
        
        # Set up migration options
        options = MigrationOptions(
            dry_run=False,
            create_backups=False,
            resolve_collisions=True,
            validate_after=False
        )
        
        migrator = ContextMigrator(options)
        result = migrator.migrate_directory(self.temp_dir)
        
        # Check migration results
        self.assertEqual(result.total_files_processed, 2)
        self.assertEqual(result.successful_migrations, 2)
        
        # Check that collisions were resolved
        with open(file1, 'r') as f:
            content1 = f.read()
        with open(file2, 'r') as f:
            content2 = f.read()
        
        # One should be 'topic', the other 'topic-1'
        id_contents = content1 + content2
        self.assertIn('[id="topic"]', id_contents)
        self.assertIn('[id="topic-1"]', id_contents)


def main():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()