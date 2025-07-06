"""
user_interface.py - Interactive user prompt utilities.

This module provides utilities for user interaction and prompting.
Contains constants and utilities for interactive CLI experiences.

Usage Examples:
    # Import constants for default values
    from .user_interface import DEFAULT_TIMESTAMP, ADT_CONFIG_CHOICE_ENV
    
    # Use default timestamp for missing fields
    timestamp = config.get('lastUpdated', DEFAULT_TIMESTAMP)
    
    # Check for non-interactive configuration choice
    choice = os.environ.get(ADT_CONFIG_CHOICE_ENV)
    if choice:
        # Use automated choice instead of prompting user
        use_automated_choice(choice)
"""

# No imports needed - this module only defines constants

# Default timestamp for missing lastUpdated fields
DEFAULT_TIMESTAMP: str = "1970-01-01T00:00:00Z"

# Environment variable for non-interactive config selection
ADT_CONFIG_CHOICE_ENV: str = "ADT_CONFIG_CHOICE"
