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

# Regex to split lines and preserve their original line endings
line_splitter = re.compile(rb'(.*?)(\r\n|\r|\n|$)')

def find_adoc_files(root, recursive):
    """
    Find all .adoc files in the given directory (optionally recursively), ignoring symlinks.
    Returns a list of file paths.
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
    Reads a file as bytes, splits into lines preserving original line endings, and decodes as UTF-8.
    Returns a list of (text, ending) tuples, where 'text' is the line content and 'ending' is the original line ending.
    """
    with open(filepath, 'rb') as f:
        content = f.read()
    lines = []
    for match in line_splitter.finditer(content):
        text = match.group(1).decode('utf-8')
        ending = match.group(2).decode('utf-8') if match.group(2) else ''
        lines.append((text, ending))
        if not ending:
            break
    return lines

def write_text_preserve_endings(filepath, lines):
    """
    Writes a list of (text, ending) tuples to a file, preserving original line endings.
    Each tuple should be (text, ending), where 'ending' is the original line ending (e.g., '\n', '\r\n', or '').
    """
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        for text, ending in lines:
            f.write(text + ending)

def common_arg_parser(description):
    """
    Returns an argparse.ArgumentParser with standard options for all scripts:
    -r / --recursive: Search subdirectories recursively
    -f / --file: Scan only the specified .adoc file
    """
    import argparse
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-r', '--recursive', action='store_true', help='Search subdirectories recursively')
    parser.add_argument('-f', '--file', type=str, help='Scan only the specified .adoc file')
    return parser

def process_adoc_files(args, process_file_func):
    """
    Batch processing pattern for .adoc files:
    - If --file is given and valid, process only that file.
    - Otherwise, find all .adoc files (recursively if requested) and process each.
    - process_file_func should be a function that takes a file path.
    """
    from .file_utils import find_adoc_files, is_valid_adoc_file
    if args.file:
        if is_valid_adoc_file(args.file):
            process_file_func(args.file)
        else:
            print(f"Error: {args.file} is not a valid .adoc file or is a symlink.")
    else:
        adoc_files = find_adoc_files('.', args.recursive)
        for filepath in adoc_files:
            process_file_func(filepath)

def is_valid_adoc_file(filepath):
    """
    Returns True if the given path is a regular .adoc file (not a symlink), else False.
    """
    import os
    return os.path.isfile(filepath) and filepath.endswith('.adoc') and not os.path.islink(filepath)
