#!/usr/bin/env python3
"""Test ModuleSequencer discovery after fixing inheritance."""

import sys
import logging
from pathlib import Path

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)

# Add src to path
sys.path.insert(0, 'src')

print("Testing ModuleSequencer discovery...")
print("=" * 50)

try:
    from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleSequencer
    
    # Create sequencer
    sequencer = ModuleSequencer()
    print("✓ ModuleSequencer created")
    
    # Try to load configurations
    try:
        sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')
        print("✓ Configurations loaded")
    except Exception as e:
        print(f"⚠️  Configuration loading failed: {e}")
        print("   (This may be expected if config files don't exist)")
    
    # Test module discovery
    print("\nDiscovering modules...")
    sequencer.discover_modules()
    
    discovered_count = len(sequencer.available_modules)
    print(f"✓ Discovered {discovered_count} modules:")
    
    for name, module in sequencer.available_modules.items():
        print(f"  - {name} (v{module.version})")
    
    if discovered_count > 0:
        print(f"\n🎉 Module discovery SUCCESS! Found {discovered_count} modules")
        
        # Test sequencing
        print("\nTesting module sequencing...")
        resolutions, errors = sequencer.sequence_modules()
        
        if errors:
            print(f"⚠️  Sequencing errors: {errors}")
        
        enabled_modules = [r.name for r in resolutions if r.state.name == "ENABLED"]
        print(f"✓ Enabled modules in sequence: {enabled_modules}")
        
    else:
        print("⚠️  No modules discovered - entry points may not be working")
        print("   This is expected if package is not installed with pip install -e .")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
