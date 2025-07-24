"""
Test for ArchiveUnusedFiles plugin

This test validates that the ArchiveUnusedFiles plugin correctly identifies
unused AsciiDoc files and optionally archives them.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from asciidoc_dita_toolkit.modules.archive_unused_files import (
    UnusedFilesDetector,
    UnusedFilesArchiver,
    process_unused_files,
    ArchiveUnusedFilesModule
)


class TestArchiveUnusedFiles(unittest.TestCase):
    """Test cases for ArchiveUnusedFiles plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.test_dir, ignore_errors=True))

        # Create test directory structure
        modules_dir = os.path.join(self.test_dir, 'modules')
        assemblies_dir = os.path.join(self.test_dir, 'assemblies')
        archive_dir = os.path.join(self.test_dir, 'archive')

        os.makedirs(modules_dir)
        os.makedirs(assemblies_dir)
        os.makedirs(archive_dir)

        # Create test files
        # used.adoc - referenced by master.adoc
        with open(os.path.join(modules_dir, 'used.adoc'), 'w') as f:
            f.write('= Used Module\n\nThis module is used.\n')

        # unused1.adoc - not referenced
        with open(os.path.join(modules_dir, 'unused1.adoc'), 'w') as f:
            f.write('= Unused Module 1\n\nThis module is not used.\n')

        # unused2.adoc - not referenced
        with open(os.path.join(modules_dir, 'unused2.adoc'), 'w') as f:
            f.write('= Unused Module 2\n\nThis module is also not used.\n')

        # master.adoc - references used.adoc
        with open(os.path.join(assemblies_dir, 'master.adoc'), 'w') as f:
            f.write('= Master Assembly\n\ninclude::../modules/used.adoc[]\n')

        self.modules_dir = modules_dir
        self.assemblies_dir = assemblies_dir
        self.archive_dir = archive_dir

    def test_collect_files(self):
        """Test file collection functionality."""
        detector = UnusedFilesDetector([self.modules_dir])
        files = detector.collect_files([self.modules_dir], {'.adoc'})

        # Should find all 3 adoc files in modules
        self.assertEqual(len(files), 3)
        self.assertTrue(any('used.adoc' in f for f in files))
        self.assertTrue(any('unused1.adoc' in f for f in files))
        self.assertTrue(any('unused2.adoc' in f for f in files))

    def test_find_included_files(self):
        """Test finding included files."""
        detector = UnusedFilesDetector([self.modules_dir])
        included = detector.find_included_files([self.test_dir])

        # Should find used.adoc as included
        self.assertIn('used.adoc', included)
        self.assertNotIn('unused1.adoc', included)
        self.assertNotIn('unused2.adoc', included)

    def test_find_unused_files(self):
        """Test finding unused files."""
        # Change to test directory for relative path resolution
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        try:
            detector = UnusedFilesDetector(['modules'])
            unused = detector.find_unused_files()

            # Should find 2 unused files
            self.assertEqual(len(unused), 2)
            self.assertTrue(any('unused1.adoc' in f for f in unused))
            self.assertTrue(any('unused2.adoc' in f for f in unused))
            self.assertFalse(any('used.adoc' in f for f in unused))
        finally:
            os.chdir(original_cwd)

    def test_archiver_manifest_only(self):
        """Test creating manifest without archiving."""
        unused_files = [
            os.path.join(self.modules_dir, 'unused1.adoc'),
            os.path.join(self.modules_dir, 'unused2.adoc')
        ]

        archiver = UnusedFilesArchiver(self.archive_dir)
        manifest_path, archive_path = archiver.write_manifest_and_archive(
            unused_files, archive=False
        )

        # Should create manifest but no archive
        self.assertIsNotNone(manifest_path)
        self.assertIsNone(archive_path)
        self.assertTrue(os.path.exists(manifest_path))

        # Check manifest content
        with open(manifest_path, 'r') as f:
            content = f.read()
            self.assertIn('unused1.adoc', content)
            self.assertIn('unused2.adoc', content)

    def test_process_unused_files_integration(self):
        """Test the complete process_unused_files function."""
        # Change to test directory for relative path resolution
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        try:
            results = process_unused_files(
                scan_dirs=['modules'],
                archive_dir='archive',
                archive=False
            )

            # Verify results
            self.assertEqual(results['unused_count'], 2)
            self.assertIsNotNone(results['manifest_path'])
            self.assertIsNone(results['archive_path'])
            self.assertEqual(results['files_archived'], 0)

        finally:
            os.chdir(original_cwd)

    def test_adt_module_execute(self):
        """Test ADTModule execution."""
        # Change to test directory for relative path resolution
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        try:
            module = ArchiveUnusedFilesModule()

            # Test module properties
            self.assertEqual(module.name, "ArchiveUnusedFiles")
            self.assertEqual(module.version, "1.0.0")
            self.assertEqual(module.dependencies, [])

            # Test execution
            context = {
                'scan_dirs': ['modules'],
                'archive_dir': 'archive',
                'archive': False
            }

            results = module.execute(context)

            # Verify results
            self.assertEqual(results['unused_count'], 2)
            self.assertIsNotNone(results['manifest_path'])

        finally:
            os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()
