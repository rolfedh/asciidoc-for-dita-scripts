"""
ContentType Plugin with Interactive UI

This plugin processes AsciiDoc files to ensure proper :_mod-docs-content-type: attributes
are present and correctly formatted. It provides an interactive UI for handling various
content type scenarios including missing, deprecated, and misplaced attributes.

Based on the ContentType UI Design Specification.
"""

__description__ = "Add :_mod-docs-content-type: labels with interactive UI for handling various content type scenarios."

import os
import re
import argparse
from typing import Optional, List, Tuple, Dict, Any

from ..file_utils import process_adoc_files, common_arg_parser, read_text_preserve_endings, write_text_preserve_endings
from ..ui_framework import (
    BaseInteractiveUI, IssueContext, UserChoice, SeverityLevel, InteractionMode,
    ContentTypeChoices, smart_content_type_detection, format_file_content_preview
)


class ContentTypeUI(BaseInteractiveUI):
    """Interactive UI for ContentType plugin"""
    
    def __init__(self, mode: InteractionMode = InteractionMode.INTERACTIVE, 
                 quiet: bool = False, verbose: bool = False):
        super().__init__(mode, quiet, verbose)
        self.content_type_patterns = {
            'current': re.compile(r'^:_mod-docs-content-type:\s*(.*)$', re.MULTILINE),
            'deprecated_content': re.compile(r'^:_content-type:\s*(.*)$', re.MULTILINE),
            'deprecated_module': re.compile(r'^:_module-type:\s*(.*)$', re.MULTILINE),
            'commented': re.compile(r'^//+\s*:_mod-docs-content-type:\s*(.*)$', re.MULTILINE)
        }
    
    def find_content_type_line(self, content: str, pattern_name: str) -> Optional[Tuple[re.Match, int, str]]:
        """
        Find content type pattern line by line to avoid multi-line matching issues
        Returns: (match_object, line_number, line_content) or None
        """
        lines = content.split('\n')
        pattern = self.content_type_patterns[pattern_name]
        
        for line_num, line in enumerate(lines, 1):
            # Use match() instead of search() to ensure we match from start of line
            if pattern_name == 'current':
                match = re.match(r':_mod-docs-content-type:\s*(.*)', line)
            elif pattern_name == 'deprecated_content':
                match = re.match(r':_content-type:\s*(.*)', line)
            elif pattern_name == 'deprecated_module':
                match = re.match(r':_module-type:\s*(.*)', line)
            elif pattern_name == 'commented':
                match = re.match(r'//+\s*:_mod-docs-content-type:\s*(.*)', line)
            else:
                continue
                
            if match:
                # Calculate position in full content for compatibility
                line_start = sum(len(l) + 1 for l in lines[:line_num-1])
                # Create a compatible match object
                class LineMatch:
                    def __init__(self, match_obj, start_pos):
                        self._match = match_obj
                        self._start = start_pos
                    def group(self, n): return self._match.group(n)
                    def start(self): return self._start
                
                return LineMatch(match, line_start), line_num, line
        
        return None
    
    def analyze_file_content(self, file_path: str, content: str) -> List[IssueContext]:
        """Analyze file content and return list of issues found"""
        issues = []
        
        # Check for existing content type attributes using line-by-line matching
        current_result = self.find_content_type_line(content, 'current')
        deprecated_content_result = self.find_content_type_line(content, 'deprecated_content')
        deprecated_module_result = self.find_content_type_line(content, 'deprecated_module')
        commented_result = self.find_content_type_line(content, 'commented')
        
        # Scenario 1: Commented out content type (always check first, independent of others)
        if commented_result:
            commented_match, line_num, line_content = commented_result
            commented_value = commented_match.group(1).strip()
            
            issues.append(IssueContext(
                file_path=file_path,
                line_number=line_num,
                severity=SeverityLevel.ERROR,
                title="Required content type attribute is disabled",
                description=f"Issue: Content type is commented out\nImpact: Vale rules cannot validate this file properly",
                current_content=line_content,
                suggested_fix=f":_mod-docs-content-type: {commented_value}",
                explanation="Content type is commented out, preventing proper Vale validation.",
                additional_info={'scenario': 'commented', 'commented_value': commented_value}
            ))
        
        # Scenario 2: Deprecated :_content-type: attribute
        elif deprecated_content_result:
            deprecated_content_match, line_num, line_content = deprecated_content_result
            old_value = deprecated_content_match.group(1).strip()
            
            issues.append(IssueContext(
                file_path=file_path,
                line_number=line_num,
                severity=SeverityLevel.WARNING,
                title="Deprecated content type attribute detected",
                description=f"Found: :_content-type: {old_value}\nIssue: This attribute format is deprecated in modern Vale rules",
                current_content=line_content,
                suggested_fix=f":_mod-docs-content-type: {old_value}",
                explanation="The :_content-type: attribute is deprecated. Modern Vale rules require :_mod-docs-content-type: for proper validation.",
                additional_info={'scenario': 'deprecated_content', 'old_value': old_value}
            ))
        
        # Scenario 3: Deprecated :_module-type: attribute  
        elif deprecated_module_result:
            deprecated_module_match, line_num, line_content = deprecated_module_result
            old_value = deprecated_module_match.group(1).strip()
            
            issues.append(IssueContext(
                file_path=file_path,
                line_number=line_num,
                severity=SeverityLevel.SUGGESTION,
                title="Legacy attribute format detected",
                description=f"Found: :_module-type: {old_value}\nNote: This is an older format that should be updated",
                current_content=line_content,
                suggested_fix=f":_mod-docs-content-type: {old_value}",
                explanation="This is an older format that should be updated for consistency.",
                additional_info={'scenario': 'deprecated_module', 'old_value': old_value}
            ))
        
        # Scenario 4: Current format but check placement and value
        elif current_result:
            current_match, line_num, line_content = current_result
            current_value = current_match.group(1).strip()
            
            # Check if it's properly placed (should be at the top, before title)
            title_match = re.search(r'^=\s+', content, re.MULTILINE)
            if title_match and current_match.start() > title_match.start():
                issues.append(IssueContext(
                    file_path=file_path,
                    line_number=line_num,
                    severity=SeverityLevel.WARNING,
                    title="Content type attribute misplaced",
                    description="Issue: :_mod-docs-content-type: should be at the top of the file\nCurrent position: After title\nRequired position: Before ID and title",
                    current_content=line_content,
                    suggested_fix="Move to correct position",
                    explanation="Content type should be at the top of the file for proper processing.",
                    additional_info={'scenario': 'misplaced', 'current_value': current_value}
                ))
            
            # Check if value is empty
            elif not current_value:
                issues.append(IssueContext(
                    file_path=file_path,
                    line_number=line_num,
                    severity=SeverityLevel.ERROR,
                    title="Content type attribute has no value",
                    description="Found: :_mod-docs-content-type:\nIssue: Missing required value",
                    current_content=line_content,
                    suggested_fix="Set appropriate content type value",
                    explanation="Content type attribute exists but has no value.",
                    additional_info={'scenario': 'empty_value'}
                ))
            else:
                # Attribute is correctly defined
                if self.verbose:
                    self.print_info(f"✅ PASS: Content type correctly defined in {file_path}")
                    self.print_info(f"Status: :_mod-docs-content-type: {current_value} (valid)")
        
        # Scenario 5: Missing content type entirely
        else:
            issues.append(IssueContext(
                file_path=file_path,
                severity=SeverityLevel.ERROR,
                title="Missing required content type attribute",
                description="Issue: No :_mod-docs-content-type: attribute found\nImpact: Vale cannot validate this file type",
                current_content="",
                suggested_fix="Add appropriate content type attribute",
                explanation="No content type attribute found. This is required for proper Vale validation.",
                additional_info={'scenario': 'missing'}
            ))
        
        return issues
    
    def handle_issue(self, context: IssueContext) -> UserChoice:
        """Handle a specific content type issue with interactive UI"""
        scenario = context.additional_info.get('scenario', 'unknown')
        
        # Check for existing batch choice
        if scenario in self.batch_choices:
            choice = self.batch_choices[scenario]
            self.print_verbose(f"Applying batch choice '{choice}' for {scenario}")
            return UserChoice(choice, apply_to_all=True)
        
        # Auto mode - apply fixes automatically
        if self.mode == InteractionMode.AUTO:
            return self._get_auto_choice(context, scenario)
        
        # Review mode - just report, no changes
        if self.mode == InteractionMode.REVIEW:
            self._display_review_info(context)
            return UserChoice('n')  # No changes in review mode
        
        # Interactive and Guided modes
        return self._handle_interactive(context, scenario)
    
    def _get_auto_choice(self, context: IssueContext, scenario: str) -> UserChoice:
        """Get automatic choice based on scenario"""
        if scenario == 'commented':
            commented_value = context.additional_info.get('commented_value', '')
            return UserChoice('y', value=commented_value)  # Auto-fix commented with value
        elif scenario in ['deprecated_content', 'deprecated_module']:
            old_value = context.additional_info.get('old_value', '')
            return UserChoice('y', value=old_value)  # Auto-fix deprecated with value
        elif scenario in ['missing', 'empty_value']:
            # Try smart detection for missing content type
            content = ""
            try:
                lines = read_text_preserve_endings(context.file_path)
                content = ''.join(line + ending for line, ending in lines)
            except:
                pass
            
            suggested_type = smart_content_type_detection(context.file_path, content)
            if suggested_type:
                return UserChoice('y', value=suggested_type)
            else:
                return UserChoice('y', value='TBD')  # Default to TBD if can't detect
        elif scenario == 'misplaced':
            current_value = context.additional_info.get('current_value', '')
            return UserChoice('y', value=current_value)  # Auto-fix misplaced with value
        
        return UserChoice('n')  # Default to no change
    
    def _display_review_info(self, context: IssueContext):
        """Display issue information in review mode"""
        print(self.format_issue_header(context))
        print(f"\nDescription: {context.description}")
        if context.suggested_fix:
            print(f"Suggested fix: {context.suggested_fix}")
        print()
    
    def _handle_interactive(self, context: IssueContext, scenario: str) -> UserChoice:
        """Handle interactive user input for issues"""
        print("\n" + "="*60)
        print(self.format_issue_header(context))
        print("="*60)
        
        if context.description:
            print(f"\n{context.description}")
        
        if context.explanation:
            print(f"\n{context.explanation}")
        
        # Show current content if available
        if context.current_content:
            print(f"\nCurrent content:")
            print(f"  {context.current_content}")
        
        return self._get_scenario_specific_choice(context, scenario)
    
    def _get_scenario_specific_choice(self, context: IssueContext, scenario: str) -> UserChoice:
        """Get user choice specific to the scenario type"""
        
        if scenario == 'deprecated_content':
            old_value = context.additional_info['old_value']
            choices = [
                ('y', f"Replace with :_mod-docs-content-type: {old_value} (recommended)"),
                ('n', "Skip this file"),
                ('a', "Apply to all deprecated attributes in session"),
                ('?', "Show documentation link"),
                ('q', "Quit")
            ]
            
            choice = self.show_choices_menu(choices, "Actions:")
            if choice == 'a':
                self.batch_choices['deprecated_content'] = 'y'
                return UserChoice('y', apply_to_all=True)
            elif choice == '?':
                self._show_help('deprecated_content')
                return self._get_scenario_specific_choice(context, scenario)
            
            return UserChoice(choice, value=old_value if choice == 'y' else None)
        
        elif scenario == 'deprecated_module':
            old_value = context.additional_info['old_value']
            choices = [
                ('y', "Apply modernization fix"),
                ('n', "Keep legacy format"),
                ('a', "Modernize all legacy attributes"),
                ('?', "Show migration guide"),
                ('q', "Quit")
            ]
            
            choice = self.show_choices_menu(choices, "Actions:")
            if choice == 'a':
                self.batch_choices['deprecated_module'] = 'y'
                return UserChoice('y', apply_to_all=True)
            elif choice == '?':
                self._show_help('deprecated_module')
                return self._get_scenario_specific_choice(context, scenario)
            
            return UserChoice(choice, value=old_value if choice == 'y' else None)
        
        elif scenario == 'commented':
            commented_value = context.additional_info['commented_value']
            choices = [
                ('y', f"Uncomment attribute (recommended)"),
                ('n', "Leave commented"),
                ('a', "Uncomment all similar cases"),
                ('d', "Delete comment entirely"),
                ('?', "Show why this is required"),
                ('q', "Quit")
            ]
            
            choice = self.show_choices_menu(choices, "Actions:")
            if choice == 'a':
                self.batch_choices['commented'] = 'y'
                return UserChoice('y', apply_to_all=True)
            elif choice == '?':
                self._show_help('commented')
                return self._get_scenario_specific_choice(context, scenario)
            
            return UserChoice(choice, value=commented_value if choice in ['y', 'd'] else None)
        
        elif scenario == 'misplaced':
            current_value = context.additional_info['current_value']
            choices = [
                ('y', "Move to correct position"),
                ('n', "Leave as-is"),
                ('a', "Fix all misplaced attributes"),
                ('?', "Show positioning guide"),
                ('q', "Quit")
            ]
            
            choice = self.show_choices_menu(choices, "Actions:")
            if choice == 'a':
                self.batch_choices['misplaced'] = 'y'
                return UserChoice('y', apply_to_all=True)
            elif choice == '?':
                self._show_help('misplaced')
                return self._get_scenario_specific_choice(context, scenario)
            
            return UserChoice(choice, value=current_value if choice == 'y' else None)
        
        elif scenario in ['missing', 'empty_value']:
            return self._handle_content_type_selection(context, scenario)
        
        # Default fallback
        return UserChoice('n')
    
    def _handle_content_type_selection(self, context: IssueContext, scenario: str) -> UserChoice:
        """Handle content type selection for missing or empty content types"""
        
        # Get file content for smart detection
        content = ""
        try:
            lines = read_text_preserve_endings(context.file_path)
            content = ''.join(line + ending for line, ending in lines)
        except:
            pass
        
        # Try smart detection first
        suggested_type = smart_content_type_detection(context.file_path, content)
        
        if suggested_type and self.mode == InteractionMode.GUIDED:
            print(f"\n🔍 ANALYZING: Content patterns detected...")
            print(f"Based on file analysis: Suggested content type is {suggested_type}")
            
            accept_choice = self.get_user_input(f"Accept suggestion '{suggested_type}'", ['y', 'n'], 'y')
            if accept_choice == 'y':
                return UserChoice('y', value=suggested_type)
        
        # Show content type selection menu
        print(f"\nSelect content type:")
        content_choices = ContentTypeChoices.get_choice_menu()
        content_choices.extend([
            ('?', "Show content type guide"),
            ('s', "Skip this file"),
            ('q', "Quit")
        ])
        
        choice = self.show_choices_menu(content_choices, "Actions:")
        
        if choice == '?':
            self._show_help('content_types')
            return self._handle_content_type_selection(context, scenario)
        elif choice in ['s', 'q']:
            return UserChoice(choice)
        elif choice in ContentTypeChoices.TYPES:
            content_type = ContentTypeChoices.get_type_name(choice)
            return UserChoice('y', value=content_type)
        
        return UserChoice('n')
    
    def _show_help(self, help_type: str):
        """Show context-sensitive help"""
        help_texts = {
            'deprecated_content': """
The :_content-type: attribute is deprecated in favor of :_mod-docs-content-type:.
Modern Vale rules require the new format for proper validation.
See: https://github.com/jhradilek/asciidoctor-dita-vale
            """,
            'deprecated_module': """
The :_module-type: attribute is a legacy format.
Updating to :_mod-docs-content-type: ensures consistency with current standards.
            """,
            'commented': """
Commented content type attributes prevent Vale from properly validating your content.
This can lead to missed errors and inconsistent documentation quality.
            """,
            'misplaced': """
Content type attributes should be placed at the very top of the file,
before the module ID and title for proper processing by Vale and other tools.
            """,
            'content_types': """
Content Type Guide:
• ASSEMBLY: Collection of modules covering a complete workflow
• CONCEPT: Explanatory content providing background and context  
• PROCEDURE: Step-by-step instructions for specific tasks
• REFERENCE: Quick lookup information (tables, lists, specs)
• SNIPPET: Reusable content fragments
• TBD: Temporary placeholder requiring expert classification
            """
        }
        
        if help_type in help_texts:
            print(help_texts[help_type])
            input("\nPress Enter to continue...")


