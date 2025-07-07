"""
File processing logic for the ContentType plugin.

This module handles file I/O operations and content type attribute manipulation
separated from UI and detection logic.
"""

import os
import logging
from typing import List, Tuple, Optional
from .content_type_detector import ContentTypeDetector, ContentTypeAttribute
from .ui_interface import UIInterface, QuietModeUI


logger = logging.getLogger(__name__)


class ContentTypeProcessor:
    """Handles file processing operations for content type management."""
    
    def __init__(self, detector: ContentTypeDetector, ui: UIInterface, 
                 file_reader=None, file_writer=None):
        """
        Initialize the processor with dependencies.
        
        Args:
            detector: Content type detector instance
            ui: User interface instance
            file_reader: Optional file reader function (for testing)
            file_writer: Optional file writer function (for testing)
        """
        self.detector = detector
        self.ui = ui
        self.file_reader = file_reader or self._default_file_reader
        self.file_writer = file_writer or self._default_file_writer
        logger.debug("ContentTypeProcessor initialized")
    
    def _default_file_reader(self, filepath: str) -> List[Tuple[str, str]]:
        """Default file reader using the toolkit's file utilities."""
        from ..file_utils import read_text_preserve_endings
        return read_text_preserve_endings(filepath)
    
    def _default_file_writer(self, filepath: str, lines: List[Tuple[str, str]]) -> None:
        """Default file writer using the toolkit's file utilities."""
        from ..file_utils import write_text_preserve_endings
        write_text_preserve_endings(filepath, lines)
    
    def validate_file_access(self, filepath: str) -> bool:
        """
        Validate that the file exists and is accessible.
        
        Args:
            filepath: Path to the file to validate
            
        Returns:
            True if file is accessible, False otherwise
        """
        if not os.path.exists(filepath):
            self.ui.show_error(f"File not found: {filepath}")
            return False
        
        if not os.access(filepath, os.R_OK):
            self.ui.show_error(f"Cannot read file: {filepath}")
            return False
        
        return True
    
    def read_file_safely(self, filepath: str) -> Optional[List[Tuple[str, str]]]:
        """
        Read file content safely with error handling.
        
        Args:
            filepath: Path to the file to read
            
        Returns:
            List of (text, ending) tuples or None if error occurred
        """
        try:
            lines = self.file_reader(filepath)
            if not lines:
                self.ui.show_warning(f"File is empty: {filepath}")
                return None
            return lines
        except PermissionError:
            self.ui.show_error(f"Permission denied: {filepath}")
            return None
        except UnicodeDecodeError:
            self.ui.show_error(f"Cannot decode file (not UTF-8): {filepath}")
            return None
        except Exception as e:
            self.ui.show_error(f"Error reading file: {e}")
            return None
    
    def write_file_safely(self, filepath: str, lines: List[Tuple[str, str]]) -> bool:
        """
        Write file content safely with error handling.
        
        Args:
            filepath: Path to the file to write
            lines: List of (text, ending) tuples to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.file_writer(filepath, lines)
            return True
        except PermissionError:
            self.ui.show_error(f"Permission denied writing to: {filepath}")
            return False
        except Exception as e:
            self.ui.show_error(f"Error writing file: {e}")
            return False
    
    def ensure_blank_line_after_attribute(self, lines: List[Tuple[str, str]], 
                                         index: int) -> List[Tuple[str, str]]:
        """
        Ensure there is a blank line after the content type attribute.
        
        Args:
            lines: List of (text, ending) tuples
            index: Index of the content type attribute line
            
        Returns:
            Modified lines with blank line after attribute
        """
        # If the attribute is the last line, add a blank line
        if index == len(lines) - 1:
            lines.append(("", "\n"))
        # If the next line is not blank, insert a blank line
        elif lines[index + 1][0].strip() != "":
            lines.insert(index + 1, ("", "\n"))
        
        return lines
    
    def update_existing_attribute(self, lines: List[Tuple[str, str]], 
                                 attribute: ContentTypeAttribute, 
                                 new_value: str) -> List[Tuple[str, str]]:
        """
        Update an existing content type attribute in place.
        
        Args:
            lines: List of (text, ending) tuples
            attribute: Existing attribute information
            new_value: New content type value
            
        Returns:
            Modified lines with updated attribute
        """
        i = attribute.line_index
        text, ending = lines[i]
        
        logger.debug("Updating existing attribute at line %d: %s -> %s", 
                    i, attribute.value, new_value)
        
        # Convert deprecated formats to current format
        if attribute.attribute_type == 'deprecated_content':
            text = text.replace(":_content-type:", ":_mod-docs-content-type:", 1)
        elif attribute.attribute_type == 'deprecated_module':
            text = text.replace(":_module-type:", ":_mod-docs-content-type:", 1)
        elif attribute.attribute_type == 'commented':
            # Uncomment the line
            text = text.replace("//:_mod-docs-content-type:", ":_mod-docs-content-type:", 1)
        
        # Update the value
        if ":_mod-docs-content-type:" in text:
            # Split on the attribute and rebuild with new value
            parts = text.split(":_mod-docs-content-type:", 1)
            text = f"{parts[0]}:_mod-docs-content-type: {new_value}"
        
        lines[i] = (text, ending)
        
        # Remove any duplicate current format lines
        current_format_indices = [j for j, (line_text, _) in enumerate(lines)
                                 if j != i and (line_text.strip().startswith(":_mod-docs-content-type:") or 
                                               line_text.strip().startswith("//:_mod-docs-content-type:"))]
        
        for j in sorted(current_format_indices, reverse=True):
            del lines[j]
            if j < i:  # Adjust index if we removed a line before the current one
                i -= 1
        
        # Ensure blank line after the attribute
        lines = self.ensure_blank_line_after_attribute(lines, i)
        
        return lines
    
    def add_new_attribute(self, lines: List[Tuple[str, str]], 
                         content_type: str) -> List[Tuple[str, str]]:
        """
        Add a new content type attribute at the beginning of the file.
        
        Args:
            lines: List of (text, ending) tuples
            content_type: Content type value to add
            
        Returns:
            Modified lines with new attribute
        """
        logger.debug("Adding new content type attribute: %s", content_type)
        
        # Insert at the beginning
        lines.insert(0, (f":_mod-docs-content-type: {content_type}", "\n"))
        
        # Ensure blank line after the attribute
        lines = self.ensure_blank_line_after_attribute(lines, 0)
        
        return lines
    
    def get_file_analysis(self, filepath: str, lines: List[Tuple[str, str]]) -> dict:
        """
        Get comprehensive analysis of a file for content type detection.
        
        Args:
            filepath: Path to the file
            lines: File content as list of (text, ending) tuples
            
        Returns:
            Dictionary with analysis results
        """
        filename = os.path.basename(filepath)
        title = self.detector.extract_document_title(lines)
        content = '\n'.join([text for text, _ in lines])
        
        detection_result = self.detector.get_comprehensive_suggestion(
            filename, title, content
        )
        
        return {
            'filename': filename,
            'title': title,
            'content': content,
            'detection_result': detection_result,
            'existing_attribute': self.detector.detect_existing_attribute(lines)
        }
    
    def process_file(self, filepath: str) -> bool:
        """
        Process a single file for content type attributes.
        
        Args:
            filepath: Path to the file to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        filename = os.path.basename(filepath)
        
        # File processing messages are handled by individual handlers
        
        # Validate file access
        if not self.validate_file_access(filepath):
            return False
        
        # Read file content
        lines = self.read_file_safely(filepath)
        if lines is None:
            return False
        
        # Get comprehensive analysis
        analysis = self.get_file_analysis(filepath, lines)
        existing_attribute = analysis['existing_attribute']
        detection_result = analysis['detection_result']
        
        # Handle existing attributes
        if existing_attribute:
            return self._handle_existing_attribute(
                filepath, lines, existing_attribute, detection_result
            )
        
        # Handle new attributes
        return self._handle_new_attribute(filepath, lines, analysis)
    
    def _handle_existing_attribute(self, filepath: str, lines: List[Tuple[str, str]], 
                                  existing_attribute: ContentTypeAttribute,
                                  detection_result) -> bool:
        """Handle files with existing content type attributes."""
        logger.debug("Handling existing attribute: %s", existing_attribute.value)
        filename = os.path.basename(filepath)
        
        # Check if value is empty and prompt if needed
        if not existing_attribute.value.strip():
            # Show file header for prompting
            self.ui.show_message(f"File: {filename} — Missing content type")
            
            content_type = self.ui.prompt_content_type(detection_result)
            if not content_type:
                return True
            
            if self.ui.should_exit():
                return False
        else:
            content_type = existing_attribute.value.strip()
        
        # Update the attribute
        lines = self.update_existing_attribute(lines, existing_attribute, content_type)
        
        # Write back to file
        if not self.write_file_safely(filepath, lines):
            return False
        
        # Show success message in minimalist format
        if existing_attribute.attribute_type == 'current' and existing_attribute.value.strip():
            self.ui.show_success(f"File: {filename} — Updated: {content_type}")
        else:
            # Convert from deprecated format
            old_type = existing_attribute.value.strip() if existing_attribute.value.strip() else "deprecated"
            self.ui.show_success(f"File: {filename} — Converted: {old_type} → {content_type}")
        
        return True
    
    def _handle_new_attribute(self, filepath: str, lines: List[Tuple[str, str]], 
                             analysis: dict) -> bool:
        """Handle files without existing content type attributes."""
        detection_result = analysis['detection_result']
        filename = analysis['filename']
        
        # Try filename-based detection first
        filename_type = self.detector.detect_from_filename(filename)
        if filename_type:
            lines = self.add_new_attribute(lines, filename_type)
            
            if not self.write_file_safely(filepath, lines):
                return False
                
            self.ui.show_success(f"File: {filename} — Detected: {filename_type}")
            return True
        
        # Check if quiet mode should auto-assign TBD
        if isinstance(self.ui, QuietModeUI):
            lines = self.add_new_attribute(lines, "TBD")
            
            if not self.write_file_safely(filepath, lines):
                return False
                
            self.ui.show_success(f"File: {filename} — Auto-assigned: TBD")
            return True
        
        # Show file header and prompt user
        self.ui.show_message(f"File: {filename} — Missing content type")
        
        # Prompt user with analysis
        content_type = self.ui.prompt_content_type(detection_result)
        
        if self.ui.should_exit():
            return False
        
        if content_type:
            lines = self.add_new_attribute(lines, content_type)
            
            if not self.write_file_safely(filepath, lines):
                return False
                
            self.ui.show_success(f"File: {filename} — Updated: {content_type}")
        
        return True


def register_subcommand(subparsers):
    """This module doesn't register as a subcommand - it's a helper module."""
    pass