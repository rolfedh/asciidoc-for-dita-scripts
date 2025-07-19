#!/usr/bin/env python3
"""
Common test utilities and fixtures for the asciidoc-dita-toolkit test suite.

This module provides shared functionality to eliminate code duplication across test files.
"""

import sys
from pathlib import Path


def get_workspace_root() -> Path:
    """
    Get the workspace root directory path.
    
    Returns:
        Path: The workspace root directory (project root)
    """
    return Path(__file__).parent.parent


def setup_test_paths() -> tuple[Path, Path]:
    """
    Set up common test paths and add them to sys.path.
    
    This function calculates the workspace root and source paths,
    then adds them to sys.path for imports.
    
    Returns:
        tuple[Path, Path]: A tuple of (workspace_root, src_path)
    """
    workspace_root = get_workspace_root()
    src_path = workspace_root / "src"
    
    # Add paths to sys.path if not already present
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    if str(workspace_root) not in sys.path:
        sys.path.insert(0, str(workspace_root))
    
    return workspace_root, src_path
