"""
User interface abstraction for the ContentType plugin.

This module provides an abstraction layer for user interaction, making it easier
to test and potentially support different UI modes (CLI, GUI, batch).
"""

import logging
import sys
from abc import ABC, abstractmethod
from typing import Optional, List
from .content_type_detector import DetectionResult


logger = logging.getLogger(__name__)


class UIInterface(ABC):
    """Abstract interface for user interaction."""
    
    @abstractmethod
    def show_message(self, message: str) -> None:
        """Display a message to the user."""
        pass
    
    @abstractmethod
    def show_error(self, error_message: str) -> None:
        """Display an error message to the user."""
        pass
    
    @abstractmethod
    def show_success(self, success_message: str) -> None:
        """Display a success message to the user."""
        pass
    
    @abstractmethod
    def show_warning(self, warning_message: str) -> None:
        """Display a warning message to the user."""
        pass
    
    @abstractmethod
    def prompt_content_type(self, detection_result: DetectionResult) -> Optional[str]:
        """
        Prompt user to select content type.
        
        Args:
            detection_result: Result of content type detection with suggestions
            
        Returns:
            Selected content type string or None if skipped
        """
        pass
    
    @abstractmethod
    def should_exit(self) -> bool:
        """Check if the user wants to exit the application."""
        pass


class MinimalistConsoleUI(UIInterface):
    """Minimalist console-based user interface implementation."""
    
    def __init__(self):
        self.exit_requested = False
        self.content_type_options = [
            ("A", "ASSEMBLY"),
            ("C", "CONCEPT"), 
            ("P", "PROCEDURE"),
            ("R", "REFERENCE"),
            ("S", "SNIPPET"),
            ("T", "TBD")
        ]
        logger.debug("MinimalistConsoleUI initialized")
    
    def show_message(self, message: str) -> None:
        """Display a message to the user."""
        print(message)
    
    def show_error(self, error_message: str) -> None:
        """Display an error message to the user."""
        print(f"Error: {error_message}")
    
    def show_success(self, success_message: str) -> None:
        """Display a success message to the user."""
        print(success_message)
    
    def show_warning(self, warning_message: str) -> None:
        """Display a warning message to the user."""
        print(f"Warning: {warning_message}")
    
    def prompt_content_type(self, detection_result: DetectionResult) -> Optional[str]:
        """
        Prompt user to select content type with minimalist interface.
        
        Args:
            detection_result: Result of content type detection with suggestions
            
        Returns:
            Selected content type string or None if skipped
        """

        logger.debug("Prompting user for content type selection")
        
        suggested_type = detection_result.suggested_type
        
        # Show analysis
        if suggested_type:
            reasoning = detection_result.reasoning[0] if detection_result.reasoning else ""
            print(f"Analysis: {suggested_type} ({reasoning})")
        else:
            print("Analysis: TBD (content analysis failed)")
        
        # Build type menu with emphasized first letters
        type_menu = []
        for letter, type_name in self.content_type_options:
            type_menu.append(f"{letter.upper()}{type_name[1:]}")
        
        print(f"Type: {', '.join(type_menu)}")
        
        # Show suggestion
        if suggested_type:
            print(f"Suggestion: {suggested_type}.")
        else:
            print("Suggestion: TBD.")
        
        print("Press: Enter to accept; the first letter of a type; Ctrl+C to quit; or Ctrl+S to skip")
        
        while True:
            try:
                # Try to get single character input
                choice = self._get_single_char_input()
                
                # Handle Enter key (accept suggestion)
                if choice in ['\r', '\n']:
                    chosen_type = suggested_type or "TBD"
                    return chosen_type
                
                # Handle Ctrl+C (quit)
                if choice == '\x03':
                    raise KeyboardInterrupt
                
                # Handle Ctrl+S (skip)
                if choice == '\x13':
                    return None
                
                # Handle type selection by first letter
                choice_upper = choice.upper()
                for letter, type_name in self.content_type_options:
                    if choice_upper == letter:
                        return type_name
                
                # Invalid choice
                print("Invalid choice. Press Enter to accept suggestion, first letter of type, Ctrl+C to quit, or Ctrl+S to skip.")
                continue
                    
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                self.exit_requested = True
                return None
    
    def _get_single_char_input(self) -> str:
        """Get single character input without requiring Enter."""
        try:
            import termios
            import tty
            
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
            user_input = input().strip()
            return user_input[:1] if user_input else '\r'
    
    def should_exit(self) -> bool:
        """Check if the user wants to exit the application."""
        return self.exit_requested


