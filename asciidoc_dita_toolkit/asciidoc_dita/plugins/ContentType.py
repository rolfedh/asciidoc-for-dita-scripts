"""
Plugin for the AsciiDoc DITA toolkit: ContentType

This plugin adds a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename.
Refactored for improved separation of concerns, testability, and extensibility.
"""

__description__ = "Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename."

import logging
import sys
from typing import Optional

from ..cli_utils import common_arg_parser
from ..plugin_manager import is_plugin_enabled
from ..workflow_utils import process_adoc_files

from .content_type_detector import ContentTypeDetector, ContentTypeConfig
from .ui_interface import ConsoleUI, BatchUI
from .content_type_processor import ContentTypeProcessor


# Setup logging
logger = logging.getLogger(__name__)


def create_processor(batch_mode: bool = False, 
                    config: Optional[ContentTypeConfig] = None) -> ContentTypeProcessor:
    """
    Create a ContentTypeProcessor with appropriate dependencies.
    
    Args:
        batch_mode: If True, use batch UI mode that doesn't prompt for input
        config: Optional configuration for content type detection
        
    Returns:
        Configured ContentTypeProcessor instance
    """
    # Create detector with configuration
    detector = ContentTypeDetector(config)
    
    # Create appropriate UI interface
    if batch_mode:
        ui = BatchUI()
    else:
        ui = ConsoleUI()
    
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
    """Main function for the ContentType plugin."""
    # Setup logging level based on args if available
    if hasattr(args, 'verbose') and args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif hasattr(args, 'quiet') and args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Create processor instance
    batch_mode = getattr(args, 'batch', False)
    processor = create_processor(batch_mode)
    
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
