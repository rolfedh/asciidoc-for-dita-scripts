"""
Plugin for the AsciiDoc DITA toolkit: ContentType

This plugin adds a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename.
Refactored for improved separation of concerns, testability, and extensibility.
"""

__description__ = "Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."

import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..cli_utils import common_arg_parser
from ..plugin_manager import is_plugin_enabled
from ..workflow_utils import process_adoc_files

from .content_type_detector import ContentTypeDetector, ContentTypeConfig
from .ui_interface import MinimalistConsoleUI, QuietModeUI, ConsoleUI, BatchUI
from .content_type_processor import ContentTypeProcessor

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


class ContentTypeModule(ADTModule):
    """
    ADTModule implementation for ContentType plugin.
    
    This module adds content type labels to .adoc files based on filename patterns
    and content analysis, with support for multiple UI modes and user interaction.
    """
    
    @property
    def name(self) -> str:
        """Module name identifier."""
        return "ContentType"
    
    @property
    def version(self) -> str:
        """Module version using semantic versioning."""
        return "2.1.0"
    
    @property
    def dependencies(self) -> List[str]:
        """List of required module names."""
        return ["EntityReference"]  # Depends on EntityReference
    
    @property
    def release_status(self) -> str:
        """Release status: 'GA' for stable, 'preview' for beta."""
        return "GA"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the module with configuration.
        
        Args:
            config: Configuration dictionary containing module settings
        """
        # UI mode configuration
        self.batch_mode = config.get("batch_mode", False)
        self.quiet_mode = config.get("quiet_mode", False)
        self.legacy_mode = config.get("legacy_mode", False)
        self.verbose = config.get("verbose", False)
        
        # Content type detection configuration
        detector_config = config.get("detector_config")
        if detector_config and isinstance(detector_config, dict):
            # Convert dict to ContentTypeConfig if needed
            self.detector_config = ContentTypeConfig(
                filename_prefixes=detector_config.get("filename_prefixes", ContentTypeConfig.get_default().filename_prefixes),
                title_patterns=detector_config.get("title_patterns", ContentTypeConfig.get_default().title_patterns),
                content_patterns=detector_config.get("content_patterns", ContentTypeConfig.get_default().content_patterns)
            )
        else:
            self.detector_config = detector_config or ContentTypeConfig.get_default()
        
        # Initialize statistics
        self.files_processed = 0
        self.content_types_assigned = 0
        self.content_types_updated = 0
        self.warnings_generated = 0
        
        # Initialize detector and processor
        self.detector = ContentTypeDetector(self.detector_config)
        self.ui = self._create_ui_interface()
        self.processor = ContentTypeProcessor(self.detector, self.ui)
        
        if self.verbose:
            print(f"Initialized ContentType v{self.version}")
            print(f"  Batch mode: {self.batch_mode}")
            print(f"  Quiet mode: {self.quiet_mode}")
            print(f"  Legacy mode: {self.legacy_mode}")
            print(f"  Detector config: {type(self.detector_config).__name__}")
    
    def _create_ui_interface(self):
        """Create appropriate UI interface based on configuration."""
        if self.batch_mode:
            return BatchUI()
        elif self.quiet_mode:
            return QuietModeUI()
        elif self.legacy_mode:
            return ConsoleUI()
        else:
            return MinimalistConsoleUI()
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the content type processing.
        
        Args:
            context: Execution context containing parameters and results from dependencies
        
        Returns:
            Dictionary with execution results
        """
        try:
            # Extract parameters from context
            file_path = context.get("file")
            recursive = context.get("recursive", False)
            directory = context.get("directory", ".")
            
            # Create args object for compatibility with legacy code
            class Args:
                def __init__(self, file=None, recursive=False, directory="."):
                    self.file = file
                    self.recursive = recursive
                    self.directory = directory
            
            args = Args(file_path, recursive, directory)
            
            # Reset statistics
            self.files_processed = 0
            self.content_types_assigned = 0
            self.content_types_updated = 0
            self.warnings_generated = 0
            
            # Process files using the existing logic
            process_adoc_files(args, self._process_file_wrapper)
            
            return {
                "module_name": self.name,
                "version": self.version,
                "files_processed": self.files_processed,
                "content_types_assigned": self.content_types_assigned,
                "content_types_updated": self.content_types_updated,
                "warnings_generated": self.warnings_generated,
                "success": True,
                "ui_mode": self._get_ui_mode_name(),
                "detector_config": {
                    "filename_prefixes": len(self.detector_config.filename_prefixes),
                    "title_patterns": len(self.detector_config.title_patterns),
                    "content_patterns": len(self.detector_config.content_patterns)
                }
            }
            
        except Exception as e:
            error_msg = f"Error in ContentType module: {e}"
            if self.verbose:
                print(error_msg)
            return {
                "module_name": self.name,
                "version": self.version,
                "error": str(e),
                "success": False,
                "files_processed": self.files_processed,
                "content_types_assigned": self.content_types_assigned,
                "content_types_updated": self.content_types_updated
            }
    
    def _get_ui_mode_name(self) -> str:
        """Get the name of the current UI mode."""
        if self.batch_mode:
            return "batch"
        elif self.quiet_mode:
            return "quiet"
        elif self.legacy_mode:
            return "legacy"
        else:
            return "minimalist"
    
    def _process_file_wrapper(self, filepath: str) -> bool:
        """
        Wrapper around the process_content_type_file function to track statistics.
        
        Args:
            filepath: Path to the file to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        if self.verbose:
            print(f"Processing file: {filepath}")
        
        original_assigned = self.content_types_assigned
        original_updated = self.content_types_updated
        original_warnings = self.warnings_generated
        
        try:
            # Process the file
            success = self.processor.process_file(filepath)
            
            # Update statistics
            self.files_processed += 1
            
            # Check if UI requested exit
            if self.ui.should_exit():
                logger.info("User requested to exit")
                if self.verbose:
                    print("Exiting at user request.")
                return False
            
            # Track content type changes (simplified tracking)
            # In a real implementation, you might want to track this more precisely
            # by analyzing the file before and after processing
            if success:
                self.content_types_assigned += 1
            
            if self.verbose:
                assigned_in_file = self.content_types_assigned - original_assigned
                updated_in_file = self.content_types_updated - original_updated
                warnings_in_file = self.warnings_generated - original_warnings
                print(f"  Content types assigned: {assigned_in_file}")
                print(f"  Content types updated: {updated_in_file}")
                print(f"  Warnings generated: {warnings_in_file}")
            
            return success
            
        except KeyboardInterrupt:
            logger.info("Process interrupted by user")
            if self.verbose:
                print("\nProcess interrupted by user.")
            return False
        except Exception as e:
            logger.error("Unexpected error processing file %s: %s", filepath, e)
            self.warnings_generated += 1
            if hasattr(self.ui, 'show_error'):
                self.ui.show_error(f"Unexpected error: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up module resources."""
        if self.verbose:
            print(f"ContentType cleanup complete")
            print(f"  Total files processed: {self.files_processed}")
            print(f"  Total content types assigned: {self.content_types_assigned}")
            print(f"  Total content types updated: {self.content_types_updated}")
            print(f"  Total warnings generated: {self.warnings_generated}")
            print(f"  UI mode: {self._get_ui_mode_name()}")