def apply_content_type_fix(file_path: str, choice: UserChoice, context: IssueContext) -> bool:
    """Apply the selected fix to the file"""
    try:
        lines = read_text_preserve_endings(file_path)
        content = ''.join(line + ending for line, ending in lines)
        
        scenario = context.additional_info.get('scenario', 'unknown')
        
        if choice.action != 'y':
            return False  # No changes requested
        
        modified_content = content
        
        if scenario == 'deprecated_content':
            # Replace :_content-type: with :_mod-docs-content-type:
            old_value = context.additional_info['old_value']
            pattern = re.compile(r'^:_content-type:\s*.*$', re.MULTILINE)
            modified_content = pattern.sub(f':_mod-docs-content-type: {old_value}', content)
        
        elif scenario == 'deprecated_module':
            # Replace :_module-type: with :_mod-docs-content-type:
            old_value = context.additional_info['old_value']
            pattern = re.compile(r'^:_module-type:\s*.*$', re.MULTILINE)
            modified_content = pattern.sub(f':_mod-docs-content-type: {old_value}', content)
        
        elif scenario == 'commented':
            # Uncomment the content type attribute
            if choice.value:
                pattern = re.compile(r'^//+\s*:_mod-docs-content-type:\s*.*$', re.MULTILINE)
                modified_content = pattern.sub(f':_mod-docs-content-type: {choice.value}', content)
        
        elif scenario == 'misplaced':
            # Move content type to the top
            current_value = choice.value
            # Remove current content type
            pattern = re.compile(r'^:_mod-docs-content-type:.*$\n?', re.MULTILINE)
            modified_content = pattern.sub('', content)
            # Add at the top
            modified_content = f':_mod-docs-content-type: {current_value}\n' + modified_content
        
        elif scenario in ['missing', 'empty_value']:
            # Add or set content type value
            if scenario == 'empty_value':
                # Replace empty value
                pattern = re.compile(r'^:_mod-docs-content-type:\s*$', re.MULTILINE)
                modified_content = pattern.sub(f':_mod-docs-content-type: {choice.value}', content)
            else:
                # Add new content type at the top
                modified_content = f':_mod-docs-content-type: {choice.value}\n' + content
        
        # Write the modified content back
        if modified_content != content:
            modified_lines = []
            for line in modified_content.split('\n'):
                if line or modified_lines:  # Preserve original line endings
                    modified_lines.append((line, '\n'))
            if modified_lines and not modified_content.endswith('\n'):
                # Remove the last newline if original didn't have it
                last_line, _ = modified_lines[-1]
                modified_lines[-1] = (last_line, '')
            
            write_text_preserve_endings(file_path, modified_lines)
            return True
        
        return False
        
    except Exception as e:
        raise Exception(f"Failed to apply fix: {e}")


