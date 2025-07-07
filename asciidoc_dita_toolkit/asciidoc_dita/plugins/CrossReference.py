"""
Plugin for the AsciiDoc DITA toolkit: CrossReference

This plugin fixes cross-references in AsciiDoc files by updating xref links to include the proper file paths.
It scans for section IDs and updates xref links that point to those IDs but lack the proper file reference.

Original author: Roger Heslop
Integrated into AsciiDoc DITA Toolkit
"""

__description__ = "Fix cross-references in AsciiDoc files by updating xref links to include proper file paths."

import os
import re
import sys
import logging
from typing import Dict, List

from ..cli_utils import common_arg_parser

# Configure logging
logger = logging.getLogger(__name__)


class Highlighter:
    """
    Utility class to modify text output with color codes.
    Provides consistent formatting for warnings, highlights, and bold text.
    """

    def __init__(self, text: str):
        self.text = text

    def warn(self) -> str:
        """Return text in red color for warnings."""
        return f'\033[0;31m{self.text}\033[0m'

    def bold(self) -> str:
        """Return text in bold format."""
        return f'\033[1m{self.text}\033[0m'

    def highlight(self) -> str:
        """Return text in cyan color for highlights."""
        return f'\033[0;36m{self.text}\033[0m'


class CrossReferenceProcessor:
    """
    Processes AsciiDoc files to fix cross-references by mapping IDs to files
    and updating xref links to include proper file paths.
    """

    def __init__(self):
        # Match IDs at the top of the file - allow underscores in IDs
        self.id_in_regex = re.compile(r'''(?<=['"])[^"']+''')

        # Match include lines for recursively traversing a book from
        # master.adoc
        self.include_in_regex = re.compile(r'(?<=^include::)[^[]+')

        # Match xrefs. The negative look-ahead (?!.*\.adoc#) prevents modifying
        # already-modified xref links.
        self.link_in_regex = re.compile(
            r'(?<=xref:)(?!.*\.adoc#)([^\[]+)(\[.*?\])')

        # The id_map dictionary maps the ID as the key and the file as the
        # value
        self.id_map: Dict[str, str] = {}

        # Track processed files to prevent infinite recursion
        self.bread_crumbs: List[str] = []

    def build_id_map(self, file: str, bread_crumbs: List[str] = None) -> None:
        """
        Recursively walk all files from master.adoc down and create ID map.

        Args:
            file: Path to the file to process
            bread_crumbs: List of already processed files to prevent infinite recursion
        """
        if bread_crumbs is None:
            bread_crumbs = []

        if file in bread_crumbs:
            return

        bread_crumbs.append(file)
        path = os.path.dirname(file)

        try:
            with open(file, 'r', encoding='utf-8') as f:
                logger.debug(f"Reading file {file}")
                lines = f.readlines()

                for line in lines:
                    match_id = self.id_in_regex.search(line.strip())
                    match_include = self.include_in_regex.search(line.strip())

                    # If there's an ID, add it to the dictionary
                    if match_id:
                        id_value = match_id.group()
                        self.id_map[id_value] = file
                        logger.debug(f"Found ID '{id_value}' in file {file}")

                    # Keep track of all file paths as well
                    elif match_include:
                        include_path = match_include.group()
                        combined_path = os.path.join(path, include_path)
                        file_path = os.path.normpath(combined_path)
                        self.build_id_map(file_path, bread_crumbs)

        except Exception as e:
            print(Highlighter(f"Error reading {file}: {e}").warn())
            logger.error(f"Error reading {file}: {e}")

    def update_link(self, regex_match) -> str:
        """
        Update a cross-reference link to include the proper file path.

        Args:
            regex_match: Regex match object containing the link components

        Returns:
            Updated link string with file path included
        """
        link_id = regex_match.group(1)  # Use the full ID for lookup
        file_path = self.id_map.get(link_id, '')

        if not file_path:
            print(
                Highlighter(
                    f"Warning: ID '{link_id}' not found in id_map.").warn())
            logger.warning(f"ID '{link_id}' not found in id_map")
            return regex_match.group(0)

        file_name = os.path.basename(file_path)
        updated_link = f"{file_name}#{regex_match.group(1)}{regex_match.group(2)}"

        print(Highlighter(
            f"Fix found! moving {regex_match.group(0)} to {updated_link}"
        ).bold())
        logger.info(f"Updated xref: {regex_match.group(0)} -> {updated_link}")

        return updated_link

    def process_files(self) -> None:
        """
        Walk all files from the ID map and replace cross-reference links.
        """
        processed_files = set(self.id_map.values())

        for file in processed_files:
            self.process_single_file(file)

    def process_single_file(self, file: str) -> None:
        """
        Process a single file to update cross-reference links.

        Args:
            file: Path to the file to process
        """
        try:
            contents = []
            with open(file, 'r', encoding='utf-8') as f:
                logger.debug(f"Checking file {file}")
                contents = f.readlines()

            # Process each line to update xref links
            updated_contents = []
            for line in contents:
                updated_line = self.link_in_regex.sub(self.update_link, line)
                updated_contents.append(updated_line)

            # Write back the updated content
            with open(file, 'w', encoding='utf-8') as f:
                f.writelines(updated_contents)

            logger.info(f"Processed file {file}")

        except Exception as e:
            print(Highlighter(f"Error processing {file}: {e}").warn())
            logger.error(f"Error processing {file}: {e}")
            sys.exit(1)