def prompt_for_mode() -> str:
    """
    Prompt user for operating mode at startup.
    
    Returns:
        Selected mode: 'quiet', 'minimalist', or 'legacy'
    """
    print("ContentType Plugin - Press Ctrl+Q for quiet mode (auto-assigns TBD), or any other key to continue")
    
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
        
        # Handle Ctrl+Q (quiet mode)
        if choice == '\x11':  # Ctrl+Q
            print("Quiet mode selected - auto-assigning TBD to unknown content types")
            return 'quiet'
        else:
            return 'minimalist'
            
    except ImportError:
        # Fallback for systems without termios/tty
        choice = input("Press Q for quiet mode, or Enter to continue: ").strip().lower()
        if choice == 'q':
            return 'quiet'
        else:
            return 'minimalist'
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
        sys.exit(0)


def create_processor(batch_mode: bool = False, 
                    quiet_mode: bool = False,
                    legacy_mode: bool = False,
                    config: Optional[ContentTypeConfig] = None) -> ContentTypeProcessor:
    """
    Create a ContentTypeProcessor with appropriate dependencies.
    
    Args:
        batch_mode: If True, use batch UI mode that doesn't prompt for input
        quiet_mode: If True, use quiet mode that auto-assigns TBD
        legacy_mode: If True, use legacy UI with emojis and decorative elements
        config: Optional configuration for content type detection
        
    Returns:
        Configured ContentTypeProcessor instance
    """
    # Create detector with configuration
    detector = ContentTypeDetector(config)
    
    # Create appropriate UI interface
    if batch_mode:
        ui = BatchUI()
    elif quiet_mode:
        ui = QuietModeUI()
    elif legacy_mode:
        ui = ConsoleUI()
    else:
        ui = MinimalistConsoleUI()
    
    # Create processor with dependencies
    processor = ContentTypeProcessor(detector, ui)
    
    return processor


