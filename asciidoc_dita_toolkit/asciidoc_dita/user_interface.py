"""
user_interface.py - Interactive user prompt utilities.

This module provides utilities for user interaction and prompting.
"""

import logging
import os

# Configure logging
logger = logging.getLogger(__name__)

# Default timestamp for missing lastUpdated fields
DEFAULT_TIMESTAMP = "1970-01-01T00:00:00Z"

# Environment variable for non-interactive config selection
ADT_CONFIG_CHOICE_ENV = "ADT_CONFIG_CHOICE"


def prompt_user_to_choose_config(local_config, home_config):
    """
    Prompt user to choose between local and home configuration files.
    Supports non-interactive mode via environment variable.
    
    Args:
        local_config: Configuration data from local .adtconfig.json
        home_config: Configuration data from ~/.adtconfig.json
    
    Returns:
        Selected configuration data
    """
    # Non-interactive mode for CI/automation
    env_choice = os.environ.get(ADT_CONFIG_CHOICE_ENV)
    if env_choice:
        if env_choice == "1" or env_choice.lower() == "local":
            logger.info("Using local configuration (set via ADT_CONFIG_CHOICE)")
            return local_config
        elif env_choice == "2" or env_choice.lower() == "home":
            logger.info("Using home configuration (set via ADT_CONFIG_CHOICE)")
            return home_config
        else:
            logger.warning(f"Invalid ADT_CONFIG_CHOICE value: {env_choice}, falling back to interactive mode")
    
    # Interactive mode
    print("Multiple configuration files found:")
    print(f"[1] Local:  ./.adtconfig.json (last updated: {local_config.get('lastUpdated', 'unknown')})")
    print(f"[2] Home:   ~/.adtconfig.json (last updated: {home_config.get('lastUpdated', 'unknown')})")
    
    # Preselect most recent
    local_time = local_config.get('lastUpdated', DEFAULT_TIMESTAMP)
    home_time = home_config.get('lastUpdated', DEFAULT_TIMESTAMP)
    default_choice = "1" if local_time >= home_time else "2"
    
    while True:
        choice = input(f"Select configuration to use [{default_choice}]: ").strip()
        if not choice:
            choice = default_choice
        
        if choice == "1":
            return local_config
        elif choice == "2":
            return home_config
        else:
            print("Please enter 1 or 2")
