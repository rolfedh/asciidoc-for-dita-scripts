#!/usr/bin/env python3
"""Debug script to understand the integration test failure."""

import os
import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleSequencer, ModuleState


def debug_integration_test():
    """Debug the integration test to see which module is failing."""
    # The test must be running from the project root, not test_files
    # os.chdir(project_root / 'test_files')
    os.chdir(project_root)

    sequencer = ModuleSequencer()

    # Import the test modules
    from asciidoc_dita_toolkit.modules.entity_reference import EntityReferenceModule
    from asciidoc_dita_toolkit.modules.content_type import ContentTypeModule
    from asciidoc_dita_toolkit.modules.directory_config import DirectoryConfigModule

    # Manually add real modules (simulating entry point discovery)
    sequencer.available_modules = {
        "EntityReference": EntityReferenceModule(),
        "ContentType": ContentTypeModule(),
        "DirectoryConfig": DirectoryConfigModule(),
    }

    print(f"Working directory: {os.getcwd()}")
    print(f"Available modules: {list(sequencer.available_modules.keys())}")

    # Load configurations
    sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')

    resolutions, errors = sequencer.sequence_modules()
    print(f"Errors during sequencing: {errors}")
    print(f"Number of resolutions: {len(resolutions)}")

    # Execute modules in order
    results = []
    for i, resolution in enumerate(resolutions):
        print(f"\nResolution {i}: {resolution.name}, state: {resolution.state}")
        if resolution.state == ModuleState.ENABLED:
            module = sequencer.available_modules[resolution.name]
            print(f"Executing module: {resolution.name}")

            # Initialize module
            try:
                module.initialize(resolution.config)
                print(f"  ✓ Module {resolution.name} initialized successfully")
            except Exception as e:
                print(f"  ✗ Module {resolution.name} initialization failed: {e}")
                continue

            # Execute module
            try:
                result = module.execute({})
                results.append(result)
                print(f"  ✓ Module {resolution.name} executed, result: {result}")
            except Exception as e:
                print(f"  ✗ Module {resolution.name} execution failed: {e}")
                results.append({"success": False, "error": str(e)})

            # Cleanup
            try:
                module.cleanup()
                print(f"  ✓ Module {resolution.name} cleaned up successfully")
            except Exception as e:
                print(f"  ✗ Module {resolution.name} cleanup failed: {e}")

    print(f"\nTotal results: {len(results)}")
    for i, result in enumerate(results):
        print(f"Result {i}: {result}")

    # Check which ones failed
    failed_results = [r for r in results if not r.get("success", False)]
    if failed_results:
        print(f"\nFailed results: {failed_results}")
    else:
        print("\nAll modules executed successfully!")


if __name__ == '__main__':
    debug_integration_test()
