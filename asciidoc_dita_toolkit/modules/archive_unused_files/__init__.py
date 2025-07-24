"""
Plugin for the AsciiDoc DITA toolkit: ArchiveUnusedFiles

This plugin scans for AsciiDoc files not referenced by any other AsciiDoc file
in the project and optionally archives them.
"""

__description__ = "Archive unused AsciiDoc files"

import logging
import os
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Set, Tuple

from asciidoc_dita_toolkit.asciidoc_dita.cli_utils import common_arg_parser
from asciidoc_dita_toolkit.asciidoc_dita.plugin_manager import is_plugin_enabled
from asciidoc_dita_toolkit.asciidoc_dita.workflow_utils import process_adoc_files

# Import ADTModule from core
try:
    from asciidoc_dita_toolkit.adt_core.module_sequencer import ADTModule
    ADT_MODULE_AVAILABLE = True
except ImportError as e:
    raise ImportError(
        f"Failed to import ADTModule from asciidoc_dita_toolkit.adt_core.module_sequencer: {e}. "
        f"This is required for ArchiveUnusedFiles module to function properly."
    )

# Setup logging
logger = logging.getLogger(__name__)


class UnusedFilesDetector:
    """
    Detects unused AsciiDoc files by analyzing include references.

    This class scans directories for AsciiDoc files and determines which files
    are not referenced by any other files in the project using include:: directives.
    """

    def __init__(self, scan_dirs: List[str], exclude_dirs: Optional[List[str]] = None,
                 exclude_files: Optional[List[str]] = None):
        """
        Initialize the detector with configuration.

        Args:
            scan_dirs: Directories to scan for AsciiDoc files
            exclude_dirs: Directories to exclude from scanning
            exclude_files: Specific files to exclude from scanning
        """
        self.scan_dirs = scan_dirs
        self.exclude_dirs = set(os.path.abspath(os.path.normpath(d)) for d in (exclude_dirs or []))
        self.exclude_files = set(os.path.abspath(os.path.normpath(f)) for f in (exclude_files or []))
        self.include_pattern = re.compile(r'include::(.+?)\[')

    def collect_files(self, directories: List[str], extensions: Set[str]) -> List[str]:
        """
        Recursively collect files with given extensions from directories.

        Args:
            directories: List of directories to scan
            extensions: Set of file extensions to collect (e.g., {'.adoc'})

        Returns:
            List of normalized file paths
        """
        found_files = []

        for base_dir in directories:
            if not os.path.exists(base_dir):
                logger.warning(f"Directory does not exist: {base_dir}")
                continue

            for root, dirs, files in os.walk(base_dir):
                abs_root = os.path.abspath(root)

                # Exclude directories by absolute path and skip symlinks
                dirs[:] = [d for d in dirs
                          if not os.path.islink(os.path.join(root, d))
                          and os.path.abspath(os.path.join(root, d)) not in self.exclude_dirs]

                for f in files:
                    file_path = os.path.normpath(os.path.join(root, f))
                    abs_file_path = os.path.abspath(file_path)

                    # Skip symlinks and excluded files
                    if os.path.islink(file_path) or abs_file_path in self.exclude_files:
                        continue

                    if os.path.splitext(f)[1].lower() in extensions:
                        found_files.append(file_path)

        return list(dict.fromkeys(found_files))  # Remove duplicates while preserving order

    def find_included_files(self, search_dirs: List[str]) -> Set[str]:
        """
        Find all files referenced by include:: directives.

        Args:
            search_dirs: Directories to search for files with include directives

        Returns:
            Set of included file basenames
        """
        included_files = set()
        adoc_files = self.collect_files(search_dirs, {'.adoc'})

        for file_path in adoc_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    includes = self.include_pattern.findall(content)
                    # Extract just the basename of included files
                    included_files.update(os.path.basename(include) for include in includes)
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")

        return included_files

    def find_unused_files(self) -> List[str]:
        """
        Find AsciiDoc files that are not referenced by any other files.

        Returns:
            List of unused file paths
        """
        # Collect all AsciiDoc files from scan directories
        asciidoc_files = self.collect_files(self.scan_dirs, {'.adoc'})

        # Find all included files by searching entire project
        included_files = self.find_included_files(['.'])

        # Determine unused files
        unused_files = [f for f in asciidoc_files
                       if os.path.basename(f) not in included_files]

        # Remove duplicates while preserving order
        return list(dict.fromkeys(unused_files))


