#!/usr/bin/env python3

import sys
import tempfile
import json
import shutil
from pathlib import Path

# Add the project to the path
sys.path.insert(0, '/home/rolfedh/asciidoc-dita-toolkit')

from asciidoc_dita_toolkit.asciidoc_dita.plugins.UserJourney import WorkflowState, ExecutionResult

def debug_save_detailed():
    """Detailed debugging of save_to_disk method."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_dir = Path(temp_dir)
        WorkflowState._default_storage_dir = storage_dir
        
        print(f"Using storage directory: {storage_dir}")
        
        # Create workflow
        workflow_name = 'test_workflow'
        modules = ['DirectoryConfig', 'ContentType']
        workflow = WorkflowState(workflow_name, '/test/docs', modules)
        
        # First save
        print("\n=== First Save ===")
        workflow.save_to_disk()
        
        main_file = storage_dir / f'{workflow_name}.json'
        backup_file = storage_dir / f'{workflow_name}.json.backup'
        temp_file = storage_dir / f'{workflow_name}.json.tmp'
        
        print(f"After first save:")
        print(f"  Main file exists: {main_file.exists()}")
        print(f"  Backup file exists: {backup_file.exists()}")
        print(f"  Temp file exists: {temp_file.exists()}")
        
        if main_file.exists():
            main_content_1 = main_file.read_text()
            print(f"  Main file size: {len(main_content_1)} chars")
        
        # Create existing backup file
        print("\n=== Creating Existing Backup ===")
        # Use the correct backup path that matches what save_to_disk expects
        backup_file = storage_dir / f'{workflow_name}.backup'  # Changed from .json.backup
        backup_file.write_text('{"old": "backup", "test": true}')
        print(f"Backup file created with {len(backup_file.read_text())} chars")
        
        # Modify workflow
        print("\n=== Modifying Workflow ===")
        workflow.mark_module_completed('DirectoryConfig', ExecutionResult('success', 'Done'))
        
        # Now manually implement the save logic with debugging
        print("\n=== Manual Save with Debugging ===")
        
        storage_path = workflow.get_storage_path()
        temp_path = storage_path.with_suffix('.tmp')
        backup_path = storage_path.with_suffix('.backup')
        
        print(f"Paths:")
        print(f"  storage_path: {storage_path}")
        print(f"  temp_path: {temp_path}")
        print(f"  backup_path: {backup_path}")
        
        print(f"Before save operation:")
        print(f"  storage exists: {storage_path.exists()}")
        print(f"  backup exists: {backup_path.exists()}")
        print(f"  temp exists: {temp_path.exists()}")
        
        if backup_path.exists():
            original_backup = backup_path.read_text()
            print(f"  original backup content: {original_backup}")
        
        try:
            # Create backup of existing state (only if current file exists)
            if storage_path.exists():
                print("  Creating backup from existing storage file...")
                shutil.copy2(storage_path, backup_path)
                print("  Backup created successfully")
                
                if backup_path.exists():
                    new_backup = backup_path.read_text()
                    print(f"  new backup content length: {len(new_backup)}")
                    print(f"  backup changed: {original_backup != new_backup}")
            
            # Write to temp file
            print("  Writing to temp file...")
            with open(temp_path, 'w') as f:
                json.dump(workflow.to_dict(), f, indent=2)
            print("  Temp file written")
            
            # Atomic rename
            print("  Renaming temp to storage...")
            temp_path.rename(storage_path)
            print("  Rename completed")
            
            # Clean up backup on success
            print("  Checking for backup cleanup...")
            if backup_path.exists():
                print("  Backup exists, unlinking...")
                backup_path.unlink()
                print("  Backup unlinked")
            else:
                print("  No backup to clean up")
                
        except Exception as e:
            print(f"Error during save: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\nAfter manual save:")
        print(f"  Main file exists: {storage_path.exists()}")
        print(f"  Backup file exists: {backup_path.exists()}")
        print(f"  Temp file exists: {temp_path.exists()}")
        
        print(f"\nAll files in directory:")
        for file_path in storage_dir.iterdir():
            print(f"  {file_path.name} ({file_path.stat().st_size} bytes)")

if __name__ == "__main__":
    debug_save_detailed()