def find_master_files(root_dir: str) -> List[str]:
    """
    Find all master.adoc files in the directory tree.

    Args:
        root_dir: Root directory to search

    Returns:
        List of paths to master.adoc files found
    """
    master_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file == "master.adoc":
                full_path = os.path.join(root, file)
                master_files.append(full_path)
    return master_files


def process_master_file(filepath: str) -> None:
    """
    Process a single master.adoc file and fix cross-references.

    Args:
        filepath: Path to the master.adoc file to process
    """
    processor = CrossReferenceProcessor()

    # Build the ID map from the master file
    processor.build_id_map(filepath)

    if not processor.id_map:
        print(
            Highlighter(
                f"No IDs found in {filepath} or its includes").warn())
        logger.warning(f"No IDs found in {filepath} or its includes")
        return

    # Process files to update cross-references
    processor.process_files()

    print(Highlighter("Cross-reference processing complete!").bold())
    logger.info("Cross-reference processing complete")


def main(args):
    """Main function for the CrossReference plugin."""
    # Setup logging based on verbosity
    if hasattr(args, 'verbose') and args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger.info("Starting cross-reference processing")

    if hasattr(args, 'master_file') and args.master_file:
        # Process specific master file
        if not os.path.exists(args.master_file):
            print(
                Highlighter(
                    f"Error: Master file {args.master_file} not found").warn())
            sys.exit(1)

        process_master_file(args.master_file)

    elif hasattr(args, 'recursive') and args.recursive:
        # Find and process all master.adoc files recursively
        directory = getattr(args, 'directory', '.')
        master_files = find_master_files(directory)

        if not master_files:
            print(
                Highlighter(
                    f"No master.adoc files found in {directory}").warn())
            logger.warning(f"No master.adoc files found in {directory}")
            return

        print(f"Found {len(master_files)} master.adoc file(s) to process")
        logger.info(f"Found {len(master_files)} master.adoc file(s) to process")

        for master_file in master_files:
            print(f"\nProcessing {master_file}")
            process_master_file(master_file)

    else:
        # Look for master.adoc in current directory
        directory = getattr(args, 'directory', '.')
        master_file = os.path.join(directory, 'master.adoc')

        if os.path.exists(master_file):
            process_master_file(master_file)
        else:
            print(
                Highlighter(
                    f"No master.adoc found in {directory}. Use --recursive to search subdirectories or specify --master-file.").warn())
            logger.warning(f"No master.adoc found in {directory}")


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser(
        "CrossReference",
        help=__description__,
        description=__description__
    )

    # Add common arguments from the toolkit
    common_arg_parser(parser)

    # Add plugin-specific arguments
    parser.add_argument(
        "--master-file",
        type=str,
        help="Complete path to your master.adoc file"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output"
    )

    parser.set_defaults(func=main)