def process_file_with_ui(ui: ContentTypeUI, file_path: str):
    """Process a single file with the interactive UI"""
    try:
        # Read file content
        lines = read_text_preserve_endings(file_path)
        content = ''.join(line + ending for line, ending in lines)
        
        # Analyze for issues
        issues = ui.analyze_file_content(file_path, content)
        
        if not issues:
            ui.print_verbose(f"No issues found in {file_path}")
            return
        
        # Process each issue
        for issue in issues:
            choice = ui.handle_issue(issue)
            
            if choice.action == 'q':
                ui.print_info("Processing cancelled by user")
                return
            
            if choice.action == 'y':
                try:
                    if apply_content_type_fix(file_path, choice, issue):
                        ui.print_colored(f"Fixed {file_path}", SeverityLevel.SUCCESS)
                        ui.results.add_result(file_path, "fixed", issue.severity)
                    else:
                        ui.print_info(f"No changes needed for {file_path}")
                except Exception as e:
                    ui.print_colored(f"Error fixing {file_path}: {e}", SeverityLevel.ERROR)
                    ui.results.add_result(file_path, "error", SeverityLevel.ERROR)
            else:
                ui.print_info(f"Skipped {file_path}")
                ui.results.add_result(file_path, "skipped", issue.severity)
    
    except Exception as e:
        ui.print_colored(f"Error processing {file_path}: {e}", SeverityLevel.ERROR)
        ui.results.add_result(file_path, "error", SeverityLevel.ERROR)


