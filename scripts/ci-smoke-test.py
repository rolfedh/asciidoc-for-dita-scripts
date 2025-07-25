#!/usr/bin/env python3
"""
Smoke test for CI environment - validates basic functionality.

This script performs basic sanity checks to ensure the environment
is set up correctly for running tests.
"""

import sys
import os
from pathlib import Path


def main():
    """Run smoke tests."""
    print("🔍 Running CI smoke tests...")

    # Test 1: Basic Python import
    try:
        import asciidoc_dita_toolkit

        print("✅ Package import successful")
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        return False

    # Test 2: Core module accessibility
    try:
        from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleSequencer

        print("✅ Core modules accessible")
    except ImportError as e:
        print(f"❌ Core modules not accessible: {e}")
        return False

    # Test 3: Plugin directory exists
    plugin_dir = Path("asciidoc_dita_toolkit/asciidoc_dita/plugins")
    if plugin_dir.exists():
        plugins = list(plugin_dir.glob("*.py"))
        print(f"✅ Plugin directory found with {len(plugins)} files")
    else:
        print("❌ Plugin directory not found")
        return False

    # Test 4: Test directory exists
    test_dir = Path("tests")
    if test_dir.exists():
        test_files = list(test_dir.glob("test_*.py"))
        print(f"✅ Test directory found with {len(test_files)} test files")
    else:
        print("❌ Test directory not found")
        return False

    # Test 5: Basic UserJourney import (if available)
    try:
        from asciidoc_dita_toolkit.asciidoc_dita.plugins.UserJourney import (
            UserJourneyModule,
        )

        print("✅ UserJourney module import successful")
    except ImportError as e:
        print(f"⚠️  UserJourney module not available: {e}")
        # This is not fatal for CI

    print("🎉 All smoke tests passed!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
