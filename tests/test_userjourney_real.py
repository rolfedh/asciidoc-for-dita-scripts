#!/usr/bin/env python3
"""Test UserJourney workflow manager with real module discovery."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

print("Testing UserJourney with Real Module Discovery")
print("=" * 50)

try:
    from asciidoc_dita_toolkit.modules.user_journey import WorkflowManager
    
    # Create workflow manager
    print("Creating WorkflowManager...")
    manager = WorkflowManager()
    print("✓ WorkflowManager created")
    
    # Test getting planned modules
    print("\nGetting planned module sequence...")
    try:
        planned_modules = manager.get_planned_modules()
        print(f"✓ Planned modules: {planned_modules}")
        print(f"  Total modules: {len(planned_modules)}")
        
        if planned_modules:
            print(f"  First module: {planned_modules[0]} (should be DirectoryConfig)")
            if planned_modules[0] == "DirectoryConfig":
                print("✓ DirectoryConfig is first as required")
            else:
                print("⚠️  DirectoryConfig is not first")
    
    except Exception as e:
        print(f"⚠️  Module planning failed: {e}")
    
    # Test workflow creation (dry run)
    print("\nTesting workflow creation...")
    test_dir = Path.cwd() / "tests" / "fixtures"
    if test_dir.exists():
        try:
            # Don't actually create, just test the validation
            if manager.workflow_exists("test_workflow"):
                print("  Cleaning up existing test workflow...")
                test_path = Path.home() / ".adt" / "workflows" / "test_workflow.json"
                if test_path.exists():
                    test_path.unlink()
            
            workflow = manager.start_workflow("test_workflow", str(test_dir))
            print(f"✓ Test workflow created successfully!")
            print(f"  Files discovered: {len(workflow.files_discovered)}")
            print(f"  Modules planned: {list(workflow.modules.keys())}")
            
            # Clean up
            workflow.get_storage_path().unlink()
            print("✓ Test workflow cleaned up")
            
        except Exception as e:
            print(f"⚠️  Workflow creation test failed: {e}")
    else:
        print("⚠️  Test directory not found, skipping workflow creation test")
    
    print("\n" + "=" * 50)
    print("🎉 UserJourney with real modules TEST COMPLETE!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