def register_subcommand(subparsers):
    """Register the ContentType subcommand"""
    parser = subparsers.add_parser('ContentType', 
                                  help='Add :_mod-docs-content-type: labels with interactive UI')
    
    # Add common file/directory arguments
    common_arg_parser(parser)
    
    # Add ContentType-specific arguments
    parser.add_argument('--mode', '-m', 
                       choices=['auto', 'review', 'interactive', 'guided'],
                       default='interactive',
                       help='Interaction mode (default: interactive)')
    
    parser.add_argument('--batch', action='store_true',
                       help='Apply the same choice to all similar issues')
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without making changes')
    
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress non-essential output')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable detailed logging')
    
    parser.set_defaults(func=main)


def main(args):
    """Main entry point for ContentType plugin"""
    # Convert string mode to enum
    mode_map = {
        'auto': InteractionMode.AUTO,
        'review': InteractionMode.REVIEW,
        'interactive': InteractionMode.INTERACTIVE,
        'guided': InteractionMode.GUIDED
    }
    
    mode = mode_map.get(args.mode, InteractionMode.INTERACTIVE)
    
    # Override mode for dry-run
    if args.dry_run:
        mode = InteractionMode.REVIEW
        args.quiet = False  # Show output in dry-run mode
    
    # Create UI instance
    ui = ContentTypeUI(mode=mode, quiet=args.quiet, verbose=args.verbose)
    
    if not args.quiet:
        ui.print_info("ContentType Plugin - Interactive Content Type Management")
        ui.print_info(f"Mode: {args.mode}")
        if args.dry_run:
            ui.print_info("DRY RUN: No changes will be made")
        ui.print_info("")
    
    # Get list of files to process
    if args.file:
        if not os.path.isfile(args.file) or not args.file.endswith('.adoc'):
            ui.print_colored(f"Error: {args.file} is not a valid .adoc file", SeverityLevel.ERROR)
            return
        files_to_process = [args.file]
    else:
        # Use file_utils to find .adoc files
        from ..file_utils import find_adoc_files
        files_to_process = find_adoc_files(
            getattr(args, 'directory', '.'), 
            getattr(args, 'recursive', False)
        )
    
    if not files_to_process:
        ui.print_info("No AsciiDoc files found to process.")
        return
    
    # Process files using the UI framework
    def process_func(file_path):
        process_file_with_ui(ui, file_path)
    
    try:
        ui.process_files(files_to_process, process_func)
        ui.display_summary()
        
    except KeyboardInterrupt:
        ui.print_info("\nOperation cancelled by user")
    except Exception as e:
        ui.print_colored(f"Unexpected error: {e}", SeverityLevel.ERROR)
    
    return None