class QuietModeUI(UIInterface):
    """Quiet mode user interface that automatically assigns TBD."""
    
    def __init__(self):
        logger.debug("QuietModeUI initialized")
    
    def show_message(self, message: str) -> None:
        """Suppress all messages in quiet mode."""
        pass
    
    def show_error(self, error_message: str) -> None:
        """Show errors even in quiet mode."""
        print(f"Error: {error_message}")
    
    def show_success(self, success_message: str) -> None:
        """Show success messages in quiet mode."""
        print(success_message)
    
    def show_warning(self, warning_message: str) -> None:
        """Suppress warnings in quiet mode."""
        pass
    
    def prompt_content_type(self, detection_result: DetectionResult) -> Optional[str]:
        """
        Return TBD without prompting in quiet mode.
        
        Args:
            detection_result: Result of content type detection with suggestions
            
        Returns:
            Always returns TBD
        """
        return "TBD"
    
    def should_exit(self) -> bool:
        """Quiet mode never exits early."""
        return False


class ConsoleUI(UIInterface):
    """Original console-based user interface (for backwards compatibility)."""
    
    def __init__(self):
        self.exit_requested = False
        self.content_type_options = [
            "ASSEMBLY",
            "CONCEPT", 
            "PROCEDURE",
            "REFERENCE",
            "SNIPPET",
            "TBD"
        ]
        logger.debug("ConsoleUI initialized")
    
    def show_message(self, message: str) -> None:
        """Display a message to the user."""
        print(message)
    
    def show_error(self, error_message: str) -> None:
        """Display an error message to the user."""
        print(f"❌ Error: {error_message}")
    
    def show_success(self, success_message: str) -> None:
        """Display a success message to the user."""
        print(f"✓ {success_message}")
    
    def show_warning(self, warning_message: str) -> None:
        """Display a warning message to the user."""
        print(f"⚠️  Warning: {warning_message}")
    
    def prompt_content_type(self, detection_result: DetectionResult) -> Optional[str]:
        """
        Prompt user to select content type interactively with smart pre-selection.
        
        Args:
            detection_result: Result of content type detection with suggestions
            
        Returns:
            Selected content type string or None if skipped
        """
        logger.debug("Prompting user for content type selection")
        
        suggested_type = detection_result.suggested_type
        suggested_index = None
        
        if suggested_type and suggested_type in self.content_type_options:
            suggested_index = self.content_type_options.index(suggested_type) + 1
        
        # Display context and suggestion
        if suggested_type:
            print(f"\nContent type not specified. Based on analysis, this appears to be a {suggested_type}.")
            if detection_result.reasoning:
                print(f"Reasoning: {'; '.join(detection_result.reasoning[:2])}")  # Show first 2 reasons
        else:
            print("\nNo content type detected.")
        
        # Build the compact option display
        options_display = []
        for i, option in enumerate(self.content_type_options, 1):
            if i == suggested_index:
                options_display.append(f"{i} {option} 💡")
            else:
                options_display.append(f"{i} {option}")
        options_display.append("7 Skip")
        
        print(f"\nType: {', '.join(options_display)}")
        
        # Show suggestion line
        if suggested_index:
            suggested_option = self.content_type_options[suggested_index - 1]
            print(f"💡 Suggestion: {suggested_index} — Press Enter to accept, 1–7 to choose, or Ctrl+C to quit")
            prompt_msg = ""
        else:
            print("Press 1–7 to choose, or Ctrl+C to quit")
            prompt_msg = ""
        
        while True:
            try:
                import termios
                import tty
                
                # Get single character input without requiring Enter
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.cbreak(fd)
                    choice = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
                # Handle Enter key (accept suggestion)
                if choice == '\r' or choice == '\n':
                    if suggested_index:
                        choice = str(suggested_index)
                    else:
                        choice = "6"  # Default to TBD if no suggestion
                
                # Handle quit (Ctrl+C equivalent)
                if choice == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                
                if choice == "7":
                    logger.debug("User chose to skip file")
                    return None
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= 6:
                        selected_type = self.content_type_options[choice_num - 1]
                        print(f"✅ {selected_type} chosen")
                        logger.info("User selected content type: %s", selected_type)
                        return selected_type
                    elif choice_num == 7:
                        logger.debug("User chose to skip file")
                        return None
                    else:
                        print("Please press a number between 1 and 7.")
                        continue
                except ValueError:
                    print("Please press a number between 1 and 7.")
                    continue
                    
            except (KeyboardInterrupt, EOFError):
                print(f"\nDefaulting to TBD (type not detected).")
                logger.info("User input interrupted, defaulting to TBD")
                return "TBD"
            except ImportError:
                # Fallback to regular input if termios/tty not available (e.g., Windows)
                return self._prompt_content_type_fallback(detection_result, suggested_index)
    
    def _prompt_content_type_fallback(self, detection_result: DetectionResult, suggested_index: Optional[int]) -> Optional[str]:
        """
        Fallback prompt method for systems without termios/tty support.
        
        Args:
            detection_result: Result of content type detection with suggestions
            suggested_index: Index of suggested option (1-based)
            
        Returns:
            Selected content type string or None if skipped
        """
        if suggested_index:
            prompt_msg = f"[{suggested_index}]: "
        else:
            prompt_msg = "Choice: "
        
        while True:
            try:
                choice = input(prompt_msg).strip()
                
                # Use suggested default if user just presses Enter
                if choice == "" and suggested_index:
                    choice = str(suggested_index)
                elif choice == "":
                    choice = "6"  # Default to TBD
                
                if choice == "7":
                    logger.debug("User chose to skip file")
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= 6:
                    selected_type = self.content_type_options[choice_num - 1]
                    print(f"✅ {selected_type} chosen")
                    logger.info("User selected content type: %s", selected_type)
                    return selected_type
                elif choice_num == 7:
                    logger.debug("User chose to skip file")
                    return None
                else:
                    print("Please enter a number between 1 and 7.")
                    
            except (ValueError, KeyboardInterrupt, EOFError):
                print(f"\nDefaulting to TBD (type not detected).")
                logger.info("User input interrupted, defaulting to TBD")
                return "TBD"
    
    def should_exit(self) -> bool:
        """Check if the user wants to exit the application."""
        return self.exit_requested


