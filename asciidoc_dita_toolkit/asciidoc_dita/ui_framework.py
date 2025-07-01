"""
Interactive UI Framework for AsciiDoc DITA Toolkit

This module provides a reusable framework for creating interactive command-line
interfaces for plugins. It handles user input, progress display, error handling,
and provides consistent styling across all plugins.

Design based on CONTENTTYPE_UI_DESIGN_SPECIFICATION.md
"""

import os
import sys
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class SeverityLevel(Enum):
    """Issue severity levels with visual styling"""
    SUGGESTION = ("💡", "SUGGESTION", "\033[0;36m")  # Cyan
    WARNING = ("⚠️", "WARNING", "\033[0;33m")         # Yellow
    ERROR = ("❌", "ERROR", "\033[0;31m")             # Red
    SUCCESS = ("✅", "SUCCESS", "\033[0;32m")         # Green
    INFO = ("📄", "INFO", "\033[0;37m")               # Gray


class InteractionMode(Enum):
    """User interaction modes"""
    AUTO = "auto"           # Automatic fixes without prompting
    REVIEW = "review"       # Report only, no changes
    INTERACTIVE = "interactive"  # Prompt for each change
    GUIDED = "guided"       # Step-by-step with explanations


@dataclass
class IssueContext:
    """Context information for an issue"""
    file_path: str
    line_number: Optional[int] = None
    severity: SeverityLevel = SeverityLevel.WARNING
    title: str = ""
    description: str = ""
    current_content: str = ""
    suggested_fix: str = ""
    explanation: str = ""
    additional_info: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}


@dataclass
class UserChoice:
    """User's choice and any associated data"""
    action: str  # 'y', 'n', 'a', 's', 'q', etc.
    value: Optional[str] = None  # For cases where user provides additional input
    apply_to_all: bool = False


class ProcessingResults:
    """Results of processing operations"""
    def __init__(self):
        self.processed_files = 0
        self.fixed_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.warning_count = 0
        self.files_with_issues = []
        
    def add_result(self, file_path: str, action: str, severity: SeverityLevel):
        """Add a processing result"""
        self.processed_files += 1
        if action == "fixed":
            self.fixed_count += 1
        elif action == "skipped":
            self.skipped_count += 1
        elif action == "error":
            self.error_count += 1
            
        if severity == SeverityLevel.WARNING:
            self.warning_count += 1
            
        self.files_with_issues.append({
            'file': file_path,
            'action': action,
            'severity': severity
        })


class BaseInteractiveUI(ABC):
    """Base class for interactive plugin UIs"""
    
    def __init__(self, mode: InteractionMode = InteractionMode.INTERACTIVE, 
                 quiet: bool = False, verbose: bool = False):
        self.mode = mode
        self.quiet = quiet
        self.verbose = verbose
        self.terminal_width = shutil.get_terminal_size().columns
        self.results = ProcessingResults()
        self.batch_choices = {}  # Store choices for "apply to all"
        
    def print_colored(self, text: str, severity: SeverityLevel):
        """Print colored text based on severity"""
        if self.quiet:
            return
            
        icon, label, color = severity.value
        reset = "\033[0m"
        
        # Check if stdout supports colors
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            print(f"{color}{icon} {label}: {text}{reset}")
        else:
            print(f"{icon} {label}: {text}")
    
    def print_info(self, text: str):
        """Print informational text"""
        if not self.quiet:
            print(text)
    
    def print_verbose(self, text: str):
        """Print verbose information"""
        if self.verbose and not self.quiet:
            print(f"🔍 DEBUG: {text}")
    
    def show_progress(self, current: int, total: int, file_path: str):
        """Show progress bar and current file"""
        if self.quiet or total <= 1:
            return
            
        # Calculate progress
        progress = int((current / total) * 20)  # 20-char progress bar
        bar = "█" * progress + "░" * (20 - progress)
        percentage = int((current / total) * 100)
        
        # Truncate filename for display
        max_filename_len = self.terminal_width - 50
        if len(file_path) > max_filename_len:
            display_path = "..." + file_path[-(max_filename_len-3):]
        else:
            display_path = file_path
            
        print(f"\rProcessing: {display_path} [{current}/{total}] {bar} {percentage}%", 
              end="", flush=True)
        
        if current == total:
            print()  # New line when complete
    
    def format_issue_header(self, context: IssueContext) -> str:
        """Format the issue header with file and location info"""
        icon, label, _ = context.severity.value
        
        if context.line_number:
            location = f" (Line {context.line_number})"
        else:
            location = ""
            
        header = f"📄 File: {context.file_path}{location}\n"
        header += f"{icon} {label}: {context.title}"
        
        return header
    
    def get_user_input(self, prompt: str, valid_choices: List[str], 
                      default: Optional[str] = None) -> str:
        """Get validated user input"""
        while True:
            try:
                if default:
                    display_prompt = f"{prompt} (default: {default}): "
                else:
                    display_prompt = f"{prompt}: "
                    
                choice = input(display_prompt).strip().lower()
                
                if not choice and default:
                    return default
                    
                if choice in valid_choices:
                    return choice
                    
                print(f"Invalid choice. Please select from: {', '.join(valid_choices)}")
                
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled by user")
                return 'q'
    
    def show_choices_menu(self, choices: List[tuple], title: str = "Choose an action:") -> str:
        """Show a menu of choices and get user selection"""
        print(f"\n{title}")
        for key, description in choices:
            print(f"  [{key}] {description}")
        print()
        
        valid_choices = [choice[0] for choice in choices]
        return self.get_user_input("Choice", valid_choices)
    
    def confirm_batch_operation(self, operation: str, count: int) -> bool:
        """Confirm a batch operation"""
        if self.mode == InteractionMode.AUTO:
            return True
            
        print(f"\n✅ Found {count} more files that {operation}")
        choice = self.get_user_input("Apply the same action to all", ['y', 'n'], 'y')
        return choice == 'y'
    
    @abstractmethod
    def handle_issue(self, context: IssueContext) -> UserChoice:
        """Handle a specific issue - must be implemented by plugins"""
        pass
    
    def process_files(self, file_paths: List[str], 
                     process_func) -> ProcessingResults:
        """Process a list of files with progress tracking"""
        total_files = len(file_paths)
        
        for i, file_path in enumerate(file_paths, 1):
            self.show_progress(i, total_files, file_path)
            
            try:
                process_func(file_path)
            except Exception as e:
                self.print_colored(f"Error processing {file_path}: {e}", 
                                 SeverityLevel.ERROR)
                self.results.add_result(file_path, "error", SeverityLevel.ERROR)
        
        return self.results
    
    def display_summary(self):
        """Display final processing summary"""
        if self.quiet:
            return
            
        print("\n" + "="*50)
        print("📊 PROCESSING COMPLETE")
        print("="*50)
        
        results = self.results
        print(f"Files processed: {results.processed_files}")
        
        if results.fixed_count > 0:
            self.print_colored(f"Fixed: {results.fixed_count} files", 
                             SeverityLevel.SUCCESS)
        if results.warning_count > 0:
            self.print_colored(f"Warnings: {results.warning_count} files", 
                             SeverityLevel.WARNING)
        if results.error_count > 0:
            self.print_colored(f"Errors: {results.error_count} files", 
                             SeverityLevel.ERROR)
        if results.skipped_count > 0:
            self.print_info(f"⏭️  Skipped: {results.skipped_count} files")
        
        if results.processed_files == 0:
            print("No files were processed.")


