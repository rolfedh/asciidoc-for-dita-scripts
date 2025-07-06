"""
security_utils.py - Path validation and security utilities.

This module provides security-focused path operations to prevent directory traversal
attacks and validate directory paths safely. All functions use robust path resolution
and validation to ensure safe file system operations.

Usage Examples:
    # Sanitize a user-provided directory path
    from .security_utils import sanitize_directory_path, validate_directory_path
    
    safe_path = sanitize_directory_path("../../../etc/passwd")  # Returns None (unsafe)
    safe_path = sanitize_directory_path("docs/modules")  # Returns absolute path if safe
    
    # Validate directory with detailed error messages
    is_valid, result = validate_directory_path("/path/to/docs", require_exists=True)
    if is_valid:
        print(f"Using directory: {result}")
    else:
        print(f"Error: {result}")
"""

import os
from typing import Optional, Tuple


def _is_subpath(child_path: str, parent_path: str) -> bool:
    """
    Check if child_path is a subpath of parent_path.
    
    Args:
        child_path: Path that might be a child
        parent_path: Path that might be the parent
    
    Returns:
        True if child_path is under parent_path, False otherwise
        
    Examples:
        >>> _is_subpath("/home/user/docs", "/home/user")
        True
        >>> _is_subpath("/etc/passwd", "/home/user") 
        False
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


def sanitize_directory_path(directory_path: str, base_path: Optional[str] = None) -> Optional[str]:
    """
    Sanitize directory path to prevent directory traversal attacks using robust realpath-based validation.
    
    This function performs comprehensive security validation:
    - Removes dangerous control characters
    - Resolves symlinks and normalizes paths
    - Ensures the path stays within the base directory
    - Prevents directory traversal attacks (../, etc.)
    
    Args:
        directory_path: Directory path to sanitize
        base_path: Optional base directory to constrain paths within (defaults to current working directory)
    
    Returns:
        Sanitized absolute path or None if path is dangerous
        
    Examples:
        >>> sanitize_directory_path("docs")  # Safe relative path
        '/current/working/dir/docs'
        >>> sanitize_directory_path("../../../etc/passwd")  # Dangerous path
        None
        >>> sanitize_directory_path("/safe/absolute/path")
        '/safe/absolute/path'
    """
    if not directory_path:
        return None
    
    sanitized = directory_path.strip()
    
    # Reject whitespace-only paths after stripping
    if not sanitized:
        return None
    
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


def validate_directory_path(directory_path: str, base_path: Optional[str] = None, require_exists: bool = True) -> Tuple[bool, str]:
    """
    Validate that a directory path is safe and optionally exists.
    
    This is an enhanced validation function that combines sanitization with
    existence checks and provides detailed error messages for troubleshooting.
    
    Args:
        directory_path: Directory path to validate
        base_path: Base directory for relative paths (optional, defaults to current working directory)
        require_exists: Whether the directory must exist
    
    Returns:
        Tuple of (is_valid: bool, result: str) where:
        - If valid: result is the validated absolute path
        - If invalid: result is a descriptive error message
        
    Examples:
        >>> validate_directory_path("docs", require_exists=False)
        (True, '/current/working/dir/docs')
        >>> validate_directory_path("../../../etc", require_exists=True)
        (False, 'Invalid directory path (security check failed): ../../../etc')
        >>> validate_directory_path("nonexistent", require_exists=True)
        (False, 'Directory does not exist: /current/working/dir/nonexistent')
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
