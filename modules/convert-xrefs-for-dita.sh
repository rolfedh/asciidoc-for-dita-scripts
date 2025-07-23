#!/bin/bash

# DITA Cross-Reference Conversion Workflow
# Converts xref:id[text] to xref:filename.adoc#id[text] format
# Modified to process each book individually to maintain clean ID mappings

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DITA_CONVERTER="$SCRIPT_DIR/dita-xref-converter.py"
RUBY_ID_MAPPER="$SCRIPT_DIR/id-filename-map.rb"
BOOK_PROCESSOR="$SCRIPT_DIR/book-by-book-processor.py"

# Default values
TARGET_PATH="."
DRY_RUN=false
CREATE_BACKUPS=true
SHOW_MAPPING=false
OUTPUT_FILE=""
PROCESS_ALL_BOOKS=true

usage() {
    cat << EOF
Usage: $0 [OPTIONS] [TARGET]

Convert cross-references from xref:id[text] to xref:filename.adoc#id[text] format for DITA preparation.
Processes each book individually to maintain clean ID mappings within book boundaries.

ARGUMENTS:
    TARGET              Path to directory to process (default: current directory)
                       If a master.adoc file is provided, only that book will be processed

OPTIONS:
    -h, --help          Show this help message
    --dry-run           Show what would be changed without making modifications  
    --no-backup         Do not create backup files
    --show-mapping      Show the complete ID to filename mapping for each book
    -o, --output FILE   Output report to file instead of stdout

BOOK-BY-BOOK APPROACH:
   - Finds all master.adoc files in the target directory
   - For each master.adoc file:
     * Builds ID → filename mapping by following includes
     * Processes only files included in that book
     * Converts xref:id[text] to xref:filename.adoc#id[text]
     * Maintains clean mappings within book boundaries
   - Moves to next book with fresh mapping

EXAMPLES:
    # Process all books in current directory
    $0

    # Process all books in specific directory
    $0 doc-Installing_Guide/

    # Process single book
    $0 doc-Installing_Guide/master.adoc

    # Dry-run to see what would be changed
    $0 --dry-run --show-mapping

    # Process with custom output and no backups
    $0 --dry-run --no-backup --output report.txt

WORKFLOW:
    1. Find all master.adoc files in target directory
    2. For each book:
       a. Build ID → filename mapping by following includes
       b. Find all files included in this book
       c. Convert xrefs in those files using the book's mapping
       d. Create backups and report results
    3. Move to next book with clean mapping

EOF
}

log_step() {
    echo -e "${BLUE}==>${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        log_error "python3 is required but not installed"
        exit 1
    fi
    
    if [[ ! -f "$BOOK_PROCESSOR" ]]; then
        log_error "Book processor not found: $BOOK_PROCESSOR"
        log_step "Creating book processor script..."
        create_book_processor
    fi
}