def process_content_type_file(filepath: str, processor: Optional[ContentTypeProcessor] = None):
    """
    Process a single file for content type attributes.
    
    Args:
        filepath: Path to the file to process
        processor: Optional processor instance (for testing)
    """
    if processor is None:
        processor = create_processor()
    
    try:
        success = processor.process_file(filepath)
        if processor.ui.should_exit():
            logger.info("User requested to exit")
            print("Exiting at user request.")
            sys.exit(0)
        
        return success
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error processing file %s: %s", filepath, e)
        processor.ui.show_error(f"Unexpected error: {e}")
        return False


def main(args):
    """Legacy main function for backward compatibility."""
    if ADT_MODULE_AVAILABLE:
        # Use the new ADTModule implementation
        module = ContentTypeModule()
        
        # Initialize with configuration from args
        config = {
            "batch_mode": getattr(args, "batch", False),
            "quiet_mode": getattr(args, "quiet_mode", False),
            "legacy_mode": getattr(args, "legacy", False),
            "verbose": getattr(args, "verbose", False),
            "detector_config": None  # Use default configuration
        }
        
        # Handle interactive mode selection if needed
        if not config["batch_mode"] and not config["legacy_mode"] and not config["quiet_mode"]:
            mode = prompt_for_mode()
            if mode == 'quiet':
                config["quiet_mode"] = True
            elif mode == 'legacy':
                config["legacy_mode"] = True
            # else: use minimalist mode (default)
        
        module.initialize(config)
        
        # Execute with context
        context = {
            "file": getattr(args, "file", None),
            "recursive": getattr(args, "recursive", False),
            "directory": getattr(args, "directory", "."),
            "verbose": getattr(args, "verbose", False)
        }
        
        result = module.execute(context)
        
        # Cleanup
        module.cleanup()
        
        return result
    else:
        # Fallback to legacy implementation
        # Setup logging level based on args if available
        if hasattr(args, 'verbose') and args.verbose:
            logging.basicConfig(level=logging.DEBUG)
        elif hasattr(args, 'quiet') and args.quiet:
            logging.basicConfig(level=logging.ERROR)
        else:
            logging.basicConfig(level=logging.INFO)
        
        # Determine operating mode
        batch_mode = getattr(args, 'batch', False)
        legacy_mode = getattr(args, 'legacy', False)
        quiet_mode = getattr(args, 'quiet_mode', False)
        
        # If no specific mode is set and not in batch mode, prompt for mode
        if not batch_mode and not legacy_mode and not quiet_mode:
            mode = prompt_for_mode()
            if mode == 'quiet':
                quiet_mode = True
            elif mode == 'legacy':
                legacy_mode = True
            # else: use minimalist mode (default)
        
        # Create processor instance
        processor = create_processor(batch_mode, quiet_mode, legacy_mode)
        
        # Process files using the workflow utility
        def process_file_wrapper(filepath):
            return process_content_type_file(filepath, processor)
        
        process_adoc_files(args, process_file_wrapper)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    if not is_plugin_enabled("ContentType"):
        return  # Plugin is disabled, don't register
    
    parser = subparsers.add_parser("ContentType", help=__description__)
    common_arg_parser(parser)
    
    # Add additional options for the refactored plugin
    parser.add_argument(
        "--batch", 
        action="store_true",
        help="Run in batch mode without prompting for input"
    )
    parser.add_argument(
        "--legacy", 
        action="store_true",
        help="Use legacy UI with emojis and decorative elements"
    )
    parser.add_argument(
        "--quiet-mode", 
        action="store_true",
        help="Auto-assign TBD to unknown content types without prompting"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--quiet", 
        action="store_true",
        help="Suppress non-error output"
    )
    
    parser.set_defaults(func=main)
