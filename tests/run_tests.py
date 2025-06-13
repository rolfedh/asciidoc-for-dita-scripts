"""
Test runner for the AsciiDoc DITA Toolkit

Runs all tests including CLI-based tests.
"""

import os
import sys
import unittest

# Add the package to the path for testing
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "asciidoc_dita_toolkit")
)


def run_all_tests():
    """Discover and run all tests."""
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
