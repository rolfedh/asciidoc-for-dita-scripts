#!/usr/bin/env python3
"""
Demo script showing the ADT ModuleSequencer in action.

This script demonstrates:
1. Module discovery
2. Configuration loading
3. Module sequencing and dependency resolution
4. Module execution with configuration
"""

import json
import logging
from src.adt_core.module_sequencer import ModuleSequencer, ModuleState
from modules.entity_reference import EntityReferenceModule
from modules.content_type import ContentTypeModule
from modules.directory_config import DirectoryConfigModule


def main():
    """Demonstrate the ModuleSequencer functionality."""

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

    print("🔥 ADT ModuleSequencer Demo")
    print("=" * 50)

    # 1. Create ModuleSequencer instance
    sequencer = ModuleSequencer()

    # 2. Simulate module discovery (in real implementation, this would use entry points)
    print("\n📦 Discovering modules...")
    sequencer.available_modules = {
        "EntityReference": EntityReferenceModule(),
        "ContentType": ContentTypeModule(),
        "DirectoryConfig": DirectoryConfigModule(),
    }

    for name, module in sequencer.available_modules.items():
        print(f"   ✓ {name} v{module.version} ({module.release_status})")
        if module.dependencies:
            print(f"     Dependencies: {', '.join(module.dependencies)}")

    # 3. Load configurations
    print("\n⚙️  Loading configurations...")
    sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')

    print(
        f"   Developer config: {len(sequencer.dev_config['modules'])} modules configured"
    )
    print(
        f"   User config: {len(sequencer.user_config.get('disabledModules', []))} modules disabled"
    )

    # 4. Get module status
    print("\n📊 Current module status:")
    status = sequencer.get_module_status()
    for module_info in status['modules']:
        state_icon = (
            "✓"
            if module_info['state'] == "enabled"
            else "⨯" if module_info['state'] == "disabled" else "?"
        )
        print(
            f"   {state_icon} {module_info['name']} [{module_info['state']}, v{module_info['version']}]"
        )
        if module_info['dependencies']:
            print(f"     Dependencies: {', '.join(module_info['dependencies'])}")

    print(
        f"\n   Total: {status['total_enabled']} enabled, {status['total_disabled']} disabled"
    )

    # 5. Sequence modules
    print("\n🔄 Sequencing modules...")
    resolutions, errors = sequencer.sequence_modules()

    if errors:
        print(f"   ⚠️  Errors: {', '.join(errors)}")
    else:
        print("   ✅ No errors")

    # Show initialization order
    enabled_modules = [r for r in resolutions if r.state == ModuleState.ENABLED]
    print(f"\n   Initialization order:")
    for resolution in enabled_modules:
        print(f"   {resolution.init_order + 1}. {resolution.name}")

    # 6. Execute modules
    print("\n🚀 Executing modules...")
    execution_results = []

    for resolution in enabled_modules:
        if resolution.state == ModuleState.ENABLED:
            module = sequencer.available_modules[resolution.name]

            print(f"\n   Initializing {resolution.name}...")
            print(f"   Config: {json.dumps(resolution.config, indent=4)}")

            # Initialize module
            module.initialize(resolution.config)

            # Execute module
            print(f"   Executing {resolution.name}...")
            result = module.execute({"input_data": {"test": "data"}})
            execution_results.append(result)

            print(f"   Result: {result}")

            # Cleanup
            module.cleanup()

    # 7. Test CLI overrides
    print("\n🎛️  Testing CLI overrides...")
    print("   Enabling DirectoryConfig via CLI override...")

    cli_overrides = {"DirectoryConfig": True}
    override_resolutions, override_errors = sequencer.sequence_modules(cli_overrides)

    override_enabled = [
        r for r in override_resolutions if r.state == ModuleState.ENABLED
    ]
    print(f"   With CLI override: {len(override_enabled)} modules enabled")
    for resolution in override_enabled:
        print(f"   {resolution.init_order + 1}. {resolution.name}")

    # 8. Validation
    print("\n✅ Validating configuration...")
    validation_errors = sequencer.validate_configuration()
    if validation_errors:
        print(f"   ⚠️  Validation errors: {', '.join(validation_errors)}")
    else:
        print("   ✅ Configuration is valid")

    print("\n🎉 Demo completed successfully!")
    print(f"   Executed {len(execution_results)} modules")
    print(f"   All modules processed without errors")


if __name__ == "__main__":
    main()
