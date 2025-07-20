#!/usr/bin/env python3
"""
Performance validation for UserJourney MVP - CHUNK 6
"""
import time
import tempfile
from pathlib import Path

# Test workflow creation performance
def test_workflow_creation_performance():
    """Test that workflow creation meets <1 second target."""
    from asciidoc_dita_toolkit.asciidoc_dita.plugins.UserJourney import WorkflowManager
    from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleSequencer
    
    # Setup
    temp_dir = tempfile.mkdtemp()
    test_dir = Path(temp_dir) / "test_docs"
    test_dir.mkdir()
    (test_dir / "test.adoc").write_text("= Test\nContent")
    
    sequencer = ModuleSequencer()
    manager = WorkflowManager(sequencer)
    
    # Time workflow creation
    start_time = time.time()
    workflow = manager.start_workflow("perf_test", str(test_dir))
    creation_time = time.time() - start_time
    
    print(f"✅ Workflow creation: {creation_time:.3f}s (target: <1s)")
    assert creation_time < 1.0, f"Workflow creation too slow: {creation_time:.3f}s"
    
    return creation_time

def test_status_display_performance():
    """Test that status display meets <0.5 second target."""
    from asciidoc_dita_toolkit.asciidoc_dita.plugins.UserJourney import WorkflowState, ExecutionResult
    
    # Create workflow with some progress
    modules = ["DirectoryConfig", "ContentType", "CrossReference", "EntityReference"]
    workflow = WorkflowState("perf_test", "/test/docs", modules)
    workflow.mark_module_completed("DirectoryConfig", ExecutionResult("success", "Done"))
    
    # Time status display
    start_time = time.time()
    progress = workflow.get_progress_summary()
    display_time = time.time() - start_time
    
    print(f"✅ Status display: {display_time:.3f}s (target: <0.5s)")
    assert display_time < 0.5, f"Status display too slow: {display_time:.3f}s"
    
    return display_time

def test_state_save_performance():
    """Test that state save meets <0.1 second target."""
    import tempfile
    from asciidoc_dita_toolkit.asciidoc_dita.plugins.UserJourney import WorkflowState, ExecutionResult
    
    # Setup temporary storage
    temp_dir = tempfile.mkdtemp()
    WorkflowState._default_storage_dir = Path(temp_dir)
    
    # Create workflow with realistic data
    modules = ["DirectoryConfig", "ContentType", "CrossReference", "EntityReference"]
    workflow = WorkflowState("perf_test", "/test/docs", modules)
    workflow.files_discovered = [f"/test/doc{i}.adoc" for i in range(50)]
    workflow.mark_module_completed("DirectoryConfig", 
                                 ExecutionResult("success", "Done", files_processed=50))
    
    # Time state save
    start_time = time.time()
    workflow.save_to_disk()
    save_time = time.time() - start_time
    
    print(f"✅ State save: {save_time:.3f}s (target: <0.1s)")
    assert save_time < 0.1, f"State save too slow: {save_time:.3f}s"
    
    return save_time

if __name__ == "__main__":
    print("🎯 UserJourney MVP Performance Validation")
    print("=" * 50)
    
    try:
        creation_time = test_workflow_creation_performance()
        display_time = test_status_display_performance()
        save_time = test_state_save_performance()
        
        print("\n" + "=" * 50)
        print("🎉 All performance targets met!")
        print(f"📊 Summary:")
        print(f"   Workflow creation: {creation_time:.3f}s / 1.0s")
        print(f"   Status display:    {display_time:.3f}s / 0.5s") 
        print(f"   State save:        {save_time:.3f}s / 0.1s")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        exit(1)