class UnusedFilesArchiver:
    """
    Archives unused files by creating manifests and optionally ZIP archives.
    """

    def __init__(self, archive_dir: str = './archive'):
        """
        Initialize the archiver.

        Args:
            archive_dir: Directory to store archives and manifests
        """
        self.archive_dir = archive_dir

    def write_manifest_and_archive(self, unused_files: List[str],
                                 manifest_prefix: str = 'unused-files',
                                 archive_prefix: str = 'unused-files',
                                 archive: bool = False,
                                 verbose: bool = False) -> Tuple[Optional[str], Optional[str]]:
        """
        Write a manifest of unused files and optionally archive them.

        Args:
            unused_files: List of unused file paths
            manifest_prefix: Prefix for manifest filename
            archive_prefix: Prefix for archive filename
            archive: Whether to create ZIP archive and delete files
            verbose: Whether to print file names to console

        Returns:
            Tuple of (manifest_path, archive_path)
        """
        if not unused_files:
            logger.info("No unused files found. No manifest or ZIP archive created.")
            return None, None

        now = datetime.now()
        datetime_str = now.strftime('%Y-%m-%d_%H%M%S')

        # Create archive directory
        os.makedirs(self.archive_dir, exist_ok=True)

        # Write manifest
        manifest_filename = f'{manifest_prefix}-{datetime_str}.txt'
        manifest_path = os.path.join(self.archive_dir, manifest_filename)

        with open(manifest_path, 'w', encoding='utf-8') as f:
            for file_path in unused_files:
                if verbose:
                    print(f"Found unused file: {file_path}")  # User feedback
                f.write(file_path + '\n')

        logger.info(f"Manifest written to: {manifest_path}")

        archive_path = None
        if archive:
            archive_filename = f"{archive_prefix}-{datetime_str}.zip"
            archive_path = os.path.join(self.archive_dir, archive_filename)

            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in unused_files:
                    arcname = os.path.relpath(file_path)
                    logger.info(f"Archiving: {file_path} -> {archive_path} ({arcname})")
                    zipf.write(file_path, arcname)
                    os.remove(file_path)

            logger.info(f"Archive created: {archive_path}")

        return manifest_path, archive_path


