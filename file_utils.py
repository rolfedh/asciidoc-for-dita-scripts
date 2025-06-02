"""
file_utils.py - Shared utilities for AsciiDoc file processing scripts.

Provides reusable functions for file discovery, symlink handling, and file reading/writing with line ending preservation.
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
    Returns a list of (text, ending) tuples.
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
    """
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        for text, ending in lines:
            f.write(text + ending)

def common_arg_parser(description):
    import argparse
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-r', '--recursive', action='store_true', help='Search subdirectories recursively')
    parser.add_argument('-f', '--file', type=str, help='Scan only the specified .adoc file')
    return parser

def process_adoc_files(args, process_file_func):
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
    import os
    return os.path.isfile(filepath) and filepath.endswith('.adoc') and not os.path.islink(filepath)
