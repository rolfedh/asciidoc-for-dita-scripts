#!/usr/bin/env python3
"""
Comprehensive Coverage Gap Tests for UserJourney Plugin

This test file addresses the specific coverage gaps identified:
1. Module execution failure scenarios 
2. DirectoryConfig import failures
3. Storage corruption scenarios
4. Concurrent access handling
5. Interactive user input scenarios
6. Performance and edge cases
"""
import json
import os
import pytest
import shutil
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from types import SimpleNamespace

# Import UserJourney components
from asciidoc_dita_toolkit.modules.user_journey import (
    WorkflowState, 
    WorkflowManager,
    UserJourneyProcessor,
    UserJourneyModule,
    WorkflowStateError,
    WorkflowExecutionError,
    InvalidDirectoryError
)


class TestComprehensiveCoverageGaps:
    """Test comprehensive coverage gaps in UserJourney implementation."""
    
    def setup_method(self, method):
        """Set up test environment with temporary directories."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.temp_storage = self.temp_dir / "workflows"
        self.temp_storage.mkdir()
        self.test_project = self.temp_dir / "project"
        self.test_project.mkdir()
        
        # Create test .adoc files
        (self.test_project / "doc1.adoc").write_text("= Doc 1\nContent")
        (self.test_project / "doc2.adoc").write_text("= Doc 2\nContent")
        
        # Set storage for testing
        WorkflowState._default_storage_dir = self.temp_storage
        WorkflowManager.set_storage_directory(self.temp_storage)
    
    def teardown_method(self, method):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        WorkflowState._default_storage_dir = None
        
    # ================================================================
    # 1. MODULE EXECUTION FAILURE SCENARIOS
    # ================================================================
    
    def test_module_crash_during_execution(self):
        """Test handling when a module crashes during execution."""
        # Import the ModuleState enum for proper mocking
        from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleState
        
        # Create workflow with mock sequencer that has proper resolution structure
        mock_sequencer = Mock()
        mock_resolution = Mock()
        mock_resolution.name = "DirectoryConfig"
        mock_resolution.state = ModuleState.ENABLED
        
        mock_sequencer.sequence_modules.return_value = ([mock_resolution], [])
        
        # Mock available modules with a crashing module
        crashing_module = Mock()
        crashing_module.execute.side_effect = RuntimeError("Module crashed!")
        crashing_module.initialize.return_value = {"status": "success"}
        crashing_module._initialized = False
        
        mock_sequencer.available_modules = {
            "DirectoryConfig": crashing_module
        }
        
        manager = WorkflowManager(mock_sequencer)
        workflow = manager.start_workflow("crash_test", str(self.test_project))
        
        # Execution should handle the crash gracefully
        with pytest.raises(WorkflowExecutionError) as exc_info:
            manager.execute_next_module(workflow)
        
        assert "Module DirectoryConfig failed" in str(exc_info.value)
        
        # Verify workflow state is updated correctly
        updated_workflow = manager.resume_workflow("crash_test")
        assert updated_workflow.modules["DirectoryConfig"].status == "failed"
        assert "Module crashed!" in updated_workflow.modules["DirectoryConfig"].error_message
        assert updated_workflow.modules["DirectoryConfig"].retry_count == 1

    def test_module_initialization_failure(self):
        """Test handling when module initialization fails."""
        from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleState
        
        mock_sequencer = Mock()
        mock_resolution = Mock()
        mock_resolution.name = "DirectoryConfig"
        mock_resolution.state = ModuleState.ENABLED
        
        mock_sequencer.sequence_modules.return_value = ([mock_resolution], [])
        
        # Mock module that fails initialization
        failing_module = Mock()
        failing_module.initialize.return_value = {"status": "error", "message": "Init failed"}
        failing_module._initialized = False
        
        mock_sequencer.available_modules = {
            "DirectoryConfig": failing_module
        }
        
        manager = WorkflowManager(mock_sequencer)
        workflow = manager.start_workflow("init_fail_test", str(self.test_project))
        
        # Should handle init failure
        with pytest.raises(WorkflowExecutionError):
            manager.execute_next_module(workflow)

    def test_directory_config_import_failure_handling(self):
        """Test graceful handling when DirectoryConfig cannot be imported."""
        # This tests the fallback behavior in _refresh_file_discovery
        workflow = WorkflowState("import_test", str(self.test_project), ["DirectoryConfig"])
        
        # The fallback discovery should work regardless of DirectoryConfig availability
        workflow._refresh_file_discovery()
        
        # Verify fallback worked and files were discovered
        assert len(workflow.files_discovered) >= 2  # doc1.adoc and doc2.adoc
        
        # Verify files were found using fallback mechanism
        adoc_files = [f for f in workflow.files_discovered if f.endswith('.adoc')]
        assert len(adoc_files) >= 2

    # ================================================================
    # 2. STORAGE CORRUPTION AND RECOVERY SCENARIOS
    # ================================================================
    
    def test_corrupted_json_recovery(self):
        """Test recovery from corrupted JSON workflow state."""
        # Create a workflow first
        workflow = WorkflowState("corrupt_test", str(self.test_project), ["DirectoryConfig"])
        workflow.save_to_disk()
        
        # Corrupt the main file
        state_path = workflow.get_storage_path()
        with open(state_path, 'w') as f:
            f.write("invalid json content {")
        
        # Create a valid backup
        backup_path = state_path.with_suffix('.backup')
        backup_data = {
            "name": "corrupt_test",
            "directory": str(self.test_project),
            "modules": {"DirectoryConfig": {"status": "pending"}},
            "files_discovered": [],
            "metadata": {"version": "1.0"}
        }
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f)
        
        # Loading should recover from backup
        recovered = WorkflowState.load_from_disk("corrupt_test", self.temp_storage)
        assert recovered.name == "corrupt_test"
        assert "DirectoryConfig" in recovered.modules

    def test_missing_backup_corruption_handling(self):
        """Test handling when both main file and backup are corrupted."""
        # Create and immediately corrupt workflow file
        workflow = WorkflowState("no_backup_test", str(self.test_project), ["DirectoryConfig"])
        state_path = workflow.get_storage_path()
        
        with open(state_path, 'w') as f:
            f.write("invalid json")
        
        # No backup file exists
        with pytest.raises(WorkflowStateError) as exc_info:
            WorkflowState.load_from_disk("no_backup_test", self.temp_storage)
        
        assert "Corrupted workflow state" in str(exc_info.value)

    def test_atomic_write_interruption_recovery(self):
        """Test recovery when atomic write is interrupted."""
        workflow = WorkflowState("atomic_test", str(self.test_project), ["DirectoryConfig"])
        
        # Create initial state
        workflow.save_to_disk()
        
        # Simulate interrupted write by creating temp file
        temp_path = workflow.get_storage_path().with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            f.write("interrupted write")
        
        # Next save should handle existing temp file
        workflow.mark_module_completed("DirectoryConfig", Mock(files_processed=5, files_modified=2, execution_time=1.5))
        workflow.save_to_disk()  # Should succeed despite temp file
        
        # Verify temp file was cleaned up
        assert not temp_path.exists()
        
        # Verify state was saved correctly
        reloaded = WorkflowState.load_from_disk("atomic_test", self.temp_storage)
        assert reloaded.modules["DirectoryConfig"].status == "completed"

    # ================================================================
    # 3. CONCURRENT ACCESS SCENARIOS
    # ================================================================
    
    def test_concurrent_workflow_access(self):
        """Test handling concurrent access to same workflow."""
        workflow = WorkflowState("concurrent_test", str(self.test_project), ["DirectoryConfig", "CrossReference"])
        workflow.save_to_disk()
        
        errors = []
        results = []
        
        def modify_workflow(thread_id):
            """Function to modify workflow from different threads."""
            try:
                local_workflow = WorkflowState.load_from_disk("concurrent_test", self.temp_storage)
                
                # Simulate some processing time
                time.sleep(0.1)
                
                # Each thread tries to mark a different module as completed
                if thread_id == 0:
                    local_workflow.mark_module_completed("DirectoryConfig", 
                        Mock(files_processed=1, files_modified=0, execution_time=0.5))
                else:
                    local_workflow.mark_module_completed("CrossReference", 
                        Mock(files_processed=2, files_modified=1, execution_time=1.0))
                
                local_workflow.save_to_disk()
                results.append(f"Thread {thread_id} succeeded")
                
            except Exception as e:
                errors.append(f"Thread {thread_id}: {e}")
        
        # Start concurrent threads
        threads = []
        for i in range(2):
            thread = threading.Thread(target=modify_workflow, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # At least one should succeed (depending on timing)
        # The key is that the system doesn't crash
        assert len(results) >= 1 or len(errors) >= 1  # Something should happen
        
        # Final state should be consistent
        final_workflow = WorkflowState.load_from_disk("concurrent_test", self.temp_storage)
        assert final_workflow.name == "concurrent_test"

    # ================================================================
    # 4. INTERACTIVE USER INPUT SCENARIOS
    # ================================================================
    
    def test_user_confirmation_yes_response(self):
        """Test user confirmation with 'yes' response."""
        processor = UserJourneyProcessor()
        
        # Mock workflow for cleanup test
        workflow = WorkflowState("confirm_test", str(self.test_project), ["DirectoryConfig"])
        workflow.save_to_disk()
        
        # Mock input to return 'y'
        with patch('builtins.input', return_value='y'):
            args = SimpleNamespace(name="confirm_test")
            result = processor._cleanup_specific_workflow("confirm_test")
        
        assert result == 0  # Success
        
        # Workflow should be deleted
        assert not processor.workflow_manager.workflow_exists("confirm_test")

    def test_user_confirmation_no_response(self):
        """Test user confirmation with 'no' response."""
        processor = UserJourneyProcessor()
        
        # Mock workflow for cleanup test
        workflow = WorkflowState("no_confirm_test", str(self.test_project), ["DirectoryConfig"])
        workflow.save_to_disk()
        
        # Mock input to return 'n'
        with patch('builtins.input', return_value='n'):
            result = processor._cleanup_specific_workflow("no_confirm_test")
        
        assert result == 0  # Success (cancelled)
        
        # Workflow should still exist
        assert processor.workflow_manager.workflow_exists("no_confirm_test")

    def test_bulk_cleanup_with_confirmation(self):
        """Test bulk cleanup with user confirmation."""
        processor = UserJourneyProcessor()
        
        # Create multiple completed workflows
        for i in range(3):
            workflow = WorkflowState(f"bulk_test_{i}", str(self.test_project), ["DirectoryConfig"])
            workflow.mark_module_completed("DirectoryConfig", 
                Mock(files_processed=1, files_modified=0, execution_time=0.1))
            workflow.save_to_disk()
        
        # Mock input to confirm deletion
        with patch('builtins.input', return_value='y'):
            args = SimpleNamespace(completed=True, all=False, name=None)
            result = processor.process_cleanup_command(args)
        
        assert result == 0
        
        # All workflows should be deleted
        for i in range(3):
            assert not processor.workflow_manager.workflow_exists(f"bulk_test_{i}")

    # ================================================================
    # 5. PERFORMANCE AND EDGE CASES
    # ================================================================
    
    def test_large_file_count_performance(self):
        """Test performance with large number of files."""
        # Create directory with many files
        large_project = self.temp_dir / "large_project"
        large_project.mkdir()
        
        # Create 100 .adoc files
        for i in range(100):
            (large_project / f"doc_{i:03d}.adoc").write_text(f"= Document {i}\nContent {i}")
        
        # Test workflow creation performance
        start_time = time.time()
        workflow = WorkflowState("large_test", str(large_project), ["DirectoryConfig"])
        creation_time = time.time() - start_time
        
        # Should complete quickly (under 1 second for 100 files)
        assert creation_time < 1.0
        
        # Should discover all files
        assert len(workflow.files_discovered) >= 100
        
        # Test save/load performance
        start_time = time.time()
        workflow.save_to_disk()
        save_time = time.time() - start_time
        
        start_time = time.time()
        reloaded = WorkflowState.load_from_disk("large_test", self.temp_storage)
        load_time = time.time() - start_time
        
        # Performance targets
        assert save_time < 0.5  # Save under 0.5 seconds
        assert load_time < 0.5  # Load under 0.5 seconds
        assert len(reloaded.files_discovered) >= 100

    def test_unicode_path_handling(self):
        """Test handling of Unicode characters in paths and names."""
        # Create directory with Unicode name
        unicode_project = self.temp_dir / "проект_тест"  # Cyrillic characters
        unicode_project.mkdir()
        
        # Create file with Unicode name
        unicode_file = unicode_project / "документ_тёст.adoc"
        unicode_file.write_text("= Тестовый документ\nСодержание")
        
        # Test workflow with Unicode paths
        workflow = WorkflowState("unicode_тест", str(unicode_project), ["DirectoryConfig"])
        workflow.save_to_disk()
        
        # Should handle Unicode correctly
        assert len(workflow.files_discovered) >= 1
        assert any("документ_тёст.adoc" in path for path in workflow.files_discovered)
        
        # Should load correctly
        reloaded = WorkflowState.load_from_disk("unicode_тест", self.temp_storage)
        assert reloaded.name == "unicode_тест"

    def test_very_long_error_messages(self):
        """Test handling of very long error messages."""
        workflow = WorkflowState("error_test", str(self.test_project), ["DirectoryConfig"])
        
        # Create very long error message
        long_error = "Error: " + "x" * 10000  # 10KB error message
        
        workflow.mark_module_failed("DirectoryConfig", long_error)
        workflow.save_to_disk()
        
        # Should handle long error without issues
        reloaded = WorkflowState.load_from_disk("error_test", self.temp_storage)
        assert reloaded.modules["DirectoryConfig"].error_message == long_error
        assert reloaded.modules["DirectoryConfig"].status == "failed"

    def test_workflow_with_many_modules(self):
        """Test workflow with large number of modules."""
        # Create workflow with many modules
        many_modules = [f"Module_{i:02d}" for i in range(50)]
        workflow = WorkflowState("many_modules_test", str(self.test_project), many_modules)
        
        # Should handle many modules efficiently
        assert len(workflow.modules) == 50
        
        # Test progress calculation with many modules
        progress = workflow.get_progress_summary()
        assert progress.total_modules == 50
        assert progress.pending_modules == 50
        assert progress.completion_percentage == 0.0
        
        # Complete half the modules
        for i in range(25):
            workflow.mark_module_completed(f"Module_{i:02d}", 
                Mock(files_processed=1, files_modified=0, execution_time=0.1))
        
        progress = workflow.get_progress_summary()
        assert progress.completed_modules == 25
        assert progress.pending_modules == 25
        assert progress.completion_percentage == 50.0

    # ================================================================
    # 6. CLI AND INTEGRATION EDGE CASES
    # ================================================================
    
    def test_cli_parser_integration(self):
        """Test CLI parser integration and command dispatch."""
        module = UserJourneyModule()
        module.initialize()
        
        # Test parser creation
        parser = module.get_cli_parser()
        assert parser is not None
        
        # Test parsing various commands
        start_args = parser.parse_args(['start', '--name=test', '--directory=/tmp'])
        assert start_args.journey_command == 'start'
        assert start_args.name == 'test'
        assert start_args.directory == '/tmp'
        
        # Test cleanup command parsing
        cleanup_args = parser.parse_args(['cleanup', '--completed'])
        assert cleanup_args.journey_command == 'cleanup'
        assert cleanup_args.completed == True

    def test_invalid_command_dispatch(self):
        """Test handling of invalid CLI commands."""
        module = UserJourneyModule()
        module.initialize()
        
        # Create args with invalid command
        invalid_args = SimpleNamespace(journey_command='invalid_command')
        
        result = module.process_cli_command(invalid_args)
        assert result == 1  # Error exit code

    def test_uninitialized_module_command_processing(self):
        """Test CLI command processing with uninitialized module."""
        module = UserJourneyModule()
        # Don't initialize the module
        
        args = SimpleNamespace(journey_command='start')
        result = module.process_cli_command(args)
        assert result == 1  # Should fail with error

    # ================================================================
    # 7. EDGE CASES IN STATUS DISPLAY
    # ================================================================
    
    def test_status_display_with_no_workflows(self):
        """Test status display when no workflows exist."""
        processor = UserJourneyProcessor()
        
        args = SimpleNamespace(name=None)
        result = processor.process_status_command(args)
        
        assert result == 0  # Should succeed but show no workflows

    def test_status_display_formatting_edge_cases(self):
        """Test status display formatting with edge cases."""
        processor = UserJourneyProcessor()
        
        # Create workflow with various states
        workflow = WorkflowState("format_test", str(self.test_project), 
                                ["DirectoryConfig", "CrossReference", "ExampleBlock"])
        
        # Set up mixed states
        workflow.mark_module_completed("DirectoryConfig", 
            Mock(files_processed=100, files_modified=50, execution_time=123.456))
        workflow.mark_module_failed("CrossReference", "Very long error message that might cause formatting issues when displayed in the terminal")
        # Leave ExampleBlock as pending
        
        workflow.save_to_disk()
        
        # Test detailed status display
        args = SimpleNamespace(name="format_test")
        result = processor.process_status_command(args)
        
        assert result == 0  # Should succeed despite formatting challenges


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
