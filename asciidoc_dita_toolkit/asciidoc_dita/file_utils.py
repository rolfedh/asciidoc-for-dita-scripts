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
import os
import re
import argparse

# Regex to split lines and preserve their original line endings
LINE_SPLITTER = re.compile(rb'(.*?)(\r\n|\r|\n|$)')

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
                if filename.endswith('.adoc'):
                    fullpath = os.path.join(dirpath, filename)
                    if not os.path.islink(fullpath):
                        adoc_files.append(fullpath)
    else:
        for filename in os.listdir(root):
            if filename.endswith('.adoc'):
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
    with open(filepath, 'rb') as f:
        content = f.read()
        
    lines = []
    for match in LINE_SPLITTER.finditer(content):
        text = match.group(1).decode('utf-8')
        ending = match.group(2).decode('utf-8') if match.group(2) else ''
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
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        for text, ending in lines:
            f.write(text + ending)


def common_arg_parser(parser):
    """
    Add standard options to the supplied parser:
    -d / --directory: Root directory to search (default: current directory)
    -r / --recursive: Search subdirectories recursively
    -f / --file: Scan only the specified .adoc file
    
    Args:
        parser: ArgumentParser instance to add arguments to
    """
    sources = parser.add_mutually_exclusive_group()
    sources.add_argument('-d', '--directory', type=str, default='.', 
                        help='Root directory to search (default: current directory)')
    sources.add_argument('-f', '--file', type=str, 
                        help='Scan only the specified .adoc file')
    parser.add_argument('-r', '--recursive', action='store_true', 
                        help='Search subdirectories recursively')

def is_valid_adoc_file(filepath):
    """
    Check if the given path is a regular .adoc file (not a symlink).
    
    Args:
        filepath: Path to check
        
    Returns:
        True if the path is a valid .adoc file, False otherwise
    """
    return os.path.isfile(filepath) and filepath.endswith('.adoc') and not os.path.islink(filepath)


def process_adoc_files(args, process_file_func):
    """
    Batch processing pattern for .adoc files:
    - If --file is given and valid, process only that file.
    - Otherwise, find all .adoc files (recursively if requested) in the specified directory and process each.
    
    Args:
        args: Parsed command line arguments (must have 'file', 'directory', 'recursive' attributes)
        process_file_func: Function that takes a file path and processes it
    """
    if args.file:
        if is_valid_adoc_file(args.file):
            process_file_func(args.file)
        else:
            print(f"Error: {args.file} is not a valid .adoc file or is a symlink.")
    else:
        adoc_files = find_adoc_files(getattr(args, 'directory', '.'), getattr(args, 'recursive', False))
        for filepath in adoc_files:
            process_file_func(filepath)
