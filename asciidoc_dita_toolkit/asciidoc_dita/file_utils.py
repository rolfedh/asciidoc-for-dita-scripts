"""
file_utils.py - Shared utilities for AsciiDoc file processing scripts.

This module provides reusable functions for:
- Discovering .adoc files in a directory (optionally recursively), always ignoring symlinks.
- Reading and writing text files while preserving original line endings for each line.
- Validating .adoc files (extension, file type, not a symlink).
- Providing a common argument parser for CLI scripts.
- Batch processing of .adoc files using a user-supplied processing function.

Intended for use by all scripts in this repository to avoid code duplication and ensure consistent file handling.
"""

import argparse
import os
import re
import sys

# Regex to split lines and preserve their original line endings
LINE_SPLITTER = re.compile(rb"(.*?)(\r\n|\r|\n|$)")


def find_adoc_files(root, recursive):
    """
    Find all .adoc files in the given directory (optionally recursively), ignoring symlinks.

    Args:
        root: Root directory to search
        recursive: Whether to search recursively

    Returns:
        List of file paths
    """
    adoc_files = []

    if recursive:
        for dirpath, dirnames, filenames in os.walk(root):
            for filename in filenames:
                if filename.endswith(".adoc"):
                    fullpath = os.path.join(dirpath, filename)
                    if not os.path.islink(fullpath):
                        adoc_files.append(fullpath)
    else:
        for filename in os.listdir(root):
            if filename.endswith(".adoc"):
                fullpath = os.path.join(root, filename)
                if not os.path.islink(fullpath):
                    adoc_files.append(fullpath)

    return adoc_files


def read_text_preserve_endings(filepath):
    """
    Read a file as bytes, split into lines preserving original line endings, and decode as UTF-8.

    Args:
        filepath: Path to the file to read

    Returns:
        List of (text, ending) tuples, where 'text' is the line content and 'ending' is the original line ending.
    """
    with open(filepath, "rb") as f:
        content = f.read()

    lines = []
    for match in LINE_SPLITTER.finditer(content):
        text = match.group(1).decode("utf-8")
        ending = match.group(2).decode("utf-8") if match.group(2) else ""
        lines.append((text, ending))
        if not ending:
            break

    return lines


def write_text_preserve_endings(filepath, lines):
    """
    Write a list of (text, ending) tuples to a file, preserving original line endings.

    Args:
        filepath: Path to the file to write
        lines: List of (text, ending) tuples, where 'ending' is the original line ending (e.g., '\n', '\r\n', or '').
    """
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        for text, ending in lines:
            f.write(text + ending)


def common_arg_parser(parser):
    """
    Add standard options to the supplied parser:
    [file_or_dir]: Optional positional argument that auto-detects file vs directory
    -nr / --no-recursive: Disable recursive search, only process current directory
    
    Deprecated (hidden from usage but still functional):
    -d / --directory: Root directory to search (default: current directory)
    -r / --recursive: Search subdirectories recursively (default: enabled)
    -f / --file: Scan only the specified .adoc file

    Args:
        parser: ArgumentParser instance to add arguments to
    """
    # Add optional positional argument for auto-detection
    parser.add_argument(
        "file_or_directory",
        nargs="?",
        metavar="file_or_dir",
        help="File or directory to search. If not specified, uses current directory."
    )
    
    # Add the main option users should use
    parser.add_argument(
        "-nr",
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="Disable recursive search, only process current directory",
    )
    
    # Deprecated options - hidden from main usage but still functional for backward compatibility
    deprecated_group = parser.add_argument_group("deprecated options (hidden)")
    sources = deprecated_group.add_mutually_exclusive_group()
    sources.add_argument(
        "-d",
        "--directory",
        type=str,
        help=argparse.SUPPRESS,  # Hide from help output
    )
    sources.add_argument(
        "-f", 
        "--file", 
        type=str, 
        help=argparse.SUPPRESS,  # Hide from help output
    )
    deprecated_group.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        default=True,
        help=argparse.SUPPRESS,  # Hide from help output
    )


def is_valid_adoc_file(filepath):
    """
    Check if the given path is a regular .adoc file (not a symlink).

    Args:
        filepath: Path to check

    Returns:
        True if the path is a valid .adoc file, False otherwise
    """
    return os.path.isfile(filepath) and filepath.endswith(".adoc") and not os.path.islink(filepath)


def process_adoc_files(args, process_file_func):
    """
    Batch processing pattern for .adoc files with auto-detection support:
    - Automatically detects whether the argument is a file or directory
    - If file mode, processes only that file
    - If directory mode, finds all .adoc files (recursively if requested) and processes each

    Args:
        args: Parsed command line arguments 
        process_file_func: Function that takes a file path and processes it
    """
    try:
        target_path, mode = resolve_target_path(args)
        
        if mode == 'file':
            if is_valid_adoc_file(target_path):
                process_file_func(target_path)
            else:
                print(f"Error: {target_path} is not a valid .adoc file or is a symlink.")
        else:  # directory mode
            adoc_files = find_adoc_files(target_path, getattr(args, "recursive", True))
            for filepath in adoc_files:
                process_file_func(filepath)
                
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

def resolve_target_path(args):
    """
    Resolve the target path from command line arguments, supporting auto-detection.
    
    Priority order:
    1. Explicit -f/--file flag (returns file path, 'file' mode)
    2. Explicit -d/--directory flag (returns directory path, 'directory' mode)  
    3. Positional path argument with auto-detection
    4. Default to current directory
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        tuple: (path, mode) where mode is 'file' or 'directory'
    """
    # Explicit file mode
    if args.file:
        return args.file, 'file'
    
    # Explicit directory mode
    if args.directory:
        return args.directory, 'directory'
    
    # Auto-detection from positional argument
    if args.file_or_directory:
        if os.path.isfile(args.file_or_directory):
            return args.file_or_directory, 'file'
        elif os.path.isdir(args.file_or_directory):
            return args.file_or_directory, 'directory'
        else:
            raise ValueError(f"Path does not exist or is not accessible: {args.file_or_directory}")
    
    # Default to current directory
    return ".", 'directory'
