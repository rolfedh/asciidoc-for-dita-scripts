"""
plugin_manager.py - Plugin system management utilities.

This module handles plugin discovery, configuration, and management.
"""

import os


def is_plugin_enabled(plugin_name):
    """
    Check if a plugin is enabled. Some plugins are enabled by default.
    This is a placeholder for future plugin configurator implementation.
    
    Args:
        plugin_name: Name of the plugin to check
    
    Returns:
        True if plugin is enabled, False otherwise
    """
    # TODO: Implement actual plugin configuration system
    # For MVP, DirectoryConfig and ContentType are disabled by default (preview stage)
    if plugin_name == "DirectoryConfig":
        return os.environ.get("ADT_ENABLE_DIRECTORY_CONFIG", "false").lower() == "true"
    if plugin_name == "ContentType":
        return os.environ.get("ADT_ENABLE_CONTENT_TYPE", "false").lower() == "true"
    return True
