"""
file_utils.py - Core file operations for AsciiDoc processing.

This module provides core file operations for:
- Discovering .adoc files in a directory (optionally recursively), always ignoring symlinks.
- Reading and writing text files while preserving original line endings for each line.
- Validating .adoc files (extension, file type, not a symlink).

After modularization (Issue #92), this module focuses solely on file operations.
Other concerns have been moved to specialized modules:
- CLI parsing → cli_utils.py
- Security validation → security_utils.py
- Configuration management → config_utils.py
- Plugin management → plugin_manager.py
- User interaction → user_interface.py
- High-level workflows → workflow_utils.py

Legacy imports are maintained for backward compatibility with deprecation warnings.
"""

import logging
import os
import re

# For backward compatibility - import from new modules
from .cli_utils import common_arg_parser
from .config_utils import load_json_config as load_config_file, save_json_config as save_config_file
from .plugin_manager import is_plugin_enabled
from .security_utils import sanitize_directory_path, validate_directory_path, _is_subpath
from .user_interface import DEFAULT_TIMESTAMP, ADT_CONFIG_CHOICE_ENV
# Note: workflow_utils import moved to avoid circular dependency

# Configure logging
logger = logging.getLogger(__name__)

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

    # Validate root directory using consolidated validation
    is_valid, result = validate_directory_path(root, require_exists=True)
    if not is_valid:
        logger.warning(f"Directory validation failed: {result}")
        return adoc_files

    try:
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
    except PermissionError as e:
        logger.warning(f"Permission denied accessing directory '{root}': {e}")
    except OSError as e:
        logger.warning(f"Could not access directory '{root}': {e}")
    except Exception as e:
        logger.warning(f"Unexpected error processing directory '{root}': {e}")

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


def is_valid_adoc_file(filepath):
    """
    Check if the given path is a regular .adoc file (not a symlink).

    Args:
        filepath: Path to check

    Returns:
        True if the path is a valid .adoc file, False otherwise
    """
    return os.path.isfile(filepath) and filepath.endswith(".adoc") and not os.path.islink(filepath)


# =============================================================================
# BACKWARD COMPATIBILITY LAYER
# =============================================================================
# These functions are deprecated and will be removed in a future version.
# They are maintained for backward compatibility and delegate to new modules.
# 
# Migration Guide:
# - CLI functions → cli_utils.py
# - Security functions → security_utils.py
# - Configuration functions → config_utils.py
# - Plugin functions → plugin_manager.py
# - UI functions → user_interface.py
# - Workflow functions → workflow_utils.py
# =============================================================================
def _validate_config_structure(config):
    """Deprecated: Use config_utils.validate_config_structure instead."""
    import warnings
    warnings.warn("_validate_config_structure is deprecated. Use config_utils.validate_config_structure instead.",
                  DeprecationWarning, stacklevel=2)
    from .config_utils import validate_config_structure
    required_fields = ['version', 'repoRoot', 'includeDirs', 'excludeDirs', 'lastUpdated']
    field_types = {
        'includeDirs': list,
        'excludeDirs': list,
        'repoRoot': str,
        'version': str,
        'lastUpdated': str
    }
    return validate_config_structure(config, required_fields, field_types)


def load_directory_config():
    """Deprecated: Use plugins.DirectoryConfig.load_directory_config instead."""
    import warnings
    warnings.warn("load_directory_config is deprecated. Use plugins.DirectoryConfig.load_directory_config instead.",
                  DeprecationWarning, stacklevel=2)
    try:
        from .plugins.DirectoryConfig import load_directory_config as load_dir_config
        return load_dir_config()
    except ImportError:
        return None


def apply_directory_filters(base_path, config):
    """Deprecated: Use plugins.DirectoryConfig.apply_directory_filters instead."""
    import warnings
    warnings.warn("apply_directory_filters is deprecated. Use plugins.DirectoryConfig.apply_directory_filters instead.",
                  DeprecationWarning, stacklevel=2)
    try:
        from .plugins.DirectoryConfig import apply_directory_filters as apply_filters
        return apply_filters(base_path, config)
    except ImportError:
        return [base_path]


def get_filtered_adoc_files(directory_path, config):
    """Deprecated: Use plugins.DirectoryConfig.get_filtered_adoc_files instead."""
    import warnings
    warnings.warn("get_filtered_adoc_files is deprecated. Use plugins.DirectoryConfig.get_filtered_adoc_files instead.",
                  DeprecationWarning, stacklevel=2)
    try:
        from .plugins.DirectoryConfig import get_filtered_adoc_files as get_filtered_files
        return get_filtered_files(directory_path, config, find_adoc_files)
    except ImportError:
        return find_adoc_files(directory_path, True)


def process_adoc_files(args, process_file_func):
    """Deprecated: Use workflow_utils.process_adoc_files instead."""
    import warnings
    warnings.warn("process_adoc_files is deprecated. Use workflow_utils.process_adoc_files instead.", 
                  DeprecationWarning, stacklevel=2)
    from .workflow_utils import process_adoc_files as process_files
    return process_files(args, process_file_func)
