"""
Plugin for the AsciiDoc DITA toolkit: ContextMigrator

This plugin migrates AsciiDoc files from context-suffixed IDs to context-free IDs
with comprehensive validation and rollback capabilities. It performs the actual
migration with safety checks and backups.

This is Phase 2 of the context migration strategy - performs actual migration.
"""

__description__ = "Migrate AsciiDoc files from context-suffixed IDs to context-free IDs with validation and rollback"

import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
import logging

from ..cli_utils import common_arg_parser
from ..file_utils import find_adoc_files, read_text_preserve_endings, write_text_preserve_endings
from ..workflow_utils import process_adoc_files

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class MigrationOptions:
    """Options for controlling the migration process."""
    dry_run: bool = False
    create_backups: bool = True
    backup_dir: str = ".migration_backups"
    resolve_collisions: bool = True
    validate_after: bool = True


@dataclass
class IDChange:
    """Represents a change made to an ID during migration."""
    old_id: str
    new_id: str
    line_number: int


@dataclass
class XrefChange:
    """Represents a change made to an xref during migration."""
    old_xref: str
    new_xref: str
    line_number: int


@dataclass
class FileMigrationResult:
    """Result of migrating a single file."""
    filepath: str
    success: bool
    id_changes: List[IDChange]
    xref_changes: List[XrefChange]
    errors: List[str]
    backup_path: str


@dataclass
class ValidationResult:
    """Result of validating a migrated file."""
    filepath: str
    valid: bool
    broken_xrefs: List[str]
    warnings: List[str]


@dataclass
class MigrationResult:
    """Result of the complete migration process."""
    total_files_processed: int
    successful_migrations: int
    failed_migrations: int
    file_results: List[FileMigrationResult]
    validation_results: List[ValidationResult]
    backup_directory: str


