"""
config_utils.py - Generic configuration management utilities.

This module provides reusable configuration file management functionality
without being tied to specific configuration schemas.

Example:
    # Load configuration
    config = load_json_config("~/.myapp.json")
    if config:
        print(f"Loaded config version: {config.get('version')}")
    
    # Save configuration
    data = {"version": "1.0", "settings": {"debug": True}}
    if save_json_config("./config.json", data):
        print("Configuration saved successfully")
    
    # Validate configuration structure
    is_valid, error = validate_config_structure(
        config, 
        required_fields=["version", "settings"],
        field_types={"version": str, "settings": dict}
    )
    if not is_valid:
        print(f"Invalid config: {error}")
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)


def load_json_config(config_path: str) -> Optional[Dict[str, Any]]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
    
    Returns:
        Dictionary with configuration data or None if file doesn't exist/invalid
        
    Example:
        config = load_json_config("~/.myapp.json")
        if config:
            version = config.get("version", "unknown")
            print(f"Config version: {version}")
    """
    expanded_path = os.path.expanduser(config_path)
    if not os.path.exists(expanded_path):
        return None
    
    try:
        with open(expanded_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Could not load configuration from {expanded_path}: {e}")
        return None


def save_json_config(config_path: str, config_data: Dict[str, Any], update_timestamp: bool = True) -> bool:
    """
    Save configuration to a JSON file.
    
    Args:
        config_path: Path to save the configuration file
        config_data: Dictionary with configuration data
        update_timestamp: Whether to update lastUpdated timestamp
    
    Returns:
        True if saved successfully, False otherwise
        
    Example:
        data = {"version": "1.0", "settings": {"debug": True}}
        if save_json_config("./config.json", data):
            print("Configuration saved successfully")
        else:
            print("Failed to save configuration")
    """
    try:
        expanded_path = os.path.expanduser(config_path)
        dir_name = os.path.dirname(expanded_path)
        if dir_name:  # Ensure the directory name is non-empty
            os.makedirs(dir_name, exist_ok=True)
        
        # Update timestamp if requested
        if update_timestamp:
            config_data['lastUpdated'] = datetime.now().isoformat()
        
        with open(expanded_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
        
        return True
    except (IOError, OSError) as e:
        logger.error(f"Could not save configuration to {expanded_path}: {e}")
        return False


def validate_config_structure(config: Any, required_fields: List[str], field_types: Optional[Dict[str, type]] = None) -> Tuple[bool, str]:
    """
    Generic configuration validation with type checking.
    
    Args:
        config: Configuration dictionary to validate
        required_fields: List of required field names
        field_types: Optional dict mapping field names to expected types
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
        If valid, error_message will be empty string
        
    Example:
        is_valid, error = validate_config_structure(
            config, 
            required_fields=["version", "settings"],
            field_types={"version": str, "settings": dict}
        )
        if not is_valid:
            print(f"Configuration error: {error}")
    """
    if not isinstance(config, dict):
        return False, "Configuration must be a dictionary"
    
    # Check required fields exist
    missing_fields = [field for field in required_fields if field not in config]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    # Type validation if provided
    if field_types:
        for field, expected_type in field_types.items():
            if field in config and not isinstance(config[field], expected_type):
                actual_type = type(config[field]).__name__
                expected_type_name = expected_type.__name__
                return False, f"Field '{field}' must be {expected_type_name}, got {actual_type}"
    
    return True, ""