# Legacy functions for backward compatibility with tests

def get_content_type_from_filename(filename):
    """
    Guess the content type from the file name conventions.
    Returns one of 'ASSEMBLY', 'CONCEPT', 'PROCEDURE', 'REFERENCE', 'SNIPPET', or None.
    
    This function supports legacy test compatibility.
    """
    import os
    import re
    
    name = os.path.basename(filename).lower()
    if re.search(r'assembly[-_]', name):
        return 'ASSEMBLY'
    if re.search(r'con[-_]', name):
        return 'CONCEPT'
    if re.search(r'proc[-_]', name):
        return 'PROCEDURE'
    if re.search(r'ref[-_]', name):
        return 'REFERENCE'
    if re.search(r'snip[-_]', name):
        return 'SNIPPET'
    return None


def add_content_type_label(file_path, content_type):
    """
    Adds :_mod-docs-content-type: LABEL to the top of the file if not present.
    Does not overwrite an existing label.
    
    This function supports legacy test compatibility.
    """
    import re
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if label already exists
    if re.search(r'^:_mod-docs-content-type:', content, re.MULTILINE):
        print(f"Skipping {file_path}, label already present")
        return
    
    # Insert label at the top
    new_content = f":_mod-docs-content-type: {content_type}\n{content}"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Added label to {file_path}")