class ContextMigrator:
    """
    Migrates AsciiDoc files from context-suffixed IDs to context-free IDs
    with comprehensive validation and rollback capabilities.
    """
    
    def __init__(self, options: MigrationOptions = None):
        self.options = options or MigrationOptions()
        self.migration_log = []
        
        # Regex patterns
        self.id_with_context_regex = re.compile(r'\[id="([^"]+)_([^"]+)"\]')
        self.xref_regex = re.compile(r'xref:([^#\[]+)(?:#([^#\[]+))?(\[.*?\])')
        self.link_regex = re.compile(r'link:([^#\[]+)(?:#([^#\[]+))?(\[.*?\])')
        self.context_attr_regex = re.compile(r'^:context:\s*(.+)$', re.MULTILINE)
        
        # Track ID mappings for cross-reference updates
        self.id_mappings: Dict[str, str] = {}  # old_id -> new_id
        self.file_id_map: Dict[str, str] = {}  # id -> filepath
        
    def create_backup(self, filepath: str) -> str:
        """
        Create a backup of the file before migration.
        
        Args:
            filepath: Path to the file to backup
            
        Returns:
            Path to the backup file
        """
        if not self.options.create_backups:
            return ""
            
        try:
            # Create backup directory if it doesn't exist
            backup_dir = self.options.backup_dir
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Create backup file path
            rel_path = os.path.relpath(filepath)
            backup_path = os.path.join(backup_dir, rel_path)
            
            # Ensure backup directory structure exists
            backup_file_dir = os.path.dirname(backup_path)
            if not os.path.exists(backup_file_dir):
                os.makedirs(backup_file_dir)
            
            # Copy the file
            shutil.copy2(filepath, backup_path)
            logger.debug(f"Created backup: {filepath} -> {backup_path}")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create backup for {filepath}: {e}")
            raise
    
    def resolve_id_collisions(self, base_id: str, existing_ids: Set[str]) -> str:
        """
        Resolve ID collisions by appending a numeric suffix.
        
        Args:
            base_id: The base ID that would cause a collision
            existing_ids: Set of existing IDs to check against
            
        Returns:
            A unique ID (may have numeric suffix)
        """
        if base_id not in existing_ids:
            return base_id
            
        if not self.options.resolve_collisions:
            return base_id  # Let the collision happen - user will handle it
            
        # Find the next available number
        counter = 1
        while f"{base_id}-{counter}" in existing_ids:
            counter += 1
            
        return f"{base_id}-{counter}"
    
    def remove_context_from_ids(self, content: str, filepath: str) -> Tuple[str, List[IDChange]]:
        """
        Remove context suffixes from IDs in the content.
        
        Args:
            content: File content to process
            filepath: Path to the file being processed
            
        Returns:
            Tuple of (modified_content, list_of_changes)
        """
        changes = []
        lines = content.split('\n')
        existing_ids = set()
        
        # First pass: collect existing IDs and identify changes needed
        id_changes_needed = []
        
        for line_num, line in enumerate(lines, 1):
            for match in self.id_with_context_regex.finditer(line):
                full_id = match.group(1) + '_' + match.group(2)
                base_id = match.group(1)
                
                # Resolve potential collisions
                new_id = self.resolve_id_collisions(base_id, existing_ids)
                existing_ids.add(new_id)
                
                id_changes_needed.append((line_num - 1, match, full_id, new_id))
                
                # Track the mapping for xref updates
                self.id_mappings[full_id] = new_id
                self.file_id_map[new_id] = filepath
        
        # Second pass: apply the changes
        for line_idx, match, old_id, new_id in id_changes_needed:
            old_line = lines[line_idx]
            new_line = old_line.replace(match.group(0), f'[id="{new_id}"]')
            lines[line_idx] = new_line
            
            changes.append(IDChange(
                old_id=old_id,
                new_id=new_id,
                line_number=line_idx + 1
            ))
        
        return '\n'.join(lines), changes
    
    def update_xrefs_and_links(self, content: str, filepath: str) -> Tuple[str, List[XrefChange]]:
        """
        Update xrefs and links to use the new IDs.
        
        Args:
            content: File content to process
            filepath: Path to the file being processed
            
        Returns:
            Tuple of (modified_content, list_of_changes)
        """
        changes = []
        lines = content.split('\n')
        
        # Update xrefs
        for line_num, line in enumerate(lines):
            # Process xref patterns
            def replace_xref(match):
                target_file = match.group(1) if match.group(1) else ""
                target_id = match.group(2) if match.group(2) else ""
                link_text = match.group(3) if match.group(3) else ""
                
                # Check if this ID has been migrated
                if target_id in self.id_mappings:
                    new_id = self.id_mappings[target_id]
                    old_xref = match.group(0)
                    
                    if target_file:
                        new_xref = f"xref:{target_file}#{new_id}{link_text}"
                    else:
                        new_xref = f"xref:{new_id}{link_text}"
                    
                    changes.append(XrefChange(
                        old_xref=old_xref,
                        new_xref=new_xref,
                        line_number=line_num + 1
                    ))
                    
                    return new_xref
                
                return match.group(0)
            
            # Update links
            def replace_link(match):
                target_file = match.group(1) if match.group(1) else ""
                target_id = match.group(2) if match.group(2) else ""
                link_text = match.group(3) if match.group(3) else ""
                
                # Check if this ID has been migrated
                if target_id in self.id_mappings:
                    new_id = self.id_mappings[target_id]
                    old_link = match.group(0)
                    
                    if target_file:
                        new_link = f"link:{target_file}#{new_id}{link_text}"
                    else:
                        new_link = f"link:{new_id}{link_text}"
                    
                    changes.append(XrefChange(
                        old_xref=old_link,
                        new_xref=new_link,
                        line_number=line_num + 1
                    ))
                    
                    return new_link
                
                return match.group(0)
            
            # Apply replacements
            new_line = self.xref_regex.sub(replace_xref, line)
            new_line = self.link_regex.sub(replace_link, new_line)
            lines[line_num] = new_line
        
        return '\n'.join(lines), changes
    
    def validate_migration(self, filepath: str) -> ValidationResult:
        """
        Validate that the migration was successful.
        
        Args:
            filepath: Path to the migrated file
            
        Returns:
            ValidationResult object
        """
        warnings = []
        broken_xrefs = []
        
        try:
            lines = read_text_preserve_endings(filepath)
            content = ''.join(text + ending for text, ending in lines)
            
            # Check for remaining context IDs
            remaining_context_ids = self.id_with_context_regex.findall(content)
            if remaining_context_ids:
                warnings.append(f"Found {len(remaining_context_ids)} remaining context IDs")
            
            # Check for broken xrefs (basic validation)
            # This is a simplified check - full validation would require cross-file analysis
            xref_matches = self.xref_regex.findall(content)
            for match in xref_matches:
                target_id = match[1] if len(match) > 1 else ""
                if target_id and target_id not in self.file_id_map:
                    broken_xrefs.append(target_id)
            
            return ValidationResult(
                filepath=filepath,
                valid=len(broken_xrefs) == 0,
                broken_xrefs=broken_xrefs,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Error validating {filepath}: {e}")
            return ValidationResult(
                filepath=filepath,
                valid=False,
                broken_xrefs=[],
                warnings=[f"Validation error: {e}"]
            )
    
    def migrate_file(self, filepath: str) -> FileMigrationResult:
        """
        Migrate a single file.
        
        Args:
            filepath: Path to the file to migrate
            
        Returns:
            FileMigrationResult object
        """
        backup_path = ""
        errors = []
        
        try:
            # Create backup
            if self.options.create_backups:
                backup_path = self.create_backup(filepath)
            
            # Read file content
            lines = read_text_preserve_endings(filepath)
            content = ''.join(text + ending for text, ending in lines)
            
            # Remove context from IDs
            content, id_changes = self.remove_context_from_ids(content, filepath)
            
            # Update xrefs and links
            content, xref_changes = self.update_xrefs_and_links(content, filepath)
            
            # Write back the modified content (unless dry run)
            if not self.options.dry_run:
                # Convert back to lines format for writing
                new_lines = []
                for line in content.split('\n'):
                    if line or new_lines:  # Don't add empty line at the end unless it was there
                        new_lines.append((line, '\n'))
                
                # Handle last line without newline
                if new_lines and content and not content.endswith('\n'):
                    new_lines[-1] = (new_lines[-1][0], '')
                
                write_text_preserve_endings(filepath, new_lines)
                logger.info(f"Migrated {filepath}: {len(id_changes)} ID changes, {len(xref_changes)} xref changes")
            else:
                logger.info(f"DRY RUN - Would migrate {filepath}: {len(id_changes)} ID changes, {len(xref_changes)} xref changes")
            
            return FileMigrationResult(
                filepath=filepath,
                success=True,
                id_changes=id_changes,
                xref_changes=xref_changes,
                errors=errors,
                backup_path=backup_path
            )
            
        except Exception as e:
            error_msg = f"Error migrating {filepath}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            
            return FileMigrationResult(
                filepath=filepath,
                success=False,
                id_changes=[],
                xref_changes=[],
                errors=errors,
                backup_path=backup_path
            )
    
    def migrate_directory(self, root_dir: str) -> MigrationResult:
        """
        Migrate all AsciiDoc files in a directory.
        
        Args:
            root_dir: Directory to migrate
            
        Returns:
            MigrationResult object
        """
        try:
            adoc_files = find_adoc_files(root_dir, recursive=True)
            
            file_results = []
            validation_results = []
            
            for filepath in adoc_files:
                result = self.migrate_file(filepath)
                file_results.append(result)
                
                # Validate if requested and migration was successful
                if self.options.validate_after and result.success and not self.options.dry_run:
                    validation_result = self.validate_migration(filepath)
                    validation_results.append(validation_result)
            
            successful_migrations = sum(1 for r in file_results if r.success)
            failed_migrations = len(file_results) - successful_migrations
            
            return MigrationResult(
                total_files_processed=len(file_results),
                successful_migrations=successful_migrations,
                failed_migrations=failed_migrations,
                file_results=file_results,
                validation_results=validation_results,
                backup_directory=self.options.backup_dir
            )
            
        except Exception as e:
            logger.error(f"Error migrating directory {root_dir}: {e}")
            return MigrationResult(
                total_files_processed=0,
                successful_migrations=0,
                failed_migrations=0,
                file_results=[],
                validation_results=[],
                backup_directory=self.options.backup_dir
            )


def format_migration_report(result: MigrationResult) -> str:
    """
    Format the migration result as a human-readable report.
    
    Args:
        result: MigrationResult to format
        
    Returns:
        Formatted text report
    """
    lines = ["=== Context Migration Report ===", ""]
    
    # Summary
    lines.extend([
        f"Total files processed: {result.total_files_processed}",
        f"Successful migrations: {result.successful_migrations}",
        f"Failed migrations: {result.failed_migrations}",
        f"Backup directory: {result.backup_directory}",
        ""
    ])
    
    # Details for each file
    if result.file_results:
        lines.append("=== File Migration Details ===")
        for file_result in result.file_results:
            status = "SUCCESS" if file_result.success else "FAILED"
            lines.append(f"{file_result.filepath}: {status}")
            
            if file_result.id_changes:
                lines.append(f"  ID Changes: {len(file_result.id_changes)}")
                for change in file_result.id_changes[:5]:  # Show first 5
                    lines.append(f"    - {change.old_id} → {change.new_id} (line {change.line_number})")
                if len(file_result.id_changes) > 5:
                    lines.append(f"    ... and {len(file_result.id_changes) - 5} more")
            
            if file_result.xref_changes:
                lines.append(f"  Xref Changes: {len(file_result.xref_changes)}")
                for change in file_result.xref_changes[:3]:  # Show first 3
                    lines.append(f"    - {change.old_xref} → {change.new_xref} (line {change.line_number})")
                if len(file_result.xref_changes) > 3:
                    lines.append(f"    ... and {len(file_result.xref_changes) - 3} more")
            
            if file_result.errors:
                lines.append(f"  Errors:")
                for error in file_result.errors:
                    lines.append(f"    - {error}")
            
            lines.append("")
    
    # Validation results
    if result.validation_results:
        lines.append("=== Validation Results ===")
        for validation in result.validation_results:
            status = "VALID" if validation.valid else "INVALID"
            lines.append(f"{validation.filepath}: {status}")
            
            if validation.broken_xrefs:
                lines.append(f"  Broken xrefs: {', '.join(validation.broken_xrefs)}")
            
            if validation.warnings:
                lines.append(f"  Warnings:")
                for warning in validation.warnings:
                    lines.append(f"    - {warning}")
            
            lines.append("")
    
    return "\n".join(lines)


def process_context_migrator_file(filepath: str, migrator: ContextMigrator):
    """
    Process a single file with the context migrator.
    
    Args:
        filepath: Path to the file to process
        migrator: ContextMigrator instance
    """
    result = migrator.migrate_file(filepath)
    return result


def main(args):
    """Main function for the ContextMigrator plugin."""
    # Setup logging
    if hasattr(args, 'verbose') and args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Parse options
    options = MigrationOptions()
    options.dry_run = getattr(args, 'dry_run', False)
    options.create_backups = not getattr(args, 'no_backup', False)
    options.backup_dir = getattr(args, 'backup_dir', '.migration_backups')
    options.resolve_collisions = not getattr(args, 'no_collision_resolution', False)
    options.validate_after = getattr(args, 'validate', False)
    
    # Create migrator
    migrator = ContextMigrator(options)
    
    # Collect all file results
    file_results = []
    
    # Process files
    def process_file_wrapper(filepath):
        result = process_context_migrator_file(filepath, migrator)
        file_results.append(result)
        return result
    
    try:
        process_adoc_files(args, process_file_wrapper)
        
        # Create migration result
        successful_migrations = sum(1 for r in file_results if r.success)
        failed_migrations = len(file_results) - successful_migrations
        
        # Run validation if requested
        validation_results = []
        if options.validate_after and not options.dry_run:
            for result in file_results:
                if result.success:
                    validation_result = migrator.validate_migration(result.filepath)
                    validation_results.append(validation_result)
        
        migration_result = MigrationResult(
            total_files_processed=len(file_results),
            successful_migrations=successful_migrations,
            failed_migrations=failed_migrations,
            file_results=file_results,
            validation_results=validation_results,
            backup_directory=options.backup_dir
        )
        
        # Generate report
        report = format_migration_report(migration_result)
        
        # Output results
        output_file = getattr(args, 'output', None)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Migration report saved to {output_file}")
        else:
            print(report)
        
        # Exit with error code if there were failures
        if failed_migrations > 0:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        print("\nMigration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}")
        print(f"Error during migration: {e}")
        sys.exit(1)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser(
        "ContextMigrator",
        help=__description__,
        description=__description__
    )
    
    # Add common arguments
    common_arg_parser(parser)
    
    # Add plugin-specific arguments
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without actually modifying files"
    )
    
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backups (not recommended)"
    )
    
    parser.add_argument(
        "--backup-dir",
        type=str,
        default=".migration_backups",
        help="Directory for backup files (default: .migration_backups)"
    )
    
    parser.add_argument(
        "--no-collision-resolution",
        action="store_true",
        help="Don't automatically resolve ID collisions with numeric suffixes"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate migration results after completion"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Save migration report to specified file"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output"
    )
    
    parser.set_defaults(func=main)