#!/usr/bin/env python3

import os
import re
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class XrefMatch:
    file_path: str
    line_number: int
    original_text: str
    id_reference: str
    link_text: str
    start_pos: int
    end_pos: int

@dataclass
class ConversionResult:
    file_path: str
    xrefs_updated: List[str]
    xrefs_not_found: List[str]
    backup_created: bool
    errors: List[str]

class DITAXrefConverter:
    def __init__(self, create_backups: bool = True, dry_run: bool = False):
        self.create_backups = create_backups
        self.dry_run = dry_run
        self.id_to_filename: Dict[str, str] = {}
        self.filename_to_ids: Dict[str, List[str]] = defaultdict(list)
        
    def extract_ids_from_file(self, filepath: str) -> List[str]:
        """Extract all IDs from an AsciiDoc file."""
        ids = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Pattern to match both new format [id="some-id"] and old format [[some-id]]
            new_format_pattern = r'\[id=["\']([^"\']+)["\']\]'
            old_format_pattern = r'\[\[([^\]]+)\]\]'
            
            # Extract IDs from both formats
            new_matches = re.findall(new_format_pattern, content)
            old_matches = re.findall(old_format_pattern, content)
            
            ids.extend(new_matches)
            ids.extend(old_matches)
            
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}")
            
        return ids
    
    def build_id_mapping(self, base_path: str) -> None:
        """Build a mapping of IDs to filenames by scanning all .adoc files."""
        print("Building ID to filename mapping...")
        
        files_scanned = 0
        total_ids_found = 0
        
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.adoc') and not file.startswith('.'):
                    filepath = os.path.join(root, file)
                    relative_path = os.path.relpath(filepath, base_path)
                    filename = os.path.basename(filepath)
                    
                    ids = self.extract_ids_from_file(filepath)
                    files_scanned += 1
                    total_ids_found += len(ids)
                    
                    for id_value in ids:
                        if id_value in self.id_to_filename:
                            print(f"Warning: Duplicate ID '{id_value}' found in:")
                            print(f"  - {self.id_to_filename[id_value]}")
                            print(f"  - {relative_path}")
                        
                        self.id_to_filename[id_value] = filename
                        self.filename_to_ids[filename].append(id_value)
        
        print(f"Scanned {files_scanned} files and found {total_ids_found} IDs")
        print(f"Built mapping for {len(self.id_to_filename)} unique IDs")
    
    def find_xrefs_in_content(self, content: str, filepath: str) -> List[XrefMatch]:
        """Find all xref statements in file content."""
        xrefs = []
        
        # Pattern to match xref:id[link text] but not xref:file.adoc#id[link text]
        # This ensures we don't convert already-converted xrefs
        xref_pattern = r'xref:([^#\s\[]+)(\[([^\]]*)\])'
        
        for match in re.finditer(xref_pattern, content):
            full_match = match.group(0)
            id_reference = match.group(1)
            link_text = match.group(3) if match.group(3) else ""
            
            # Skip if this looks like it's already converted (contains .adoc)
            if '.adoc' in id_reference:
                continue
                
            # Find line number for better reporting
            lines_before = content[:match.start()].count('\n')
            line_number = lines_before + 1
            
            xref_match = XrefMatch(
                file_path=filepath,
                line_number=line_number,
                original_text=full_match,
                id_reference=id_reference,
                link_text=link_text,
                start_pos=match.start(),
                end_pos=match.end()
            )
            xrefs.append(xref_match)
        
        return xrefs
    
    def convert_xref(self, xref_match: XrefMatch) -> Optional[str]:
        """Convert a single xref to DITA format."""
        id_ref = xref_match.id_reference
        
        # Look up the filename for this ID
        if id_ref in self.id_to_filename:
            filename = self.id_to_filename[id_ref]
            link_text = xref_match.link_text
            
            # Create the new DITA-style xref
            new_xref = f"xref:{filename}#{id_ref}[{link_text}]"
            return new_xref
        
        return None
    
    def convert_file(self, filepath: str) -> ConversionResult:
        """Convert all xrefs in a single file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            return ConversionResult(
                file_path=filepath,
                xrefs_updated=[],
                xrefs_not_found=[],
                backup_created=False,
                errors=[f"Could not read file: {str(e)}"]
            )
        
        # Find all xrefs in the file
        xrefs = self.find_xrefs_in_content(original_content, filepath)
        
        if not xrefs:
            return ConversionResult(
                file_path=filepath,
                xrefs_updated=[],
                xrefs_not_found=[],
                backup_created=False,
                errors=[]
            )
        
        content = original_content
        xrefs_updated = []
        xrefs_not_found = []
        
        # Sort xrefs by position (descending) so we can replace from end to start
        # This prevents position shifts from affecting later replacements
        xrefs.sort(key=lambda x: x.start_pos, reverse=True)
        
        for xref_match in xrefs:
            new_xref = self.convert_xref(xref_match)
            
            if new_xref:
                # Replace the xref in the content
                content = (content[:xref_match.start_pos] + 
                          new_xref + 
                          content[xref_match.end_pos:])
                
                xrefs_updated.append(f"Line {xref_match.line_number}: {xref_match.original_text} → {new_xref}")
            else:
                xrefs_not_found.append(f"Line {xref_match.line_number}: {xref_match.original_text} (ID '{xref_match.id_reference}' not found)")
        
        # Create backup and write the file if changes were made
        backup_created = False
        errors = []
        
        if xrefs_updated and not self.dry_run:
            if self.create_backups:
                backup_path = f"{filepath}.backup"
                try:
                    shutil.copy2(filepath, backup_path)
                    backup_created = True
                except Exception as e:
                    errors.append(f"Could not create backup: {str(e)}")
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                errors.append(f"Could not write file: {str(e)}")
        
        return ConversionResult(
            file_path=filepath,
            xrefs_updated=xrefs_updated,
            xrefs_not_found=xrefs_not_found,
            backup_created=backup_created,
            errors=errors
        )
    
    def convert_directory(self, directory: str) -> List[ConversionResult]:
        """Convert all xrefs in all .adoc files in a directory."""
        results = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.adoc') and not file.startswith('.'):
                    filepath = os.path.join(root, file)
                    result = self.convert_file(filepath)
                    results.append(result)
        
        return results
    
    def generate_report(self, results: List[ConversionResult]) -> str:
        """Generate a comprehensive report of the conversion."""
        total_files = len(results)
        files_with_updates = len([r for r in results if r.xrefs_updated])
        files_with_missing_refs = len([r for r in results if r.xrefs_not_found])
        files_with_errors = len([r for r in results if r.errors])
        total_updates = sum(len(r.xrefs_updated) for r in results)
        total_missing = sum(len(r.xrefs_not_found) for r in results)
        
        report = []
        report.append(f"\n{'='*70}")
        report.append(f"DITA CROSS-REFERENCE CONVERSION REPORT")
        report.append(f"{'='*70}")
        report.append(f"Files processed: {total_files}")
        report.append(f"Files with updates: {files_with_updates}")
        report.append(f"Files with missing references: {files_with_missing_refs}")
        report.append(f"Files with errors: {files_with_errors}")
        report.append(f"Total xrefs updated: {total_updates}")
        report.append(f"Total missing references: {total_missing}")
        report.append(f"Total IDs in mapping: {len(self.id_to_filename)}")
        
        # Show detailed results for files with changes
        for result in results:
            if result.xrefs_updated or result.xrefs_not_found or result.errors:
                report.append(f"\n{'-'*50}")
                report.append(f"File: {result.file_path}")
                
                if result.xrefs_updated:
                    report.append(f"\n✅ XREFS UPDATED ({len(result.xrefs_updated)}):")
                    for update in result.xrefs_updated:
                        report.append(f"   • {update}")
                    
                    if result.backup_created:
                        report.append(f"   📁 Backup created: {result.file_path}.backup")
                
                if result.xrefs_not_found:
                    report.append(f"\n❌ MISSING REFERENCES ({len(result.xrefs_not_found)}):")
                    for missing in result.xrefs_not_found:
                        report.append(f"   • {missing}")
                
                if result.errors:
                    report.append(f"\n⚠️  ERRORS ({len(result.errors)}):")
                    for error in result.errors:
                        report.append(f"   • {error}")
        
        return '\n'.join(report)
    
    def show_id_mapping_summary(self) -> str:
        """Show a summary of the ID mapping for verification."""
        report = []
        report.append(f"\n{'='*50}")
        report.append(f"ID MAPPING SUMMARY")
        report.append(f"{'='*50}")
        
        # Group by filename
        for filename, ids in sorted(self.filename_to_ids.items()):
            report.append(f"\n{filename}:")
            for id_value in sorted(ids):
                report.append(f"   • {id_value}")
        
        return '\n'.join(report)

def main():
    parser = argparse.ArgumentParser(
        description='Convert cross-references for DITA preparation'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to directory to process (default: current directory)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making modifications'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )
    parser.add_argument(
        '--show-mapping',
        action='store_true',
        help='Show the complete ID to filename mapping'
    )
    parser.add_argument(
        '--output',
        help='Output report to file instead of stdout'
    )
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.path):
        print(f"Error: {args.path} is not a directory")
        return 1
    
    print(f"Starting DITA cross-reference conversion for: {args.path}")
    if args.dry_run:
        print("Running in DRY-RUN mode - no files will be modified")
    
    converter = DITAXrefConverter(
        create_backups=not args.no_backup,
        dry_run=args.dry_run
    )
    
    # Phase 1: Build ID mapping
    converter.build_id_mapping(args.path)
    
    if args.show_mapping:
        print(converter.show_id_mapping_summary())
    
    # Phase 2: Convert xrefs
    print("\nConverting cross-references...")
    results = converter.convert_directory(args.path)
    
    # Phase 3: Generate report
    report = converter.generate_report(results)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
            if args.show_mapping:
                f.write(converter.show_id_mapping_summary())
        print(f"Report written to {args.output}")
    else:
        print(report)
    
    # Return error code if there were missing references or errors
    has_missing = any(r.xrefs_not_found for r in results)
    has_errors = any(r.errors for r in results)
    
    if has_missing or has_errors:
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main()) 