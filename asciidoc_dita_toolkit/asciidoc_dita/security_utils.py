"""
security_utils.py - Path validation and security utilities.

This module provides security-focused path operations to prevent directory traversal
attacks and validate directory paths safely.
"""

import os


def _is_subpath(child_path, parent_path):
    """
    Check if child_path is a subpath of parent_path.
    
    Args:
        child_path: Path that might be a child
        parent_path: Path that might be the parent
    
    Returns:
        True if child_path is under parent_path, False otherwise
    """
    try:
        child_path = os.path.abspath(child_path)
        parent_path = os.path.abspath(parent_path)
        
        # Use os.path.commonpath for safer comparison
        try:
            common = os.path.commonpath([child_path, parent_path])
            return common == parent_path
        except ValueError:
            # Paths are on different drives (Windows) or other issues
            return False
    except (OSError, ValueError):
        return False


def sanitize_directory_path(directory_path, base_path=None):
    """
    Sanitize directory path to prevent directory traversal attacks using robust realpath-based validation.
    
    Args:
        directory_path: Directory path to sanitize
        base_path: Optional base directory to constrain paths within (defaults to current working directory)
    
    Returns:
        Sanitized absolute path or None if path is dangerous
    """
    if not directory_path:
        return None
    
    sanitized = directory_path.strip()
    
    # Check for null bytes or other control characters
    if '\x00' in sanitized or any(ord(c) < 32 for c in sanitized if c not in '\t\n\r'):
        return None
    
    # Set default base path to current working directory if not provided
    if base_path is None:
        base_path = os.getcwd()
    
    try:
        # Resolve the base path to its canonical form
        base_real = os.path.realpath(base_path)
        
        # Convert relative paths to absolute by joining with base_path
        if not os.path.isabs(sanitized):
            candidate_path = os.path.join(base_path, sanitized)
        else:
            candidate_path = sanitized
        
        # Resolve to canonical path (follows symlinks and normalizes)
        resolved_path = os.path.realpath(candidate_path)
        
        # Verify the resolved path is within the base directory
        if not _is_subpath(resolved_path, base_real) and resolved_path != base_real:
            return None
        
        return resolved_path
        
    except (OSError, ValueError):
        # Path resolution failed - treat as dangerous
        return None


def validate_directory_path(directory_path, base_path=None, require_exists=True):
    """
    Validate that a directory path is safe and optionally exists.
    
    Args:
        directory_path: Directory path to validate
        base_path: Base directory for relative paths (optional, defaults to current working directory)
        require_exists: Whether the directory must exist
    
    Returns:
        Tuple of (is_valid: bool, result: str) where result is either the validated path or error message
    """
    if not directory_path:
        return False, "Directory path cannot be empty"
    
    # Sanitize input using robust realpath-based validation
    validated_path = sanitize_directory_path(directory_path, base_path)
    if validated_path is None:
        return False, f"Invalid directory path (security check failed): {directory_path}"
    
    if require_exists:
        if not os.path.exists(validated_path):
            return False, f"Directory does not exist: {validated_path}"
        
        if not os.path.isdir(validated_path):
            return False, f"Path is not a directory: {validated_path}"
    
    return True, validated_path
