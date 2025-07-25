#!/usr/bin/env python3
"""
Archive Unused Files - ADT Module Wrapper

This module provides a command-line interface for the ArchiveUnusedFiles plugin.
It scans for AsciiDoc files not referenced by any other AsciiDoc file
in the project and optionally archives them.
"""

import argparse
import sys
from pathlib import Path

# Try to import from the installed package first, fallback to relative import
try:
    from asciidoc_dita_toolkit.asciidoc_dita.plugins.ArchiveUnusedFiles import (
        process_unused_files,
    )
except ImportError:
    # Fallback for development/testing when package isn't installed
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from asciidoc_dita_toolkit.asciidoc_dita.plugins.ArchiveUnusedFiles import (
        process_unused_files,
    )


def main():
    """Main entry point for the archive unused files module."""
    parser = argparse.ArgumentParser(
        description='Archive unused AsciiDoc files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Find unused files (dry run)
  archive-unused-files

  # Archive unused files
  archive-unused-files --archive

  # Exclude specific directories
  archive-unused-files --exclude-dir ./modules/legacy --exclude-dir ./modules/archive

  # Use custom scan directories
  archive-unused-files --scan-dirs ./docs ./content --archive

  # Use exclusion list file
  archive-unused-files --exclude-list exclusions.txt --archive

EXCLUSION LIST FORMAT:
  The exclusion list file should contain one path per line:
    ./modules/legacy
    ./modules/archive/obsolete.adoc
    # This is a comment
    ./temp
""",
    )

    parser.add_argument(
        '--archive',
        action='store_true',
        help='Move unused files to a dated zip in the archive directory',
    )
    parser.add_argument(
        '--scan-dirs',
        nargs='+',
        default=['./modules', './modules/rn', './assemblies'],
        help='Directories to scan for AsciiDoc files (default: ./modules ./modules/rn ./assemblies)',
    )
    parser.add_argument(
        '--archive-dir',
        default='./archive',
        help='Directory to store archived files (default: ./archive)',
    )
    parser.add_argument(
        '--exclude-dir',
        action='append',
        default=[],
        help='Directory to exclude from scanning (can be used multiple times)',
    )
    parser.add_argument(
        '--exclude-file',
        action='append',
        default=[],
        help='Specific file to exclude (can be used multiple times)',
    )
    parser.add_argument(
        '--exclude-list',
        help='Path to file containing directories/files to exclude, one per line',
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='Enable verbose output'
    )

    args = parser.parse_args()

    # Set up logging level
    import logging

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s',
    )

    try:
        # Process unused files
        results = process_unused_files(
            scan_dirs=args.scan_dirs,
            archive_dir=args.archive_dir,
            archive=args.archive,
            exclude_dirs=args.exclude_dir,
            exclude_files=args.exclude_file,
            exclude_list=args.exclude_list,
        )

        # Print summary
        print(f"\nResults:")
        print(f"  Unused files found: {results['unused_count']}")

        if results['manifest_path']:
            print(f"  Manifest created: {results['manifest_path']}")

        if results['archive_path']:
            print(f"  Archive created: {results['archive_path']}")
            print(f"  Files archived and deleted: {results['files_archived']}")
        elif args.archive:
            print("  No files to archive")
        else:
            print("  Run with --archive to move files to archive")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
