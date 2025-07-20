"""
Additional tests for UserJourney plugin coverage gaps.

These tests address critical areas that were not covered in the main test suite,
focusing on error handling, edge cases, and integration scenarios.
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import json

from asciidoc_dita_toolkit.asciidoc_dita.plugins.UserJourney import (
    WorkflowState, WorkflowManager, UserJourneyProcessor,
    ExecutionResult, ModuleExecutionState, WorkflowProgress,
    WorkflowError, WorkflowExecutionError, InvalidDirectoryError
)


class TestCoverageGaps:
    """Tests for previously uncovered functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_dir = Path(self.temp_dir) / "workflows"
        WorkflowManager.set_storage_directory(self.storage_dir)
        
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        WorkflowManager._storage_dir = None
        WorkflowState._default_storage_dir = None
    
    def test_directory_config_import_failure(self):
        """Test workflow behavior when DirectoryConfig is not available."""
        # Create a workflow instance first
        modules = ["DirectoryConfig", "ContentType"]
        workflow = WorkflowState("test_workflow", "/test/docs", modules)
        
        # Now test the _refresh_file_discovery method with import failure
        with patch('asciidoc_dita_toolkit.asciidoc_dita.plugins.UserJourney.logging') as mock_logging:
            # Mock the specific import inside _refresh_file_discovery to fail
            import_path = 'asciidoc_dita_toolkit.asciidoc_dita.plugins.DirectoryConfig'
            with patch.dict('sys.modules', {import_path: None}):
                # Force the method to take the exception path
                original_path = workflow.directory
                workflow.directory = Path("/nonexistent/path")  # This will cause fallback
                workflow._refresh_file_discovery()
                
                # Should fall back to simple .adoc file discovery without crashing
                assert isinstance(workflow.files_discovered, list)
                
                # Restore original path
                workflow.directory = original_path
            
    def test_module_execution_edge_cases(self):
        """Test edge cases in module execution."""
        workflow_manager = WorkflowManager()
        
        # Test with empty modules list
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir)
            test_file = test_dir / "test.adoc"
            test_file.write_text("= Test Document")
            
            with patch.object(workflow_manager, 'get_planned_modules', return_value=[]):
                workflow = workflow_manager.start_workflow("empty_workflow", str(test_dir))
                
                # Should handle empty module list gracefully
                result = workflow_manager.execute_next_module(workflow)
                assert result.status == "completed"
                assert result.message == "All modules completed"
    
    def test_storage_corruption_recovery(self):
        """Test recovery from corrupted workflow files."""
        workflow_name = "corrupted_test"
        modules = ["DirectoryConfig", "ContentType"]
        workflow = WorkflowState(workflow_name, "/test/docs", modules)
        
        # Save valid workflow
        workflow.save_to_disk()
        
        # Corrupt the main file
        storage_path = workflow.get_storage_path()
        storage_path.write_text('{"invalid": json')
        
        # Create a valid backup
        backup_path = storage_path.with_suffix('.backup')
        backup_path.write_text(json.dumps(workflow.to_dict(), indent=2))
        
        # Should recover from backup
        recovered_workflow = WorkflowState.load_from_disk(workflow_name)
        assert recovered_workflow.name == workflow_name
        assert len(recovered_workflow.modules) == 2
    
    def test_workflow_processor_edge_cases(self):
        """Test UserJourneyProcessor edge cases."""
        processor = UserJourneyProcessor()
        
        # Test with missing arguments
        class MockArgs:
            pass
        
        args = MockArgs()
        
        # Should handle missing name gracefully
        result = processor.process_start_command(args)
        assert result == 1  # Error exit code
        
        # Should handle missing directory gracefully  
        args.name = "test_workflow"
        result = processor.process_start_command(args)
        assert result == 1  # Error exit code
    
    def test_large_workflow_performance(self):
        """Test performance with large workflows."""
        # Create workflow with many modules
        large_module_list = [f"Module{i}" for i in range(100)]
        workflow = WorkflowState("large_workflow", "/test/docs", large_module_list)
        
        # Should handle large module lists efficiently
        progress = workflow.get_progress_summary()
        assert progress.total_modules == 100
        assert progress.completion_percentage == 0.0
        
        # Mark some modules as completed
        for i in range(25):
            workflow.mark_module_completed(
                f"Module{i}", 
                ExecutionResult("success", "Done", files_processed=10)
            )
        
        progress = workflow.get_progress_summary()
        assert progress.completion_percentage == 25.0
        assert progress.processed_files == 250  # 25 modules * 10 files each
    
    def test_concurrent_access_safety(self):
        """Test workflow safety under concurrent access."""
        workflow_name = "concurrent_test"
        modules = ["DirectoryConfig", "ContentType"]
        workflow = WorkflowState(workflow_name, "/test/docs", modules)
        workflow.save_to_disk()
        
        # Simulate concurrent modifications
        workflow1 = WorkflowState.load_from_disk(workflow_name)
        workflow2 = WorkflowState.load_from_disk(workflow_name)
        
        # Both modify state
        workflow1.mark_module_completed("DirectoryConfig", ExecutionResult("success", "Done"))
        workflow2.mark_module_failed("ContentType", "Test error")
        
        # Both save - last one wins
        workflow1.save_to_disk()
        workflow2.save_to_disk()
        
        # Reload and verify final state
        final_workflow = WorkflowState.load_from_disk(workflow_name)
        assert final_workflow.modules["ContentType"].status == "failed"
        assert final_workflow.modules["ContentType"].error_message == "Test error"
    
    def test_file_permission_errors(self):
        """Test handling of file permission errors."""
        workflow_name = "permission_test"
        modules = ["DirectoryConfig"]
        workflow = WorkflowState(workflow_name, "/test/docs", modules)
        
        # Mock permission error during save
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(Exception):  # Should raise WorkflowStateError
                workflow.save_to_disk()
    
    def test_unicode_path_handling(self):
        """Test handling of Unicode characters in paths and names."""
        unicode_name = "测试_workflow_🚀"
        modules = ["DirectoryConfig"]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            unicode_dir = Path(temp_dir) / "测试_directory_🗂️"
            unicode_dir.mkdir()
            
            workflow = WorkflowState(unicode_name, str(unicode_dir), modules)
            
            # Should handle Unicode paths correctly
            assert workflow.name == unicode_name
            assert unicode_dir.name in str(workflow.directory)
            
            # Should save and load Unicode names correctly
            workflow.save_to_disk()
            reloaded = WorkflowState.load_from_disk(unicode_name)
            assert reloaded.name == unicode_name
    
    def test_workflow_progress_edge_cases(self):
        """Test edge cases in progress calculation."""
        # Empty workflow
        empty_workflow = WorkflowState("empty", "/test", [])
        progress = empty_workflow.get_progress_summary()
        assert progress.total_modules == 0
        assert progress.completion_percentage == 0  # Should handle division by zero
        
        # Workflow with only failed modules
        failed_workflow = WorkflowState("failed", "/test", ["Module1", "Module2"])
        failed_workflow.mark_module_failed("Module1", "Error 1")
        failed_workflow.mark_module_failed("Module2", "Error 2")
        
        progress = failed_workflow.get_progress_summary()
        assert progress.failed_modules == 2
        assert progress.completion_percentage == 0  # Failed doesn't count as completed
        
        # Mixed status workflow
        mixed_workflow = WorkflowState("mixed", "/test", ["M1", "M2", "M3", "M4"])
        mixed_workflow.mark_module_completed("M1", ExecutionResult("success", "Done"))
        mixed_workflow.mark_module_failed("M2", "Error")
        mixed_workflow.mark_module_started("M3")
        # M4 remains pending
        
        progress = mixed_workflow.get_progress_summary()
        assert progress.completed_modules == 1
        assert progress.failed_modules == 1
        assert progress.pending_modules == 2  # M3 is "running", M4 is "pending"
        assert progress.completion_percentage == 25.0
        
    def test_workflow_state_validation_edge_cases(self):
        """Test edge cases in workflow state validation."""
        # Test missing required fields
        invalid_data = {"name": "test"}  # Missing directory and modules
        
        with pytest.raises(Exception):  # Should raise WorkflowStateError
            WorkflowState._validate_state_data(invalid_data)
        
        # Test data migration with different versions
        old_version_data = {
            "name": "test",
            "directory": "/test",
            "modules": {"Module1": {"status": "pending"}},
            "metadata": {"version": "0.9.0"}  # Old version
        }
        
        # Should migrate successfully
        migrated_data = WorkflowState._migrate_state_format(old_version_data)
        assert migrated_data["name"] == "test"  # Data preserved


class TestFormattingAndDisplay:
    """Test display and formatting functionality."""
    
    def test_time_duration_formatting(self):
        """Test the _format_time_duration method."""
        processor = UserJourneyProcessor()
        
        # Test different time ranges
        assert processor._format_time_duration(30.5) == "30.5s"
        assert processor._format_time_duration(90.0) == "1m 30s"
        assert processor._format_time_duration(3665.0) == "1h 1m"
        assert processor._format_time_duration(7325.5) == "2h 2m"
    
    def test_progress_bar_edge_cases(self):
        """Test progress bar display with edge cases."""
        processor = UserJourneyProcessor()
        
        # Zero modules
        progress = WorkflowProgress(0, 0, 0, 0, None, 0, 0, 0.0)
        # Should not crash with division by zero
        processor._show_progress_bar(progress)
        
        # Single module completed
        progress = WorkflowProgress(1, 1, 0, 0, None, 10, 10, 100.0)
        processor._show_progress_bar(progress)
        
        # Partial completion
        progress = WorkflowProgress(10, 3, 1, 6, "Module4", 100, 35, 30.0)
        processor._show_progress_bar(progress)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