create_book_processor() {
    cat > "$BOOK_PROCESSOR" << 'EOF'
#!/usr/bin/env python3

import os
import re
import argparse
import sys
from collections import defaultdict

class Highlighter:
    def __init__(self, text):
        self.text = text
    def warn(self):
        return '\033[0;31m' + self.text + '\033[0m'
    def bold(self):
        return '\033[1m' + self.text + '\033[0m'
    def highlight(self):
        return '\033[0;36m' + self.text + '\033[0m'
    def success(self):
        return '\033[0;32m' + self.text + '\033[0m'

def find_all_master_files(directory):
    """Find all master.adoc files in the directory tree"""
    master_files = []
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file == "master.adoc":
                filepath = os.path.join(root, file)
                master_files.append(filepath)
    return master_files

def get_book_files_and_mapping(master_file):
    """
    Build ID mapping and get all files included in this book
    Based on the pattern from the user's example script
    """
    context = None
    context_regex = re.compile(r':context:\s+(.*)')
    id_regex = re.compile(r'\[\[(.*?)\]\]|\[id="?(.*?)"?\]')
    include_regex = re.compile(r'^include::([^[]+)')
    
    file_id_dictionary = {}
    included_files = set()
    
    def get_files(file_path, level=0):
        nonlocal context
        
        if not os.path.exists(file_path):
            return
            
        included_files.add(file_path)
        file_dir = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    # Look for context setting
                    context_match = context_regex.search(line.strip())
                    if context_match:
                        context = context_match.group(1).strip()
                    
                    # Look for IDs
                    for id_match in id_regex.finditer(line):
                        id_string = id_match.group(1) or id_match.group(2)
                        if not id_string:
                            continue
                        
                        # Store both the base ID and context version
                        file_id_dictionary[id_string] = filename
                        if context:
                            complete_id = f'{id_string}_{context}'
                            file_id_dictionary[complete_id] = filename
                    
                    # Look for includes
                    include_match = include_regex.search(line.strip())
                    if include_match:
                        path = include_match.group(1).strip()
                        # Combine file_dir with relative 'path'
                        full_path = os.path.join(file_dir, path)
                        full_path = os.path.normpath(full_path)
                        get_files(full_path, level + 1)
        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    get_files(master_file)
    return file_id_dictionary, included_files

def convert_xrefs_in_file(filepath, id_map, dry_run=False, create_backups=True):
    """Convert xrefs in a single file using the provided ID mapping"""
    filename = os.path.basename(filepath)
    xref_regex = re.compile(r'(xref:)(?!.*\.adoc#)([^\[]+)(\[.*?\])')
    
    changes_made = 0
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        def replacer(match):
            nonlocal changes_made
            xref_id = match.group(2).strip()
            link_text = match.group(3)
            
            if xref_id in id_map:
                target_filename = id_map[xref_id]
                new_link = f"xref:{target_filename}#{xref_id}{link_text}"
                changes_made += 1
                print(f"  {Highlighter('Fixing link:').highlight()} {xref_id} -> {target_filename}")
                return new_link
            else:
                issue = f"Cannot find ID '{xref_id}' in {filename}"
                issues.append(issue)
                print(f"  {Highlighter('Broken link:').warn()} {issue}")
                return match.group(0)
        
        new_content = xref_regex.sub(replacer, content)
        
        # If changes were made and not dry run, write the new content
        if changes_made > 0 and not dry_run:
            # Create backup if requested
            if create_backups:
                backup_path = f"{filepath}.backup"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Write the new content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  {Highlighter('Updated:').success()} {filename} - {changes_made} changes")
        elif changes_made > 0:
            print(f"  {Highlighter('Would update:').highlight()} {filename} - {changes_made} changes")
    
    except Exception as e:
        error_msg = f"Error processing {filepath}: {e}"
        issues.append(error_msg)
        print(f"  {Highlighter('Error:').warn()} {error_msg}")
    
    return changes_made, issues

def build_global_id_mapping(master_files):
    """Build a global ID mapping from all books"""
    global_id_map = {}
    
    for master_file in master_files:
        print(f"  Processing {master_file}...")
        book_id_map, _ = get_book_files_and_mapping(master_file)
        
        # Merge book mapping into global mapping
        for id_val, filename in book_id_map.items():
            if id_val in global_id_map and global_id_map[id_val] != filename:
                # Handle ID conflicts - prefer the first occurrence
                print(f"    Warning: ID '{id_val}' found in multiple files: {global_id_map[id_val]} and {filename}")
            else:
                global_id_map[id_val] = filename
    
    print(f"  Built global mapping with {len(global_id_map)} IDs")
    return global_id_map

def process_book_with_global_mapping(master_file, global_id_map, dry_run=False, create_backups=True, show_mapping=False):
    """Process a single book using the global ID mapping"""
    print(f"\n{Highlighter('Processing book:').bold()} {master_file}")
    
    # Get included files for this book (but use global ID mapping)
    _, included_files = get_book_files_and_mapping(master_file)
    
    print(f"\n{Highlighter('Files in this book:').highlight()} {len(included_files)}")
    for file_path in sorted(included_files):
        print(f"  {file_path}")
    
    # Convert xrefs in all included files using global mapping
    total_changes = 0
    total_issues = []
    
    print(f"\n{Highlighter('Converting cross-references:').highlight()}")
    for file_path in included_files:
        if file_path.endswith('.adoc'):
            changes, issues = convert_xrefs_in_file(file_path, global_id_map, dry_run, create_backups)
            total_changes += changes
            total_issues.extend(issues)
    
    return total_changes, total_issues

def process_book(master_file, dry_run=False, create_backups=True, show_mapping=False):
    """Process a single book (legacy function for backward compatibility)"""
    print(f"\n{Highlighter('Processing book:').bold()} {master_file}")
    
    # Build ID mapping and get included files
    id_map, included_files = get_book_files_and_mapping(master_file)
    
    if show_mapping:
        print(f"\n{Highlighter('ID Mapping:').highlight()}")
        for id_val, filename in sorted(id_map.items()):
            print(f"  {id_val} -> {filename}")
    
    print(f"\n{Highlighter('Files in this book:').highlight()} {len(included_files)}")
    for file_path in sorted(included_files):
        print(f"  {file_path}")
    
    # Convert xrefs in all included files
    total_changes = 0
    total_issues = []
    
    print(f"\n{Highlighter('Converting cross-references:').highlight()}")
    for file_path in included_files:
        if file_path.endswith('.adoc'):
            changes, issues = convert_xrefs_in_file(file_path, id_map, dry_run, create_backups)
            total_changes += changes
            total_issues.extend(issues)
    
    return total_changes, total_issues

def main():
    parser = argparse.ArgumentParser(description='Process books individually for DITA xref conversion')
    parser.add_argument('target', nargs='?', default='.', help='Target directory or master.adoc file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making modifications')
    parser.add_argument('--no-backup', action='store_true', help='Do not create backup files')
    parser.add_argument('--show-mapping', action='store_true', help='Show the complete ID to filename mapping')
    parser.add_argument('--output', help='Output report to file instead of stdout')
    
    args = parser.parse_args()
    
    # Determine if we're processing a single book or all books
    if args.target.endswith('.adoc'):
        master_files = [args.target]
    else:
        master_files = find_all_master_files(args.target)
    
    if not master_files:
        print(f"{Highlighter('No master.adoc files found').warn()}")
        return 1
    
    print(f"{Highlighter('Found books to process:').bold()} {len(master_files)}")
    for master_file in master_files:
        print(f"  {master_file}")
    
    # Build global ID mapping from all books
    print(f"\n{Highlighter('Building global ID mapping from all books...').bold()}")
    global_id_map = build_global_id_mapping(master_files)
    
    if args.show_mapping:
        print(f"\n{Highlighter('Global ID Mapping:').highlight()} ({len(global_id_map)} total IDs)")
        for id_val, filename in sorted(global_id_map.items()):
            print(f"  {id_val} -> {filename}")
    
    # Process each book using the global mapping
    total_changes = 0
    total_issues = []
    
    for master_file in master_files:
        changes, issues = process_book_with_global_mapping(
            master_file, 
            global_id_map,
            dry_run=args.dry_run, 
            create_backups=not args.no_backup,
            show_mapping=False  # Already shown above
        )
        total_changes += changes
        total_issues.extend(issues)
    
    # Summary
    print(f"\n{Highlighter('Summary:').bold()}")
    print(f"  Books processed: {len(master_files)}")
    print(f"  Total changes: {total_changes}")
    print(f"  Total issues: {len(total_issues)}")
    
    if total_issues:
        print(f"\n{Highlighter('Issues found:').warn()}")
        for issue in total_issues:
            print(f"  {issue}")
    
    # Write report if requested
    if args.output:
        with open(args.output, 'w') as f:
            f.write(f"DITA Cross-Reference Conversion Report\n")
            f.write(f"=====================================\n\n")
            f.write(f"Books processed: {len(master_files)}\n")
            f.write(f"Total changes: {total_changes}\n")
            f.write(f"Total issues: {len(total_issues)}\n\n")
            if total_issues:
                f.write("Issues:\n")
                for issue in total_issues:
                    f.write(f"  {issue}\n")
    
    return 0 if not total_issues else 1

if __name__ == '__main__':
    sys.exit(main())
EOF
    
    chmod +x "$BOOK_PROCESSOR"
    log_success "Book processor script created"
}

