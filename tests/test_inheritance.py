#!/usr/bin/env python3
"""Test script to verify ADTModule inheritance is fixed."""

import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

print("Testing ADTModule inheritance fixes...")
print("=" * 50)

try:
    # Import real ADTModule
    from asciidoc_dita_toolkit.adt_core.module_sequencer import ADTModule as RealADTModule
    print(f"✓ Successfully imported real ADTModule: {RealADTModule}")
    print(f"  Location: {RealADTModule.__module__}")
    
    # Test DirectoryConfig
    print("\nTesting DirectoryConfig...")
    from asciidoc_dita_toolkit.modules.directory_config import DirectoryConfigModule
    dm = DirectoryConfigModule()
    is_real = isinstance(dm, RealADTModule)
    print(f"  DirectoryConfigModule is instance of ADTModule: {is_real}")
    
    if is_real:
        print(f"  ✓ DirectoryConfig inheritance FIXED!")
    else:
        print(f"  ✗ DirectoryConfig inheritance FAILED")
        print(f"    MRO: {[c.__name__ for c in DirectoryConfigModule.__mro__]}")
    
    # Test ContentType
    print("\nTesting ContentType...")
    from asciidoc_dita_toolkit.modules.content_type import ContentTypeModule
    cm = ContentTypeModule()
    is_real = isinstance(cm, RealADTModule)
    print(f"  ContentTypeModule is instance of ADTModule: {is_real}")
    
    if is_real:
        print(f"  ✓ ContentType inheritance FIXED!")
    else:
        print(f"  ✗ ContentType inheritance FAILED")

    # Test EntityReference  
    print("\nTesting EntityReference...")
    from asciidoc_dita_toolkit.modules.entity_reference import EntityReferenceModule
    em = EntityReferenceModule()
    is_real = isinstance(em, RealADTModule)
    print(f"  EntityReferenceModule is instance of ADTModule: {is_real}")
    
    if is_real:
        print(f"  ✓ EntityReference inheritance FIXED!")
    else:
        print(f"  ✗ EntityReference inheritance FAILED")

    print("\n" + "=" * 50)
    print("🎉 ADTModule inheritance tests completed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    traceback.print_exc()
