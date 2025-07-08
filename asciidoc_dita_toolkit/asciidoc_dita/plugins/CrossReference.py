THIS SHOULD BE A LINTER ERROR"""
Plugin for the AsciiDoc DITA toolkit: CrossReference

This plugin fixes cross-references in AsciiDoc files by updating xref links to include proper file paths.
It scans for section IDs and updates xref links that point to those IDs but lack the proper file reference.

Enhanced for Phase 3 of context migration strategy with validation, reporting, and migration-aware processing.

Original author: Roger Heslop
Enhanced for AsciiDoc DITA Toolkit framework
"""

__description__ = "Fix cross-references in AsciiDoc files by updating xref links to include proper file paths"

import json
import os
import re
import sys
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path

from ..cli_utils import common_arg_parser
from ..file_utils import find_adoc_files, read_text_preserve_endings, write_text_preserve_endings
from ..workflow_utils import process_adoc_files

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class BrokenXref:
    """Represents a broken cross-reference."""
    filepath: str
    line_number: int
    xref_text: str
    target_id: str
    target_file: str
    reason: str


@dataclass
class XrefFix:
    """Represents a fixed cross-reference."""
    filepath: str
    line_number: int
    old_xref: str
    new_xref: str


@dataclass
class ValidationReport:
    """Comprehensive validation report for cross-references."""
    total_files_processed: int
    total_xrefs_found: int
    broken_xrefs: List[BrokenXref]
    fixed_xrefs: List[XrefFix]
    warnings: List[str]
    validation_successful: bool


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

    def success(self) -> str:
        """Return text in green color for success."""
        return f'\033[0;32m{self.text}\033[0m'


