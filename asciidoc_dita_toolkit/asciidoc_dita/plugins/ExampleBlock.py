"""
Plugin for the AsciiDoc DITA toolkit: ExampleBlock

This plugin detects and fixes AsciiDoc example blocks that are placed in invalid locations
according to DITA 1.3 specification (within sections, other blocks, or lists).
"""

__description__ = "Move example blocks to the main body of topics for DITA 1.3 compliance."

import logging
import re
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from ..cli_utils import common_arg_parser
from ..plugin_manager import is_plugin_enabled
from ..workflow_utils import process_adoc_files

# Try to import ADTModule for the new pattern
try:
    # Add the path to find the ADTModule
    package_root = Path(__file__).parent.parent.parent.parent
    if str(package_root / "src") not in sys.path:
        sys.path.insert(0, str(package_root / "src"))
    
    from adt_core.module_sequencer import ADTModule
    ADT_MODULE_AVAILABLE = True
except ImportError:
    ADT_MODULE_AVAILABLE = False
    # Create a dummy ADTModule for backward compatibility
    class ADTModule:
        pass

# Setup logging
logger = logging.getLogger(__name__)


class ExampleBlockDetector:
    """Detects example blocks in AsciiDoc content and determines their validity."""
    
    def __init__(self):
        # More precise regex patterns
        self.example_block_delimited_start = re.compile(r'^====\s*$', re.MULTILINE)
        self.example_block_style = re.compile(r'^\[example\]', re.MULTILINE)
        self.section_header = re.compile(r'^==+\s+', re.MULTILINE)
        self.list_item = re.compile(r'^[*\-+]|\d+\.|[a-zA-Z]\.|[ivxIVX]+\)', re.MULTILINE)
        self.admonition_styles = re.compile(r'^\[(NOTE|TIP|IMPORTANT|WARNING|CAUTION|source|literal)\]', re.MULTILINE)
    
    def find_example_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Find all example blocks in the content."""
        blocks = []
        lines = content.split('\n')
        
        # Find delimited example blocks (====) - but not in code blocks or comments
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line == '====':
                # Check if this is inside a code block or comment
                if self._is_in_code_block_or_comment(lines, i):
                    i += 1
                    continue
                
                # Check if this is part of an admonition
                if self._is_admonition_block(lines, i):
                    i += 1
                    continue
                
                start_line = i
                # Find the closing delimiter
                j = i + 1
                while j < len(lines) and lines[j].strip() != '====':
                    j += 1
                if j < len(lines):  # Found closing delimiter
                    end_line = j
                    start_pos = sum(len(lines[k]) + 1 for k in range(start_line))
                    end_pos = sum(len(lines[k]) + 1 for k in range(end_line + 1))
                    
                    # Check if this has a title (previous line starts with .)
                    title_start = start_line
                    if start_line > 0 and lines[start_line - 1].strip().startswith('.'):
                        title_start = start_line - 1
                        start_pos = sum(len(lines[k]) + 1 for k in range(title_start))
                    
                    blocks.append({
                        'type': 'delimited',
                        'start': start_pos,
                        'end': end_pos,
                        'start_line': title_start,
                        'end_line': end_line,
                        'content': '\n'.join(lines[title_start:end_line + 1])
                    })
                    i = j + 1
                else:
                    i += 1
            else:
                i += 1
        
        # Find style example blocks ([example]) - but not in comments
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line == '[example]':
                # Check if this is inside a comment
                if self._is_in_comment(lines, i):
                    i += 1
                    continue
                
                start_line = i
                # Find the content (next non-empty line(s))
                j = i + 1
                while j < len(lines) and lines[j].strip() == '':
                    j += 1
                
                if j < len(lines):
                    # Find the end of the content
                    end_line = j
                    while end_line + 1 < len(lines):
                        next_line = lines[end_line + 1].strip()
                        if next_line == '' or next_line.startswith('[') or next_line.startswith('='):
                            break
                        end_line += 1
                    
                    start_pos = sum(len(lines[k]) + 1 for k in range(start_line))
                    end_pos = sum(len(lines[k]) + 1 for k in range(end_line + 1))
                    
                    blocks.append({
                        'type': 'style',
                        'start': start_pos,
                        'end': end_pos,
                        'start_line': start_line,
                        'end_line': end_line,
                        'content': '\n'.join(lines[start_line:end_line + 1])
                    })
                    i = end_line + 1
                else:
                    i += 1
            else:
                i += 1
        
        return blocks
    
    def _is_in_code_block_or_comment(self, lines: List[str], line_index: int) -> bool:
        """Check if the line is inside a code block or comment."""
        # Check for code block delimiters
        code_delimiters = ['----', '....']
        
        for delimiter in code_delimiters:
            count = 0
            for i in range(line_index):
                if lines[i].strip() == delimiter:
                    count += 1
            if count % 2 == 1:  # Odd number means we're inside
                return True
        
        # Check for comment blocks
        comment_count = 0
        for i in range(line_index):
            if lines[i].strip() == '////':
                comment_count += 1
        if comment_count % 2 == 1:
            return True
        
        # Check for source/literal blocks that might contain example syntax
        for i in range(line_index - 1, max(0, line_index - 5), -1):
            line = lines[i].strip()
            if re.match(r'^\[(source|literal)', line):
                return True
            if line == '' or line.startswith('.'):
                continue
            else:
                break
        
        return False
    
    def _is_in_comment(self, lines: List[str], line_index: int) -> bool:
        """Check if the line is inside a comment."""
        # Check for single-line comment
        if line_index > 0 and lines[line_index - 1].strip().startswith('//'):
            return True
        
        # Check for comment blocks
        comment_count = 0
        for i in range(line_index):
            if lines[i].strip() == '////':
                comment_count += 1
        if comment_count % 2 == 1:
            return True
        
        return False
    
    def _is_admonition_block(self, lines: List[str], line_index: int) -> bool:
        """Check if the block is part of an admonition."""
        # Look backwards for admonition markers
        for i in range(line_index - 1, max(0, line_index - 10), -1):
            line = lines[i].strip()
            
            # Direct admonition marker before our block
            if re.match(r'^\[(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', line):
                return True
            
            # Check for admonition with empty lines in between
            if line == '' and i > 0:
                prev_line = lines[i-1].strip()
                if re.match(r'^\[(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', prev_line):
                    return True
            
            # Check for admonition with continuation marker
            if line == '+' and i > 0:
                for j in range(i - 1, max(0, i - 5), -1):
                    check_line = lines[j].strip()
                    if re.match(r'^\[(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', check_line):
                        return True
            
            # If we hit something substantial, stop looking
            if line != '' and not line.startswith('.') and line != '+':
                break
        
        return False
    
    def find_main_body_end(self, content: str) -> int:
        """Find the end of the main body (before first section header)."""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.match(r'^==+\s+', line):
                return sum(len(lines[k]) + 1 for k in range(i))
        return len(content)
    
    def is_in_main_body(self, block: Dict[str, Any], content: str) -> bool:
        """Check if a block is in the main body of the document."""
        lines = content.split('\n')
        
        # Check if there's a section header before this block
        for i in range(block['start_line']):
            if re.match(r'^==+\s+', lines[i]):
                return False
        
        return True
    
    def is_in_list(self, block: Dict[str, Any], content: str) -> bool:
        """Check if a block is inside a list item."""
        lines = content.split('\n')
        
        # Look backwards from the block to find list context
        for i in range(block['start_line'] - 1, -1, -1):
            line = lines[i].strip()
            
            # If we hit a section header or empty line, stop
            if re.match(r'^==+\s+', line) or (line == '' and i < block['start_line'] - 5):
                break
            
            # Check for list item markers
            if re.match(r'^[*\-+]|\d+\.|[a-zA-Z]\.|[ivxIVX]+\)', line):
                # Check if there's a continuation marker (+) leading to our block
                for j in range(i + 1, block['start_line']):
                    if lines[j].strip() == '+':
                        return True
        
        return False
    
    def is_in_block(self, block: Dict[str, Any], content: str) -> bool:
        """Check if a block is inside another block (sidebar, quote, etc.)."""
        lines = content.split('\n')
        
        # Common block delimiters
        block_delimiters = ['****', '--']
        
        for delimiter in block_delimiters:
            open_count = 0
            for i in range(block['start_line']):
                if lines[i].strip() == delimiter:
                    open_count += 1
            
            # If odd number of delimiters before our block, we're inside
            if open_count % 2 == 1:
                return True
        
        return False


class ExampleBlockProcessor:
    """Processes example blocks and applies fixes."""
    
    def __init__(self, detector: ExampleBlockDetector, interactive: bool = True):
        self.detector = detector
        self.interactive = interactive
        self.comment_template = """//
