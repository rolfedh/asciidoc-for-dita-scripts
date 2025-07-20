#!/usr/bin/env python3
"""Diagnostic test for ADTModule inheritance in entry points."""

import sys
from importlib.metadata import entry_points

# Add src to path
sys.path.insert(0, 'src')

from asciidoc_dita_toolkit.adt_core.module_sequencer import ADTModule as RealADTModule

print("Diagnostic Test: ADTModule Entry Points")
print("=" * 50)

try:
    # Get entry points
    eps = entry_points()
    adt_eps = eps.select(group='adt.modules') if hasattr(eps, 'select') else eps.get('adt.modules', [])
    
    print(f"Found {len(list(adt_eps))} entry points")
    
    for ep in adt_eps:
        print(f"\nTesting {ep.name}:")
        print(f"  Entry point: {ep.value}")
        
        try:
            # Load the class
            module_class = ep.load()
            print(f"  Class loaded: {module_class}")
            
            # Create instance
            instance = module_class()
            print(f"  Instance created: {type(instance)}")
            
            # Check inheritance
            is_instance = isinstance(instance, RealADTModule)
            print(f"  Is instance of ADTModule: {is_instance}")
            
            if is_instance:
                print(f"  ✓ {ep.name} inheritance OK")
                print(f"    Name: {instance.name}")
                print(f"    Version: {instance.version}")
            else:
                print(f"  ✗ {ep.name} inheritance FAILED")
                print(f"    MRO: {[c.__name__ for c in type(instance).__mro__]}")
                
                # Check if ADTModule is in MRO
                adt_in_mro = any('ADTModule' in c.__name__ for c in type(instance).__mro__)
                print(f"    ADTModule in MRO: {adt_in_mro}")
                
                # Check the actual ADTModule class in MRO
                for c in type(instance).__mro__:
                    if 'ADTModule' in c.__name__:
                        print(f"    ADTModule class: {c}")
                        print(f"    Same as real: {c is RealADTModule}")
                        break
                        
        except Exception as e:
            print(f"  ❌ Error loading {ep.name}: {e}")
            import traceback
            traceback.print_exc()

except Exception as e:
    print(f"❌ Diagnostic failed: {e}")
    import traceback
    traceback.print_exc()