class CrossReferenceProcessor:
    """
    Processes AsciiDoc files to fix cross-references by mapping IDs to files
    and updating xref links to include proper file paths.
    Enhanced with validation, migration awareness, and comprehensive reporting.
    """

    def __init__(self, validation_only: bool = False, migration_mode: bool = False):
        # Match IDs - captures both old and new style IDs
        self.id_regex = re.compile(r'\[id="([^"]+)"\]')
        
        # Match include lines for recursively traversing a book from master.adoc
        self.include_regex = re.compile(r'(?<=^include::)[^[]+')
        
        # Match xrefs. The negative look-ahead (?!.*\.adoc#) prevents modifying already-modified xref links.
        self.xref_regex = re.compile(r'(?<=xref:)(?!.*\.adoc#)([^\[]+)(\[.*?\])')
        
        # Match context-style IDs for migration awareness
        self.context_id_regex = re.compile(r'\[id="([^"]+)_([^"]+)"\]')
        
        # The id_map dictionary maps the ID as the key and the file as the value
        self.id_map: Dict[str, str] = {}
        
        # Track processed files to prevent infinite recursion
        self.processed_files: Set[str] = set()
        
        # Enhanced tracking for migration and validation
        self.validation_only = validation_only
        self.migration_mode = migration_mode
        self.broken_xrefs: List[BrokenXref] = []
        self.fixed_xrefs: List[XrefFix] = []
        self.warnings: List[str] = []
        
        # Context-aware ID mappings (old_id -> new_id)
        self.context_id_mappings: Dict[str, str] = {}
        
        # Track all found xrefs for validation
        self.all_xrefs: List[Tuple[str, int, str, str, str]] = []  # (filepath, line_num, full_match, target_id, target_file)

    def build_id_map(self, file: str, processed_files: Set[str] = None) -> None:
        """
        Recursively walk all files from master.adoc down and create ID map.
        Enhanced to handle both old and new style IDs for migration awareness.

        Args:
            file: Path to the file to process
            processed_files: Set of already processed files to prevent infinite recursion
        """
        if processed_files is None:
            processed_files = set()

        if file in processed_files:
            return

        processed_files.add(file)
        self.processed_files.add(file)
        path = os.path.dirname(file)

        try:
            with open(file, 'r', encoding='utf-8') as f:
                logger.debug(f"Reading file {file}")
                lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    # Look for ID definitions
                    id_match = self.id_regex.search(line.strip())
                    include_match = self.include_regex.search(line.strip())

                    if id_match:
                        id_value = id_match.group(1)
                        self.id_map[id_value] = file
                        logger.debug(f"Found ID '{id_value}' in file {file}")

                        # Check if this is a context-style ID for migration awareness
                        if self.migration_mode:
                            context_match = self.context_id_regex.search(line.strip())
                            if context_match:
                                full_id = context_match.group(1) + '_' + context_match.group(2)
                                base_id = context_match.group(1)
                                
                                # In migration mode, prefer the base ID if both exist
                                if base_id in self.id_map and self.id_map[base_id] == file:
                                    self.context_id_mappings[full_id] = base_id
                                    logger.debug(f"Context ID mapping: {full_id} -> {base_id}")

                    elif include_match:
                        include_path = include_match.group()
                        combined_path = os.path.join(path, include_path)
                        file_path = os.path.normpath(combined_path)
                        
                        if os.path.exists(file_path):
                            self.build_id_map(file_path, processed_files)
                        else:
                            warning = f"Include file not found: {file_path} (referenced in {file})"
                            self.warnings.append(warning)
                            logger.warning(warning)

        except Exception as e:
            error_msg = f"Error reading {file}: {e}"
            print(Highlighter(error_msg).warn())
            logger.error(error_msg)

    def prefer_context_free_ids(self, target_id: str, target_file: str) -> str:
        """
        In migration mode, prefer context-free IDs over context-suffixed ones.
        
        Args:
            target_id: The target ID to check
            target_file: The target file (if specified)
            
        Returns:
            Preferred ID to use
        """
        if not self.migration_mode:
            return target_id
            
        # Check if there's a context-free version of this ID
        if target_id in self.context_id_mappings:
            preferred_id = self.context_id_mappings[target_id]
            logger.debug(f"Preferring context-free ID: {target_id} -> {preferred_id}")
            return preferred_id
            
        return target_id

    def validate_xref(self, filepath: str, line_num: int, xref_text: str, target_id: str, target_file: str) -> bool:
        """
        Validate a single cross-reference.
        
        Args:
            filepath: File containing the xref
            line_num: Line number of the xref
            xref_text: Full xref text
            target_id: Target ID
            target_file: Target file (if specified)
            
        Returns:
            True if valid, False if broken
        """
        if not target_id:
            return True  # Empty target ID is not necessarily broken
            
        # Check if target ID exists in our map
        if target_id not in self.id_map:
            reason = f"Target ID '{target_id}' not found in documentation"
            broken_xref = BrokenXref(
                filepath=filepath,
                line_number=line_num,
                xref_text=xref_text,
                target_id=target_id,
                target_file=target_file,
                reason=reason
            )
            self.broken_xrefs.append(broken_xref)
            return False
            
        # If target file is specified, validate it matches
        if target_file:
            expected_file = os.path.basename(self.id_map[target_id])
            if target_file != expected_file:
                reason = f"Target file '{target_file}' doesn't match expected '{expected_file}' for ID '{target_id}'"
                broken_xref = BrokenXref(
                    filepath=filepath,
                    line_number=line_num,
                    xref_text=xref_text,
                    target_id=target_id,
                    target_file=target_file,
                    reason=reason
                )
                self.broken_xrefs.append(broken_xref)
                return False
                
        return True

    def update_xref(self, filepath: str, line_num: int, regex_match) -> str:
        """
        Update a cross-reference link to include the proper file path.
        Enhanced with validation and migration awareness.

        Args:
            filepath: File containing the xref
            line_num: Line number of the xref
            regex_match: Regex match object containing the link components

        Returns:
            Updated link string with file path included
        """
        target_id = regex_match.group(1)
        link_text = regex_match.group(2)
        original_xref = regex_match.group(0)

        # Apply migration-aware ID preference
        preferred_id = self.prefer_context_free_ids(target_id, "")
        
        # Check if ID exists in our map
        if preferred_id not in self.id_map:
            warning = f"Warning: ID '{preferred_id}' not found in id_map (in {filepath}:{line_num})"
            print(Highlighter(warning).warn())
            logger.warning(warning)
            self.warnings.append(warning)
            
            # Record as broken xref
            broken_xref = BrokenXref(
                filepath=filepath,
                line_number=line_num,
                xref_text=original_xref,
                target_id=preferred_id,
                target_file="",
                reason=f"ID '{preferred_id}' not found in documentation"
            )
            self.broken_xrefs.append(broken_xref)
            
            return original_xref

        target_file_path = self.id_map[preferred_id]
        file_name = os.path.basename(target_file_path)
        updated_xref = f"{file_name}#{preferred_id}{link_text}"

        # Record the fix
        fix = XrefFix(
            filepath=filepath,
            line_number=line_num,
            old_xref=original_xref,
            new_xref=updated_xref
        )
        self.fixed_xrefs.append(fix)

        if self.migration_mode and preferred_id != target_id:
            print(Highlighter(
                f"Migration-aware fix: {original_xref} -> {updated_xref} (context-free ID preferred)"
            ).highlight())
        else:
            print(Highlighter(
                f"Fix found! {original_xref} -> {updated_xref}"
            ).success())
        
        logger.info(f"Updated xref: {original_xref} -> {updated_xref}")

        return updated_xref

    def process_file(self, filepath: str) -> None:
        """
        Process a single file to update cross-reference links or validate them.
        Enhanced with validation-only mode and comprehensive tracking.

        Args:
            filepath: Path to the file to process
        """
        try:
            lines = read_text_preserve_endings(filepath)
            logger.debug(f"Processing file {filepath}")

            # Track all xrefs for validation
            for line_num, (text, ending) in enumerate(lines, 1):
                for match in self.xref_regex.finditer(text):
                    target_id = match.group(1)
                    full_match = match.group(0)
                    self.all_xrefs.append((filepath, line_num, full_match, target_id, ""))

            if self.validation_only:
                # Only validate, don't modify
                for line_num, (text, ending) in enumerate(lines, 1):
                    for match in self.xref_regex.finditer(text):
                        target_id = match.group(1)
                        full_match = match.group(0)
                        self.validate_xref(filepath, line_num, full_match, target_id, "")
                return

            # Process each line to update xref links
            updated_lines = []
            for line_num, (text, ending) in enumerate(lines, 1):
                def replace_xref(match):
                    return self.update_xref(filepath, line_num, match)
                
                updated_text = self.xref_regex.sub(replace_xref, text)
                updated_lines.append((updated_text, ending))

            # Write back the updated content
            write_text_preserve_endings(filepath, updated_lines)
            logger.info(f"Processed file {filepath}")

        except Exception as e:
            error_msg = f"Error processing {filepath}: {e}"
            print(Highlighter(error_msg).warn())
            logger.error(error_msg)
            self.warnings.append(error_msg)

    def process_files(self, start_file: str = None) -> None:
        """
        Process all files from the ID map or starting from a specific file.
        
        Args:
            start_file: Optional starting file (e.g., master.adoc)
        """
        if start_file:
            # Build ID map starting from the specified file
            self.build_id_map(start_file)
        
        # Process all files we've discovered
        processed_files = set(self.id_map.values())
        
        for filepath in processed_files:
            self.process_file(filepath)

    def generate_validation_report(self) -> ValidationReport:
        """
        Generate a comprehensive validation report.
        
        Returns:
            ValidationReport object
        """
        return ValidationReport(
            total_files_processed=len(self.processed_files),
            total_xrefs_found=len(self.all_xrefs),
            broken_xrefs=self.broken_xrefs,
            fixed_xrefs=self.fixed_xrefs,
            warnings=self.warnings,
            validation_successful=len(self.broken_xrefs) == 0
        )


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


