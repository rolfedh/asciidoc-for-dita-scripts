"""
Reusable test utilities for AsciiDoc plugin/processing scripts.

Provides functions for fixture discovery and reading.
"""
import os

def get_fixture_path(fixture_name, fixture_dir="fixtures"):
    """
    Get the absolute path to a fixture file.
    """
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), fixture_dir, fixture_name)
    )

def read_fixture(fixture_name, fixture_dir="fixtures"):
    """
    Read the content of a fixture file.
    """
    with open(get_fixture_path(fixture_name, fixture_dir), "r", encoding="utf-8") as f:
        return f.read()
