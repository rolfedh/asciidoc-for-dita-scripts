"""
workflow_utils.py - High-level processing workflows.

This module provides high-level workflow orchestration functions that coordinate
different aspects of the AsciiDoc processing pipeline.
"""

import logging

from .plugin_manager import is_plugin_enabled

# Configure logging
logger = logging.getLogger(__name__)


def process_adoc_files(args, process_file_func):
    """
    Batch processing pattern for .adoc files with optional directory configuration:
    - If --file is given and valid, process only that file.
    - Otherwise, find all .adoc files using directory configuration if available,
      or fall back to legacy behavior (recursively if requested) in the specified directory.

    Args:
        args: Parsed command line arguments (must have 'file', 'directory', 'recursive' attributes)
        process_file_func: Function that takes a file path and processes it
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
                    adoc_files = find_adoc_files(directory_path, getattr(args, "recursive", False))
            else:
                # Legacy behavior: process all files in directory
                adoc_files = find_adoc_files(directory_path, getattr(args, "recursive", False))
        except ImportError:
            # DirectoryConfig plugin not available, fall back to legacy behavior
            logger.debug("DirectoryConfig plugin not available, using legacy file discovery")
            adoc_files = find_adoc_files(directory_path, getattr(args, "recursive", False))
    else:
        # Legacy behavior: process all files in directory
        adoc_files = find_adoc_files(directory_path, getattr(args, "recursive", False))
    
    for filepath in adoc_files:
        process_file_func(filepath)
