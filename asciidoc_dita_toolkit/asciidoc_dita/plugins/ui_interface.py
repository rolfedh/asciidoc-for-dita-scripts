"""
User interface abstraction for the ContentType plugin.

This module provides an abstraction layer for user interaction, making it easier
to test and potentially support different UI modes (CLI, GUI, batch).
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, List
from .content_type_detector import DetectionResult


logger = logging.getLogger(__name__)


class Highlighter:
    """Simple text highlighter for console output."""

    def __init__(self, text: str):
        self.text = text

    def warn(self) -> str:
        return f"\033[0;31m{self.text}\033[0m"

    def bold(self) -> str:
        return f"\033[1m{self.text}\033[0m"

    def highlight(self) -> str:
        return f"\033[0;36m{self.text}\033[0m"

    def success(self) -> str:
        return f"\033[0;32m{self.text}\033[0m"


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


class ConsoleUI(UIInterface):
    """Console-based user interface implementation."""
    
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
        print(f"  ❌ Error: {error_message}")
    
    def show_success(self, success_message: str) -> None:
        """Display a success message to the user."""
        print(f"  ✓ {success_message}")
    
    def show_warning(self, warning_message: str) -> None:
        """Display a warning message to the user."""
        print(f"  ⚠️  Warning: {warning_message}")
    
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
            print(f"\nContent type not specified. Based on analysis, this appears to be a {Highlighter(suggested_type).highlight()}.")
            if detection_result.reasoning:
                print(f"Reasoning: {'; '.join(detection_result.reasoning[:2])}")  # Show first 2 reasons
            print("\nSelect content type:")
        else:
            print("\nNo content type detected. Please select:")
        
        # Display options
        for i, option in enumerate(self.content_type_options, 1):
            if i == suggested_index:
                print(f"[{i}] ✓ {Highlighter(option).highlight()} (recommended)")
            elif option == "TBD" and not suggested_index:
                print(f"[{i}] ✓ {Highlighter(option).highlight()} (type not detected)")
            else:
                print(f"[{i}]   {option}")
        
        print("[7] Skip this file")
        print("[8] Quit")
        
        # Set default choice message
        prompt_msg = f"Choice (1-8) [{suggested_index}]: " if suggested_index else "Choice (1-8): "
        
        while True:
            try:
                choice = input(prompt_msg).strip()
                
                # Use suggested default if user just presses Enter
                if choice == "" and suggested_index:
                    choice = str(suggested_index)
                elif choice == "":
                    # No suggestion, default to 6 (TBD)
                    choice = "6"
                
                if choice == "7":
                    logger.debug("User chose to skip file")
                    return None
                if choice == "8":
                    logger.info("User requested to quit")
                    self.exit_requested = True
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= 6:
                    selected_type = self.content_type_options[choice_num - 1]
                    logger.info("User selected content type: %s", selected_type)
                    return selected_type
                else:
                    print("Please enter a number between 1 and 8.")
                    
            except (ValueError, KeyboardInterrupt, EOFError):
                print(f"\nDefaulting to {Highlighter('TBD').highlight()} (type not detected).")
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
        print(f"  ❌ Error: {error_message}")
    
    def show_success(self, success_message: str) -> None:
        """Display a success message to the user."""
        print(f"  ✓ {success_message}")
    
    def show_warning(self, warning_message: str) -> None:
        """Display a warning message to the user."""
        print(f"  ⚠️  Warning: {warning_message}")
    
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


class TestUI(UIInterface):
    """Test user interface for automated testing."""
    
    def __init__(self, responses: Optional[List[str]] = None):
        self.responses = responses or []
        self.response_index = 0
        self.messages = []
        self.errors = []
        self.successes = []
        self.warnings = []
        self.prompts = []
        self.exit_requested = False
        logger.debug("TestUI initialized with %d responses", len(self.responses))
    
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
            elif response == "QUIT":
                self.exit_requested = True
                return None
            else:
                return response
        
        # Default fallback
        return detection_result.suggested_type or "TBD"
    
    def should_exit(self) -> bool:
        """Check if exit was requested during testing."""
        return self.exit_requested