def process_master_file(filepath: str, validation_only: bool = False, migration_mode: bool = False) -> ValidationReport:
    """
    Process a single master.adoc file and fix cross-references.

    Args:
        filepath: Path to the master.adoc file to process
        validation_only: If True, only validate without fixing
        migration_mode: If True, use migration-aware processing

    Returns:
        ValidationReport object
    """
    processor = CrossReferenceProcessor(validation_only, migration_mode)

    # Build the ID map from the master file
    processor.build_id_map(filepath)

    if not processor.id_map:
        warning = f"No IDs found in {filepath} or its includes"
        print(Highlighter(warning).warn())
        logger.warning(warning)
        processor.warnings.append(warning)
        return processor.generate_validation_report()

    # Process files to update/validate cross-references
    processor.process_files()

    if validation_only:
        print(Highlighter("Cross-reference validation complete!").bold())
    else:
        print(Highlighter("Cross-reference processing complete!").bold())
    
    logger.info("Cross-reference processing complete")
    return processor.generate_validation_report()


def format_validation_report(report: ValidationReport, detailed: bool = False) -> str:
    """
    Format validation report as human-readable text.
    
    Args:
        report: ValidationReport to format
        detailed: Whether to include detailed information
        
    Returns:
        Formatted text report
    """
    lines = ["=== Cross-Reference Validation Report ===", ""]
    
    # Summary
    lines.extend([
        f"Files processed: {report.total_files_processed}",
        f"Total xrefs found: {report.total_xrefs_found}",
        f"Broken xrefs: {len(report.broken_xrefs)}",
        f"Fixed xrefs: {len(report.fixed_xrefs)}",
        f"Warnings: {len(report.warnings)}",
        f"Validation successful: {'Yes' if report.validation_successful else 'No'}",
        ""
    ])
    
    # Broken xrefs
    if report.broken_xrefs:
        lines.append("=== Broken Cross-References ===")
        for broken in report.broken_xrefs:
            lines.append(f"{broken.filepath}:{broken.line_number}")
            lines.append(f"  Xref: {broken.xref_text}")
            lines.append(f"  Target ID: {broken.target_id}")
            lines.append(f"  Reason: {broken.reason}")
            lines.append("")
    
    # Fixed xrefs (if detailed)
    if detailed and report.fixed_xrefs:
        lines.append("=== Fixed Cross-References ===")
        for fix in report.fixed_xrefs:
            lines.append(f"{fix.filepath}:{fix.line_number}")
            lines.append(f"  {fix.old_xref} -> {fix.new_xref}")
            lines.append("")
    
    # Warnings
    if report.warnings:
        lines.append("=== Warnings ===")
        for warning in report.warnings:
            lines.append(f"- {warning}")
        lines.append("")
    
    return "\n".join(lines)