// ADT ExampleBlock: Move this example block to the main body of the topic 
// (before the first section header) for DITA 1.3 compliance.
//
"""
    
    def process_content(self, content: str) -> Tuple[str, List[str]]:
        """Process content and return modified content and list of issues."""
        issues = []
        lines = content.split('\n')
        
        blocks = self.detector.find_example_blocks(content)
        
        # Find invalid blocks
        invalid_blocks = []
        for block in blocks:
            if not self.detector.is_in_main_body(block, content):
                issue_type = self._determine_issue_type(block, content)
                issues.append(f"Example block at position {block['start']} is in {issue_type}")
                invalid_blocks.append(block)
        
        if not invalid_blocks:
            return content, issues
        
        # Apply fixes
        if self.interactive:
            # Apply automatic fixes - move blocks to main body
            modified_lines = lines[:]
            moved_blocks = []
            
            # Sort blocks by line number (reverse order to maintain positions)
            invalid_blocks.sort(key=lambda x: x['start_line'], reverse=True)
            
            for block in invalid_blocks:
                # Extract block content
                block_content = modified_lines[block['start_line']:block['end_line'] + 1]
                
                # Remove from current position
                del modified_lines[block['start_line']:block['end_line'] + 1]
                
                # Store for insertion at main body
                moved_blocks.append(block_content)
            
            # Find where to insert (before first section header)
            insert_pos = len(modified_lines)
            for i, line in enumerate(modified_lines):
                if re.match(r'^==+\s+', line):
                    insert_pos = i
                    break
            
            # Insert all moved blocks at the end of main body
            for block_content in reversed(moved_blocks):
                modified_lines[insert_pos:insert_pos] = block_content + ['']
                insert_pos += len(block_content) + 1
            
            return '\n'.join(modified_lines), issues
        else:
            # Insert comments only
            modified_lines = lines[:]
            
            # Sort blocks by line number (reverse order to maintain positions)
            invalid_blocks.sort(key=lambda x: x['start_line'], reverse=True)
            
            for block in invalid_blocks:
                comment_lines = self.comment_template.strip().split('\n')
                modified_lines[block['start_line']:block['start_line']] = comment_lines
            
            return '\n'.join(modified_lines), issues
    
    def _determine_issue_type(self, block: Dict[str, Any], content: str) -> str:
        """Determine what type of invalid location the block is in."""
        if self.detector.is_in_list(block, content):
            return "list"
        elif self.detector.is_in_block(block, content):
            return "block"
        else:
            return "section"


def process_example_block_file(filepath: str, processor: ExampleBlockProcessor) -> bool:
    """Process a single AsciiDoc file for example block issues."""
    try:
        file_path = Path(filepath)
        
        if not file_path.exists():
            logger.warning(f"File not found: {filepath}")
            return False
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Process the content
        modified_content, issues = processor.process_content(content)
        
        # Write back if changed
        if modified_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            if issues:
                print(f"Fixed example block issues in {filepath}:")
                for issue in issues:
                    print(f"  - {issue}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing {filepath}: {e}")
        return False


def create_processor(batch_mode: bool = False, quiet_mode: bool = False) -> ExampleBlockProcessor:
    """Create an ExampleBlockProcessor with appropriate settings."""
    detector = ExampleBlockDetector()
    return ExampleBlockProcessor(detector, interactive=not batch_mode)


def main():
    """Main entry point for the plugin."""
    parser = common_arg_parser("ExampleBlock", __description__)
    args = parser.parse_args()
    
    if not is_plugin_enabled("ExampleBlock"):
        print("ExampleBlock plugin is disabled")
        return
    
    processor = create_processor(batch_mode=False, quiet_mode=args.quiet if hasattr(args, 'quiet') else False)
    
    def process_file_wrapper(filepath):
        return process_example_block_file(filepath, processor)
    
    process_adoc_files(args, process_file_wrapper)


if __name__ == "__main__":
    main()
