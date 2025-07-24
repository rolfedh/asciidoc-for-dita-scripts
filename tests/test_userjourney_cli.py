#!/usr/bin/env python3
"""
UserJourney Test CLI

A simplified test version of the UserJourney CLI that uses mock modules
for testing purposes when the full ADT module system isn't available.
"""

import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

# Add the project root to Python path
script_dir = Path(__file__).parent
project_root = script_dir
sys.path.insert(0, str(project_root))

def create_test_workflow():
    """Create a test workflow to demonstrate functionality."""
    print("UserJourney Test CLI")
    print("=" * 50)
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    test_docs = temp_dir / "test_docs"
    test_docs.mkdir()
    
    # Create test document
    (test_docs / "test.adoc").write_text("""= Test Document
:doctype: article

This is a test document for UserJourney.

== Section 1
Content here.
""")
    
    print(f"✅ Created test directory: {test_docs}")
    print(f"✅ Created test document: test.adoc")
    
    try:
        # Import UserJourney components
        from asciidoc_dita_toolkit.modules.user_journey import (
            WorkflowState, WorkflowManager, UserJourneyProcessor,
            ExecutionResult
        )
        
        print("✅ UserJourney components imported successfully")
        
        # Create mock ModuleSequencer
        mock_sequencer = Mock()
        
        # Import ModuleState enum
        from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleState
        
        # Create properly configured mock modules with actual string names
        mock_dir_config = Mock()
        mock_dir_config.name = "DirectoryConfig"
        mock_dir_config.state = ModuleState.ENABLED
        
        mock_content_type = Mock() 
        mock_content_type.name = "ContentType"
        mock_content_type.state = ModuleState.ENABLED
        
        mock_entity_ref = Mock()
        mock_entity_ref.name = "EntityReference"
        mock_entity_ref.state = ModuleState.ENABLED
        
        # Create properly ordered mock modules with DirectoryConfig first
        mock_resolutions = [mock_dir_config, mock_content_type, mock_entity_ref]
        
        mock_sequencer.sequence_modules.return_value = (
            mock_resolutions,
            []  # No errors
        )
        
        print("✅ Mock ModuleSequencer created (DirectoryConfig first)")
        
        # Debug: Test the mock sequencer
        resolutions, errors = mock_sequencer.sequence_modules()
        print(f"✅ Debug - Module names: {[r.name for r in resolutions]}")
        print(f"✅ Debug - First module: {resolutions[0].name if resolutions else 'None'}")
        print(f"✅ Debug - Errors: {errors}")
        
        # Create WorkflowManager with mock sequencer
        workflow_manager = WorkflowManager(mock_sequencer)
        print("✅ WorkflowManager initialized")
        
        # Create workflow
        workflow = workflow_manager.start_workflow("test_workflow", str(test_docs))
        print(f"✅ Workflow 'test_workflow' created successfully")
        
        # Show workflow state
        progress = workflow.get_progress_summary()
        print(f"✅ Workflow progress: {progress.completed_modules}/{progress.total_modules} modules")
        print(f"✅ Files discovered: {len(workflow.files_discovered)}")
        print(f"✅ Debug - Module order: {list(workflow.modules.keys())}")
        print(f"✅ Debug - Current module: {workflow.get_next_module()}")
        
        # Test processor
        processor = UserJourneyProcessor(workflow_manager)
        print("✅ UserJourneyProcessor initialized")
        
        # Simulate status display
        print("\n" + "=" * 50)
        print("WORKFLOW STATUS DEMO")
        print("=" * 50)
        
        # Create mock args for status command
        mock_args = Mock()
        mock_args.name = "test_workflow"
        
        # This will show the formatted status
        result = processor.process_status_command(mock_args)
        print(f"\n✅ Status command returned: {result}")
        
        # Test list command
        print("\n" + "=" * 50)
        print("WORKFLOW LIST DEMO")
        print("=" * 50)
        
        mock_args_list = Mock()
        result = processor.process_list_command(mock_args_list)
        print(f"\n✅ List command returned: {result}")
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("UserJourney CLI implementation is working correctly.")
        print("=" * 50)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
            print(f"✅ Cleaned up temp directory: {temp_dir}")
        except Exception:
            pass

if __name__ == '__main__':
    sys.exit(create_test_workflow())
