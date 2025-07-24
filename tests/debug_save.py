#!/usr/bin/env python3

import sys
import tempfile
from pathlib import Path

# Add the project to the path
sys.path.insert(0, '/home/rolfedh/asciidoc-dita-toolkit')

from asciidoc_dita_toolkit.modules.user_journey import WorkflowState, ExecutionResult

def debug_save_behavior():
    """Debug the save_to_disk behavior to understand why backup isn't cleaned up."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_dir = Path(temp_dir)
        WorkflowState._default_storage_dir = storage_dir
        
        print(f"Using storage directory: {storage_dir}")
        
        # Create workflow
        workflow_name = 'test_workflow'
        modules = ['DirectoryConfig', 'ContentType']
        workflow = WorkflowState(workflow_name, '/test/docs', modules)
        
        # First save - should create main file, no backup
        print("\n=== First Save ===")
        workflow.save_to_disk()
        
        main_file = storage_dir / f'{workflow_name}.json'
        backup_file = storage_dir / f'{workflow_name}.json.backup'
        
        print(f"Main file exists: {main_file.exists()}")
        print(f"Backup file exists: {backup_file.exists()}")
        
        # Manually create a backup file (simulating existing backup)
        print("\n=== Creating Existing Backup ===")
        backup_file.write_text('{"old": "backup", "test": true}')
        print(f"Created backup file: {backup_file.exists()}")
        print(f"Backup content: {backup_file.read_text()[:50]}...")
        
        # Modify workflow and save again
        print("\n=== Second Save (with existing backup) ===")
        workflow.mark_module_completed('DirectoryConfig', ExecutionResult('success', 'Done'))
        
        try:
            workflow.save_to_disk()
            print("Save completed successfully")
        except Exception as e:
            print(f"Save failed with error: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"Main file exists: {main_file.exists()}")
        print(f"Backup file exists: {backup_file.exists()}")
        
        if backup_file.exists():
            backup_content = backup_file.read_text()
            print(f"Backup content: {backup_content[:100]}...")
            print(f"Backup is original content: {'old' in backup_content}")
            
        # Show what files are actually in the directory
        print(f"\nAll files in directory:")
        for file_path in storage_dir.iterdir():
            print(f"  {file_path.name} ({file_path.stat().st_size} bytes)")

if __name__ == "__main__":
    debug_save_behavior()
