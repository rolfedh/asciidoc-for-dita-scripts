"""
Main entry point for adt_core package.

This module provides command-line interface compatibility with the old asciidoc-dita-toolkit.
"""

import sys
from .cli import main

if __name__ == "__main__":
    main()