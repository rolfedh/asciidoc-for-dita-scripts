"""
Plugin for the AsciiDoc DITA toolkit: ExampleBlock

This plugin detects and fixes AsciiDoc example blocks that are placed in invalid locations
according to DITA 1.3 specification (within sections, other blocks, or lists).
"""

__description__ = "Detect and process example blocks"

import logging
import re
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

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
        f"This is required for ExampleBlock module to function properly."
    )


# Setup logging
logger = logging.getLogger(__name__)


class ExampleBlockDetector:
    """
    Detects example blocks in AsciiDoc content and determines their validity.

    This class uses regex patterns to identify and validate example blocks in AsciiDoc files.
    It supports two types of example blocks:
    1. Delimited example blocks, which are enclosed by `====` lines.
    2. Styled example blocks, which are marked with `[example]`.

    Regex patterns used:
    - `example_block_delimited_start`: Matches the start of a delimited example block (`====`).
    - `example_block_style`: Matches the `[example]` style block marker.
    - `section_header`: Matches section headers (e.g., `== Section`).
    - `list_item`: Matches list items (e.g., `*`, `-`, `1.`, `a.`, `i.`).
    - `admonition_styles`: Matches admonition blocks (e.g., `[NOTE]`, `[TIP]`).

    These patterns help identify the context and structure of example blocks to ensure they
    are placed in valid locations according to the DITA 1.3 specification.
    """

    def __init__(self):
        # More precise regex patterns
        self.example_block_delimited_start = re.compile(r'^====\s*$', re.MULTILINE)
        self.example_block_style = re.compile(r'^\[example\]', re.MULTILINE)
        self.section_header = re.compile(r'^==+\s+', re.MULTILINE)
        self.list_item = re.compile(
            r'^(?:[*\-+]|\d+\.|[a-zA-Z]\.|[ivxIVX]+\))', re.MULTILINE
        )
        self.admonition_styles = re.compile(
            r'^\[(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', re.MULTILINE
        )

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
                    # Skip to find the closing delimiter and jump past it
                    j = i + 1
                    while j < len(lines) and lines[j].strip() != '====':
                        j += 1
                    if j < len(lines):  # Found closing delimiter
                        i = j + 1  # Jump past the closing delimiter
                    else:
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

                    blocks.append(
                        {
                            'type': 'delimited',
                            'start': start_pos,
                            'end': end_pos,
                            'start_line': title_start,
                            'end_line': end_line,
                            'content': '\n'.join(lines[title_start : end_line + 1]),
                        }
                    )
                    i = j + 1  # Jump past the closing delimiter
                else:
                    i += 1
            else:
                i += 1

        # Find style example blocks ([example]) - but not in comments or code blocks
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line == '[example]':
                # Check if this is inside a comment or code block
                if self._is_in_code_block_or_comment(lines, i):
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
                        if (
                            next_line == ''
                            or next_line.startswith('[')
                            or next_line.startswith('=')
                        ):
                            break
                        end_line += 1

                    start_pos = sum(len(lines[k]) + 1 for k in range(start_line))
                    end_pos = sum(len(lines[k]) + 1 for k in range(end_line + 1))

                    blocks.append(
                        {
                            'type': 'style',
                            'start': start_pos,
                            'end': end_pos,
                            'start_line': start_line,
                            'end_line': end_line,
                            'content': '\n'.join(lines[start_line : end_line + 1]),
                        }
                    )
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
                prev_line = lines[i - 1].strip()
                if re.match(r'^\[(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', prev_line):
                    return True

            # Check for admonition with continuation marker
            if line == '+' and i > 0:
                for j in range(i - 1, max(0, i - 5), -1):
                    check_line = lines[j].strip()
                    if re.match(
                        r'^\[(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', check_line
                    ):
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
            if re.match(r'^==+\s+', line) or (
                line == '' and i < block['start_line'] - 5
            ):
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

    def __init__(
        self,
        detector: ExampleBlockDetector,
        interactive: bool = True,
        quiet_mode: bool = False,
    ):
        self.detector = detector
        self.interactive = interactive
        self.quiet_mode = quiet_mode
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
            # A block is invalid if it's NOT in the main body OR it's in a list OR it's in another block
            if (
                not self.detector.is_in_main_body(block, content)
                or self.detector.is_in_list(block, content)
                or self.detector.is_in_block(block, content)
            ):
                issue_type = self._determine_issue_type(block, content)
                issues.append(
                    f"Example block at position {block['start']} is in {issue_type}"
                )
                invalid_blocks.append(block)

        if not invalid_blocks:
            return content, issues

        # Process each invalid block
        modified_lines = lines[:]

        if self.interactive:
            # Process each block individually with user interaction
            for block in invalid_blocks:
                if self._should_exit():
                    break

                choice = self._prompt_user_for_block(block, content)
                if choice:
                    modified_lines = self._apply_user_choice(
                        modified_lines, block, choice, content
                    )
        else:
            # Non-interactive mode: add comments by default
            self._add_default_comments(modified_lines, invalid_blocks)

        return '\n'.join(modified_lines), issues

    def _should_exit(self) -> bool:
        """Check if user has requested to exit."""
        return getattr(self, '_exit_requested', False)

    def _prompt_user_for_block(
        self, block: Dict[str, Any], content: str
    ) -> Optional[str]:
        """Prompt user for action on a specific block."""
        print(f"\nExample block found at line {block['start_line'] + 1}:")
        print(f"Content: {block['content'][:50]}...")

        # Generate placement options
        placement_options = self._generate_placement_options(block, content)

        # Show top 3 options, with "See more" if there are more
        display_options = placement_options[:3]
        if len(placement_options) > 3:
            display_options.append(("4", "See more choices"))

        print("Options:")
        for i, (key, description) in enumerate(display_options, 1):
            print(f"  {i} - {description}")

        print("  L - Leave as-is and insert comment")
        print("  S - Skip this block")
        print("  Q - Quit plugin")
        print("Press: Number for placement, L/S/Q, or Enter for option 1")

        while True:
            try:
                choice = self._get_single_char_input()

                # Handle Enter (default to option 1)
                if choice in ['\r', '\n']:
                    return placement_options[0][0] if placement_options else 'L'

                # Handle Ctrl+C (quit)
                if choice == '\x03':
                    raise KeyboardInterrupt

                # Handle number choices
                if choice.isdigit():
                    choice_num = int(choice)
                    if choice_num == 4 and len(placement_options) > 3:
                        return self._show_full_options(
                            placement_options, block, content
                        )
                    elif 1 <= choice_num <= min(3, len(placement_options)):
                        return placement_options[choice_num - 1][0]

                # Handle letter choices
                choice_upper = choice.upper()
                if choice_upper == 'L':
                    return 'L'
                elif choice_upper == 'S':
                    return 'S'
                elif choice_upper == 'Q':
                    self._exit_requested = True
                    return 'Q'

                print("Invalid choice. Try again.")

            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                self._exit_requested = True
                return 'Q'

    def _show_full_options(
        self,
        placement_options: List[Tuple[str, str]],
        block: Dict[str, Any],
        content: str,
    ) -> Optional[str]:
        """Show all placement options."""
        print("\nAll placement options:")
        for i, (key, description) in enumerate(placement_options, 1):
            print(f"  {i} - {description}")

        print("  L - Leave as-is and insert comment")
        print("  S - Skip this block")
        print("  Q - Quit plugin")
        print("Press: Number for placement, L/S/Q")

        while True:
            try:
                choice = self._get_single_char_input()

                if choice == '\x03':
                    raise KeyboardInterrupt

                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(placement_options):
                        return placement_options[choice_num - 1][0]

                choice_upper = choice.upper()
                if choice_upper == 'L':
                    return 'L'
                elif choice_upper == 'S':
                    return 'S'
                elif choice_upper == 'Q':
                    self._exit_requested = True
                    return 'Q'

                print("Invalid choice. Try again.")

            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                self._exit_requested = True
                return 'Q'

    def _generate_placement_options(
        self, block: Dict[str, Any], content: str
    ) -> List[Tuple[str, str]]:
        """Generate placement options for a block."""
        options = []

        # Option 1: End of main body (before first section)
        options.append(("1", "Move to end of main body"))

        # Option 2: Beginning of main body (after title/header)
        options.append(("2", "Move to beginning of main body"))

        # Option 3: Near related content (if identifiable)
        if self._has_related_content(block, content):
            options.append(("3", "Move near related content"))

        return options

    def _has_related_content(self, block: Dict[str, Any], content: str) -> bool:
        """Check if block has related content that could guide placement."""
        # Simple heuristic: if block has a title, it might have related content
        return block.get('content', '').strip().startswith('.')

    def _apply_user_choice(
        self, lines: List[str], block: Dict[str, Any], choice: str, content: str
    ) -> List[str]:
        """Apply user's choice to the content."""
        if choice == 'S':
            # Skip - no changes
            return lines
        elif choice == 'L':
            # Leave as-is and add comment
            return self._add_comment_to_block(lines, block)
        elif choice == 'Q':
            # Quit - no changes
            return lines
        elif choice in ['1', '2', '3']:
            # Move block to specified location
            return self._move_block_to_location(lines, block, choice)
        else:
            # Default: add comment
            return self._add_comment_to_block(lines, block)

    def _move_block_to_location(
        self, lines: List[str], block: Dict[str, Any], location: str
    ) -> List[str]:
        """Move block to specified location."""
        # Extract block content
        block_content = lines[block['start_line'] : block['end_line'] + 1]

        # Remove from current position
        del lines[block['start_line'] : block['end_line'] + 1]

        # Find insertion point based on location
        if location == '1':
            # End of main body (before first section)
            insert_pos = self._find_end_of_main_body(lines)
        elif location == '2':
            # Beginning of main body (after title/header)
            insert_pos = self._find_beginning_of_main_body(lines)
        elif location == '3':
            # Near related content (for now, same as end of main body)
            insert_pos = self._find_end_of_main_body(lines)
        else:
            # Default: end of main body
            insert_pos = self._find_end_of_main_body(lines)

        # Insert block content
        lines[insert_pos:insert_pos] = block_content + ['']

        return lines

    def _find_end_of_main_body(self, lines: List[str]) -> int:
        """Find the end of the main body (before first section header)."""
        for i, line in enumerate(lines):
            if re.match(r'^==+\s+', line):
                return i
        return len(lines)

    def _find_beginning_of_main_body(self, lines: List[str]) -> int:
        """Find the beginning of the main body (after title/header)."""
        # Skip title, author, and attribute lines
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('=') and not line.startswith(':'):
                return i
        return 0

    def _add_comment_to_block(
        self, lines: List[str], block: Dict[str, Any]
    ) -> List[str]:
        """Add comment to a block."""
        comment_lines = self.comment_template.strip().split('\n')
        lines[block['start_line'] : block['start_line']] = comment_lines
        return lines

    def _add_default_comments(
        self, lines: List[str], blocks: List[Dict[str, Any]]
    ) -> None:
        """Add default comments for non-interactive mode."""
        # Sort blocks by line number (reverse order to maintain positions)
        blocks.sort(key=lambda x: x['start_line'], reverse=True)

        for block in blocks:
            comment_lines = self.comment_template.strip().split('\n')
            lines[block['start_line'] : block['start_line']] = comment_lines

        # Add end-of-main-body comment
        main_body_end = self._find_end_of_main_body(lines)
        if main_body_end < len(lines):
            end_comment = [
                "",
                "//",
                "// ADT ExampleBlock: This is the end of the main body.",
                "// Example blocks should be placed above this point for DITA 1.3 compliance.",
                "//",
            ]
            lines[main_body_end:main_body_end] = end_comment

    def _get_single_char_input(self) -> str:
        """Get single character input without requiring Enter."""
        try:
            import termios
            import tty
            import sys

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.cbreak(fd)
                choice = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            return choice
        except (ImportError, AttributeError):
            # Fallback for systems without termios/tty (e.g., Windows)
            # Note: This fallback doesn't match the single-character behavior of the termios version
            user_input = input().strip()
            return user_input[:1] if user_input else '\r'

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