def main(args):
    """Main function for the CrossReference plugin."""
    # Setup logging based on verbosity
    if hasattr(args, 'verbose') and args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger.info("Starting cross-reference processing")
    
    # Parse arguments
    validation_only = getattr(args, 'check_only', False)
    migration_mode = getattr(args, 'migration_mode', False)
    generate_report = getattr(args, 'validate', False) or validation_only
    report_file = getattr(args, 'report', None)
    detailed_report = getattr(args, 'detailed', False)

    try:
        if hasattr(args, 'master_file') and args.master_file:
            # Process specific master file
            if not os.path.exists(args.master_file):
                error_msg = f"Master file {args.master_file} not found"
                print(Highlighter(error_msg).warn())
                logger.error(error_msg)
                sys.exit(1)

            report = process_master_file(args.master_file, validation_only, migration_mode)

        elif hasattr(args, 'recursive') and args.recursive:
            # Find and process all master.adoc files recursively
            directory = getattr(args, 'directory', '.')
            master_files = find_master_files(directory)

            if not master_files:
                warning = f"No master.adoc files found in {directory}"
                print(Highlighter(warning).warn())
                logger.warning(warning)
                return

            print(f"Found {len(master_files)} master.adoc file(s) to process")
            logger.info(f"Found {len(master_files)} master.adoc file(s) to process")

            # Process all master files and combine reports
            all_reports = []
            for master_file in master_files:
                print(f"\nProcessing {master_file}")
                report = process_master_file(master_file, validation_only, migration_mode)
                all_reports.append(report)

            # Create combined report
            report = ValidationReport(
                total_files_processed=sum(r.total_files_processed for r in all_reports),
                total_xrefs_found=sum(r.total_xrefs_found for r in all_reports),
                broken_xrefs=[xref for r in all_reports for xref in r.broken_xrefs],
                fixed_xrefs=[fix for r in all_reports for fix in r.fixed_xrefs],
                warnings=[warning for r in all_reports for warning in r.warnings],
                validation_successful=all(r.validation_successful for r in all_reports)
            )

        else:
            # Look for master.adoc in current directory
            directory = getattr(args, 'directory', '.')
            master_file = os.path.join(directory, 'master.adoc')

            if os.path.exists(master_file):
                report = process_master_file(master_file, validation_only, migration_mode)
            else:
                warning = f"No master.adoc found in {directory}. Use --recursive to search subdirectories or specify --master-file."
                print(Highlighter(warning).warn())
                logger.warning(warning)
                return

        # Generate and output report if requested
        if generate_report:
            if report_file and report_file.endswith('.json'):
                # JSON report
                report_dict = asdict(report)
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report_dict, f, indent=2)
                print(f"Validation report saved to {report_file}")
            else:
                # Text report
                report_text = format_validation_report(report, detailed_report)
                if report_file:
                    with open(report_file, 'w', encoding='utf-8') as f:
                        f.write(report_text)
                    print(f"Validation report saved to {report_file}")
                else:
                    print(report_text)

        # Exit with error code if validation failed
        if validation_only and not report.validation_successful:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


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
        "--check-only",
        action="store_true",
        help="Only validate xrefs without fixing them"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Generate validation report after processing"
    )

    parser.add_argument(
        "--migration-mode",
        action="store_true",
        help="Use migration-aware processing (prefer context-free IDs)"
    )

    parser.add_argument(
        "--report",
        type=str,
        help="Save validation report to specified file (use .json extension for JSON format)"
    )

    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Include detailed information in reports"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output"
    )

    parser.set_defaults(func=main)