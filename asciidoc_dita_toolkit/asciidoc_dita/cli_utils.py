"""
cli_utils.py - CLI argument parsing utilities.

This module provides reusable CLI argument parsing functionality for AsciiDoc processing tools.

Example usage:
    parser = argparse.ArgumentParser()
    common_arg_parser(parser)
    args = parser.parse_args()
"""

import argparse


def common_arg_parser(parser: argparse.ArgumentParser) -> None:
    """
    Add standard options to the supplied parser:
    -d / --directory: Root directory to search (default: current directory)
    -r / --recursive: Search subdirectories recursively
    -f / --file: Scan only the specified .adoc file

    Args:
        parser: ArgumentParser instance to add arguments to
    """
    sources = parser.add_mutually_exclusive_group()
    sources.add_argument(
        "-d",
        "--directory",
        type=str,
        default=".",
        help="Root directory to search (default: current directory)",
    )
    sources.add_argument("-f", "--file", type=str, help="Scan only the specified .adoc file")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Search subdirectories recursively",
    )