def create_processor(
    batch_mode: bool = False, quiet_mode: bool = False
) -> ExampleBlockProcessor:
    """Create an ExampleBlockProcessor with appropriate settings."""
    detector = ExampleBlockDetector()
    return ExampleBlockProcessor(
        detector, interactive=not batch_mode, quiet_mode=quiet_mode
    )


class ExampleBlockModule(ADTModule):
    """
    ADTModule implementation for ExampleBlock plugin.

    Detects and fixes AsciiDoc example blocks that are placed in invalid locations
    according to DITA 1.3 specification (within sections, other blocks, or lists).
    """

    @property
    def name(self) -> str:
        """Module name identifier."""
        return "ExampleBlock"

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
        # ExampleBlock doesn't require special initialization
        pass

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the module to process files and detect/fix example block issues.

        Args:
            context: Processing context containing files and configuration

        Returns:
            Dict containing processing results and statistics
        """
        files = context.get('files', [])
        results = {
            'files_processed': 0,
            'files_modified': 0,
            'issues_found': 0,
            'issues_fixed': 0
        }

        processor = create_processor(
            batch_mode=context.get('batch_mode', True),
            quiet_mode=context.get('quiet_mode', False)
        )

        for file_path in files:
            if file_path.endswith('.adoc'):
                success = process_example_block_file(file_path, processor)
                if success:
                    results['files_processed'] += 1
                    # Note: More detailed statistics would require modifying
                    # the process_example_block_file function

        return results


def main():
    """Main entry point for the plugin."""
    parser = common_arg_parser("ExampleBlock", __description__)
    args = parser.parse_args()

    if not is_plugin_enabled("ExampleBlock"):
        print("ExampleBlock plugin is disabled")
        return

    processor = create_processor(
        batch_mode=False, quiet_mode=args.quiet if hasattr(args, 'quiet') else False
    )

    def process_file_wrapper(filepath):
        return process_example_block_file(filepath, processor)

    process_adoc_files(args, process_file_wrapper)


if __name__ == "__main__":
    main()