class BatchUI(UIInterface):
    """Batch mode user interface that doesn't prompt for input."""
    
    def __init__(self, default_type: str = "TBD"):
        self.default_type = default_type
        logger.debug("BatchUI initialized with default type: %s", default_type)
    
    def show_message(self, message: str) -> None:
        """Display a message to the user."""
        print(message)
    
    def show_error(self, error_message: str) -> None:
        """Display an error message to the user."""
        print(f"❌ Error: {error_message}")
    
    def show_success(self, success_message: str) -> None:
        """Display a success message to the user."""
        print(f"✓ {success_message}")
    
    def show_warning(self, warning_message: str) -> None:
        """Display a warning message to the user."""
        print(f"⚠️  Warning: {warning_message}")
    
    def prompt_content_type(self, detection_result: DetectionResult) -> Optional[str]:
        """
        Return suggested type or default without prompting.
        
        Args:
            detection_result: Result of content type detection with suggestions
            
        Returns:
            Suggested content type or default type
        """
        suggested_type = detection_result.suggested_type
        if suggested_type:
            logger.info("Using suggested content type: %s", suggested_type)
            return suggested_type
        else:
            logger.info("No suggestion found, using default: %s", self.default_type)
            return self.default_type
    
    def should_exit(self) -> bool:
        """Batch mode never exits early."""
        return False


class MockUI(UIInterface):
    """Mock user interface for automated testing."""
    
    def __init__(self, responses: Optional[List[str]] = None):
        self.responses = responses or []
        self.response_index = 0
        self.messages = []
        self.errors = []
        self.successes = []
        self.warnings = []
        self.prompts = []
        self.exit_requested = False
        logger.debug("MockUI initialized with %d responses", len(self.responses))
    
    def show_message(self, message: str) -> None:
        """Store message for testing verification."""
        self.messages.append(message)
    
    def show_error(self, error_message: str) -> None:
        """Store error for testing verification."""
        self.errors.append(error_message)
    
    def show_success(self, success_message: str) -> None:
        """Store success message for testing verification."""
        self.successes.append(success_message)
    
    def show_warning(self, warning_message: str) -> None:
        """Store warning for testing verification."""
        self.warnings.append(warning_message)
    
    def prompt_content_type(self, detection_result: DetectionResult) -> Optional[str]:
        """
        Return pre-configured response for testing.
        
        Args:
            detection_result: Result of content type detection with suggestions
            
        Returns:
            Pre-configured response or None
        """
        self.prompts.append(detection_result)
        
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
            
            if response == "SKIP":
                return None
            else:
                return response
        
        # Default fallback
        return detection_result.suggested_type or "TBD"
    
    def should_exit(self) -> bool:
        """Check if exit was requested during testing."""
        return self.exit_requested


def register_subcommand(subparsers):
    """This module doesn't register as a subcommand - it's a helper module."""
    pass