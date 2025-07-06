"""
config_utils.py - Generic configuration management utilities.

This module provides reusable configuration file management functionality
without being tied to specific configuration schemas.
"""

import json
import logging
import os
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


def load_json_config(config_path):
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
    
    Returns:
        Dictionary with configuration data or None if file doesn't exist/invalid
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


def save_json_config(config_path, config_data, update_timestamp=True):
    """
    Save configuration to a JSON file.
    
    Args:
        config_path: Path to save the configuration file
        config_data: Dictionary with configuration data
        update_timestamp: Whether to update lastUpdated timestamp
    
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        expanded_path = os.path.expanduser(config_path)
        os.makedirs(os.path.dirname(expanded_path), exist_ok=True)
        
        # Update timestamp if requested
        if update_timestamp:
            config_data['lastUpdated'] = datetime.now().isoformat()
        
        with open(expanded_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
        
        return True
    except (IOError, OSError) as e:
        logger.error(f"Could not save configuration to {expanded_path}: {e}")
        return False


def validate_config_structure(config, required_fields, field_types=None):
    """
    Generic configuration validation with type checking.
    
    Args:
        config: Configuration dictionary to validate
        required_fields: List of required field names
        field_types: Optional dict mapping field names to expected types
    
    Returns:
        True if configuration is valid, False otherwise
    """
    if not isinstance(config, dict):
        return False
    
    # Check required fields exist
    if not all(field in config for field in required_fields):
        return False
    
    # Type validation if provided
    if field_types:
        for field, expected_type in field_types.items():
            if field in config and not isinstance(config[field], expected_type):
                return False
    
    return True
