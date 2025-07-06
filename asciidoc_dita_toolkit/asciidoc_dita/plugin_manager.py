"""
plugin_manager.py - Plugin system management utilities.

This module handles plugin discovery, configuration, and management.
Provides a centralized system for checking plugin availability and enablement.

Usage Examples:
    # Check if a plugin is enabled
    from .plugin_manager import is_plugin_enabled
    
    if is_plugin_enabled("DirectoryConfig"):
        # Use DirectoryConfig features
        pass
    
    # Enable DirectoryConfig plugin via environment variable
    # export ADT_ENABLE_DIRECTORY_CONFIG=true
    # or in Python:
    # os.environ["ADT_ENABLE_DIRECTORY_CONFIG"] = "true"
"""

import os

# Plugin configuration constants
PREVIEW_PLUGINS = {"DirectoryConfig", "ContentType"}
ENV_VAR_PREFIX = "ADT_ENABLE_"


def is_plugin_enabled(plugin_name: str) -> bool:
    """
    Check if a plugin is enabled. Some plugins are enabled by default.
    This is a placeholder for future plugin configurator implementation.
    
    The plugin enablement system uses environment variables to control which
    plugins are active. This allows users to selectively enable experimental
    or preview-stage plugins.
    
    Args:
        plugin_name: Name of the plugin to check (e.g., "DirectoryConfig", "ContentType")
    
    Returns:
        True if plugin is enabled, False otherwise
        
    Environment Variables:
        ADT_ENABLE_DIRECTORY_CONFIG: Set to "true" to enable DirectoryConfig plugin
        ADT_ENABLE_CONTENT_TYPE: Set to "true" to enable ContentType plugin
        
    Examples:
        >>> is_plugin_enabled("EntityReference")  # Built-in plugin
        True
        >>> is_plugin_enabled("DirectoryConfig")  # Preview plugin, disabled by default
        False
        >>> os.environ["ADT_ENABLE_DIRECTORY_CONFIG"] = "true"
        >>> is_plugin_enabled("DirectoryConfig")
        True
    """
    if not plugin_name or not isinstance(plugin_name, str):
        return False
    
    # Preview plugins require explicit enablement via environment variables
    if plugin_name in PREVIEW_PLUGINS:
        env_var = f"{ENV_VAR_PREFIX}{plugin_name.upper()}"
        return os.environ.get(env_var, "false").lower() == "true"
    
    # All other plugins are enabled by default
    return True