validate_target() {
    if [[ -z "$TARGET_PATH" ]]; then
        TARGET_PATH="."
    fi
    
    if [[ ! -d "$TARGET_PATH" ]] && [[ ! -f "$TARGET_PATH" ]]; then
        log_error "Target must be a directory or master.adoc file: $TARGET_PATH"
        exit 1
    fi
}

run_book_by_book_conversion() {
    log_step "Converting cross-references using book-by-book approach..."
    
    local args=("$TARGET_PATH")
    
    if [[ "$DRY_RUN" == true ]]; then
        args+=(--dry-run)
    fi
    
    if [[ "$CREATE_BACKUPS" == false ]]; then
        args+=(--no-backup)
    fi
    
    if [[ "$SHOW_MAPPING" == true ]]; then
        args+=(--show-mapping)
    fi
    
    if [[ -n "$OUTPUT_FILE" ]]; then
        args+=(--output "$OUTPUT_FILE")
    fi
    
    if python3 "$BOOK_PROCESSOR" "${args[@]}"; then
        log_success "Book-by-book cross-reference conversion completed successfully"
        return 0
    else
        log_error "Book-by-book cross-reference conversion found issues"
        return 1
    fi
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --no-backup)
            CREATE_BACKUPS=false
            shift
            ;;
        --show-mapping)
            SHOW_MAPPING=true
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -*)
            echo "Unknown option: $1" >&2
            usage
            exit 1
            ;;
        *)
            TARGET_PATH="$1"
            shift
            ;;
    esac
done

# Main execution
main() {
    echo -e "${BLUE}DITA Cross-Reference Conversion (Book-by-Book)${NC}"
    echo ""
    
    check_dependencies
    validate_target
    
    if [[ "$DRY_RUN" == true ]]; then
        log_step "Running in DRY-RUN mode - no files will be modified"
    fi
    
    # Run book-by-book conversion
    if run_book_by_book_conversion; then
        echo ""
        log_success "DITA cross-reference conversion completed!"
        
        if [[ "$DRY_RUN" == false ]]; then
            echo ""
            echo "Next steps:"
            echo "1. Review any backup files created (*.backup)"
            echo "2. Check for any missing references in the report"
            echo "3. Test that your documentation builds correctly"
            echo "4. Commit changes for DITA preparation"
        fi
        exit 0
    else
        echo ""
        log_error "Conversion encountered issues - see report above"
        exit 1
    fi
}

main "$@" 