class ContentTypeChoices:
    """Content type definitions and descriptions"""
    
    TYPES = {
        '1': ('ASSEMBLY', 'Collection of modules on a topic'),
        '2': ('CONCEPT', 'Conceptual overview information'),
        '3': ('PROCEDURE', 'Step-by-step instructions'),
        '4': ('REFERENCE', 'Lookup information (tables, lists)'),
        '5': ('SNIPPET', 'Reusable content fragment'),
        '6': ('TBD', 'Temporary placeholder for unclassified content')
    }
    
    @classmethod
    def get_choice_menu(cls) -> List[tuple]:
        """Get formatted choices for menu display"""
        choices = []
        for key, (type_name, description) in cls.TYPES.items():
            choices.append((key, f"{type_name:<12} - {description}"))
        return choices
    
    @classmethod
    def get_type_name(cls, choice: str) -> Optional[str]:
        """Get type name from choice key"""
        if choice in cls.TYPES:
            return cls.TYPES[choice][0]
        return None


# Utility functions for common UI patterns
def truncate_text(text: str, max_length: int) -> str:
    """Truncate text with ellipsis if too long"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_file_content_preview(content: str, max_lines: int = 5) -> str:
    """Format file content for preview display"""
    lines = content.split('\n')
    if len(lines) <= max_lines:
        return content
        
    preview_lines = lines[:max_lines]
    remaining = len(lines) - max_lines
    
    result = '\n'.join(preview_lines)
    if remaining > 0:
        result += f"\n... ({remaining} more lines)"
    
    return result


def smart_content_type_detection(file_path: str, content: str) -> Optional[str]:
    """Attempt to detect content type from filename and content patterns"""
    filename = os.path.basename(file_path)
    
    # Filename-based detection
    prefixes = {
        ('assembly_', 'assembly-'): 'ASSEMBLY',
        ('con_', 'con-'): 'CONCEPT',
        ('proc_', 'proc-'): 'PROCEDURE',
        ('ref_', 'ref-'): 'REFERENCE',
        ('snip_', 'snip-'): 'SNIPPET'
    }
    
    for prefix_group, content_type in prefixes.items():
        if any(filename.startswith(prefix) for prefix in prefix_group):
            return content_type
    
    # Content-based detection
    lines = content.lower().split('\n')
    content_text = ' '.join(lines)
    
    # Look for procedural indicators
    step_indicators = ['1.', '2.', '3.', '. ', 'step', 'procedure', 'instructions']
    if any(indicator in content_text for indicator in step_indicators):
        return 'PROCEDURE'
    
    # Look for conceptual indicators
    concept_indicators = ['overview', 'introduction', 'concept', 'about', 'what is']
    if any(indicator in content_text for indicator in concept_indicators):
        return 'CONCEPT'
    
    # Look for reference indicators
    ref_indicators = ['table', 'list', 'reference', 'specification', 'parameters']
    if any(indicator in content_text for indicator in ref_indicators):
        return 'REFERENCE'
    
    return None  # Cannot determine automatically
