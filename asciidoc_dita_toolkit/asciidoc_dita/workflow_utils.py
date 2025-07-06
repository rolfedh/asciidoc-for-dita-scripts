"""
workflow_utils.py - High-level processing workflows.

This module provides high-level workflow orchestration functions that coordinate
different aspects of the AsciiDoc processing pipeline. It handles batch processing
patterns and integrates with the DirectoryConfig plugin when available.

Usage Examples:
    # Define a file processing function
    def my_process_file(filepath):
        print(f"Processing {filepath}")
        # Perform file operations...
    
    # Use the batch processing workflow
    from .workflow_utils import process_adoc_files
    
    # args should have 'file', 'directory', 'recursive' attributes
    process_adoc_files(args, my_process_file)
    
    # This will:
    # - Process single file if args.file is specified
    # - Use DirectoryConfig filtering if plugin is enabled
    # - Fall back to recursive/non-recursive directory scanning
"""

import logging
from typing import Any, Callable

from .plugin_manager import is_plugin_enabled

# Configure logging
logger = logging.getLogger(__name__)


def process_adoc_files(args: Any, process_file_func: Callable[[str], None]) -> None:
    """
    Batch processing pattern for .adoc files with optional directory configuration.
    
    This function implements a sophisticated file discovery workflow:
    1. If --file is specified, process only that file (with validation)
    2. If DirectoryConfig plugin is enabled, use configuration-based filtering
    3. Otherwise, fall back to traditional recursive/non-recursive directory scanning
    
    The workflow automatically handles plugin availability and gracefully degrades
    when DirectoryConfig is not available or enabled.

    Args:
        args: Parsed command line arguments (must have 'file', 'directory', 'recursive' attributes)
        process_file_func: Function that takes a file path and processes it
        
    Examples:
        >>> class Args:
        ...     def __init__(self):
        ...         self.file = None
        ...         self.directory = "docs"
        ...         self.recursive = True
        ...
        >>> args = Args()
        >>> def processor(filepath):
        ...     print(f"Processing: {filepath}")
        ...
        >>> process_adoc_files(args, processor)
        # Processes all .adoc files in docs/ recursively
    """
    from .file_utils import is_valid_adoc_file, find_adoc_files
    
    if args.file:
        if is_valid_adoc_file(args.file):
            process_file_func(args.file)
        else:
            logger.error(f"{args.file} is not a valid .adoc file or is a symlink.")
        return
    
    # Initialize adoc_files to avoid UnboundLocalError
    adoc_files = []
    
    # Try to load directory configuration if DirectoryConfig plugin is available
    directory_path = getattr(args, "directory", ".")
    recursive = getattr(args, "recursive", False)
    
    # Helper function to avoid code duplication
    def fallback_to_legacy():
        return find_adoc_files(directory_path, recursive)
    
    # Check if DirectoryConfig plugin is enabled
    if is_plugin_enabled("DirectoryConfig"):
        try:
            from .plugins.DirectoryConfig import load_directory_config, get_filtered_adoc_files, apply_directory_filters
            
            config = load_directory_config()
            if config:
                # Use configuration-aware file discovery
                logger.info("Using directory configuration")
                adoc_files = get_filtered_adoc_files(directory_path, config, find_adoc_files)
                if adoc_files:
                    directories = apply_directory_filters(directory_path, config)
                    excluded_count = len(config.get('excludeDirs', []))
                    dir_text = "directory" if len(directories) == 1 else "directories"
                    exclude_text = f", excluding {excluded_count}" if excluded_count > 0 else ""
                    logger.info(f"Processing {len(directories)} {dir_text}{exclude_text}")
                    logger.info(f"Found {len(adoc_files)} .adoc file{'s' if len(adoc_files) != 1 else ''} to process")
                else:
                    logger.warning("No .adoc files found in configured directories")
                    # Fall back to legacy behavior when no files found in config
                    adoc_files = fallback_to_legacy()
            else:
                # Legacy behavior: process all files in directory
                adoc_files = fallback_to_legacy()
        except ImportError:
            # DirectoryConfig plugin not available, fall back to legacy behavior
            logger.debug("DirectoryConfig plugin not available, using legacy file discovery")
            adoc_files = fallback_to_legacy()
    else:
        # Legacy behavior: process all files in directory
        adoc_files = fallback_to_legacy()
    
    for filepath in adoc_files:
        process_file_func(filepath)