def process_unused_files(scan_dirs: List[str],
                        archive_dir: str = './archive',
                        archive: bool = False,
                        exclude_dirs: Optional[List[str]] = None,
                        exclude_files: Optional[List[str]] = None,
                        exclude_list: Optional[str] = None,
                        verbose: bool = False) -> Dict[str, Any]:
    """
    Main processing function to find and optionally archive unused files.

    Args:
        scan_dirs: Directories to scan for AsciiDoc files
        archive_dir: Directory to store archives
        archive: Whether to archive and delete unused files
        exclude_dirs: Directories to exclude
        exclude_files: Files to exclude
        exclude_list: Path to file containing exclusions

    Returns:
        Dictionary with processing results
    """
    # Process exclusion list file
    final_exclude_dirs = list(exclude_dirs or [])
    final_exclude_files = list(exclude_files or [])

    if exclude_list and os.path.isfile(exclude_list):
        try:
            with open(exclude_list, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if os.path.isdir(line):
                        final_exclude_dirs.append(line)
                    else:
                        final_exclude_files.append(line)
        except Exception as e:
            logger.error(f"Error reading exclude list file {exclude_list}: {e}")

    # Detect unused files
    detector = UnusedFilesDetector(scan_dirs, final_exclude_dirs, final_exclude_files)
    unused_files = detector.find_unused_files()

    # Archive if requested
    archiver = UnusedFilesArchiver(archive_dir)
    manifest_path, archive_path = archiver.write_manifest_and_archive(
        unused_files, archive=archive, verbose=verbose
    )

    return {
        'unused_files': unused_files,
        'unused_count': len(unused_files),
        'manifest_path': manifest_path,
        'archive_path': archive_path,
        'files_archived': len(unused_files) if archive else 0
    }


class ArchiveUnusedFilesModule(ADTModule):
    """
    ADTModule implementation for ArchiveUnusedFiles plugin.

    Scans for AsciiDoc files not referenced by any other AsciiDoc file
    in the project and optionally archives them.
    """

    @property
    def name(self) -> str:
        """Module name identifier."""
        return "ArchiveUnusedFiles"

    @property
    def version(self) -> str:
        """Module version."""
        return "1.0.0"

    @property
    def dependencies(self) -> List[str]:
        """List of required module names."""
        return []

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the module with configuration."""
        # ArchiveUnusedFiles doesn't require special initialization
        pass

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the module to find and optionally archive unused files.

        Args:
            context: Processing context containing configuration

        Returns:
            Dict containing processing results and statistics
        """
        # Extract configuration from context
        scan_dirs = context.get('scan_dirs', ['./modules', './modules/rn', './assemblies'])
        archive_dir = context.get('archive_dir', './archive')
        archive = context.get('archive', False)
        exclude_dirs = context.get('exclude_dirs', [])
        exclude_files = context.get('exclude_files', [])
        exclude_list = context.get('exclude_list')

        # Process unused files
        results = process_unused_files(
            scan_dirs=scan_dirs,
            archive_dir=archive_dir,
            archive=archive,
            exclude_dirs=exclude_dirs,
            exclude_files=exclude_files,
            exclude_list=exclude_list
        )

        return results


def main():
    """Main entry point for the plugin."""
    parser = common_arg_parser("ArchiveUnusedFiles", __description__)

    # Add plugin-specific arguments
    parser.add_argument(
        '--archive',
        action='store_true',
        help='Move unused files to a dated zip in the archive directory'
    )
    parser.add_argument(
        '--scan-dirs',
        nargs='+',
        default=['./modules', './modules/rn', './assemblies'],
        help='Directories to scan for AsciiDoc files (default: ./modules ./modules/rn ./assemblies)'
    )
    parser.add_argument(
        '--archive-dir',
        default='./archive',
        help='Directory to store archived files (default: ./archive)'
    )
    parser.add_argument(
        '--exclude-dir',
        action='append',
        default=[],
        help='Directory to exclude from scanning (can be used multiple times)'
    )
    parser.add_argument(
        '--exclude-file',
        action='append',
        default=[],
        help='Specific file to exclude (can be used multiple times)'
    )
    parser.add_argument(
        '--exclude-list',
        help='Path to file containing directories/files to exclude, one per line'
    )

    args = parser.parse_args()

    # Check if plugin is enabled
    if not is_plugin_enabled("ArchiveUnusedFiles"):
        logger.info("ArchiveUnusedFiles plugin is disabled. Skipping...")
        return

    # Process unused files
    results = process_unused_files(
        scan_dirs=args.scan_dirs,
        archive_dir=args.archive_dir,
        archive=args.archive,
        exclude_dirs=args.exclude_dir,
        exclude_files=args.exclude_file,
        exclude_list=args.exclude_list
    )

    # Print summary
    print(f"\nSummary:")
    print(f"  Unused files found: {results['unused_count']}")
    print(f"  Manifest created: {results['manifest_path']}")
    if results['archive_path']:
        print(f"  Archive created: {results['archive_path']}")
        print(f"  Files archived: {results['files_archived']}")


if __name__ == "__main__":
    main()
