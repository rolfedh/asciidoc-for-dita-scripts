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
