"""
Comprehensive Test Framework for UserJourney Plugin - Chunk 4 Implementation

This module provides comprehensive test coverage following the Chunk 4 specification:
1. Unit Tests - State persistence, module state transitions, progress calculations
2. Integration Tests - ModuleSequencer integration, DirectoryConfig integration  
3. Scenario Tests - Complete workflow execution, interruption/resume, module failures

Focus Areas:
- Test fixtures utilization
- Mock ModuleSequencer patterns
- State persistence edge cases
- CLI command comprehensive testing
- Performance validation
"""

import unittest
import tempfile
import shutil
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, call
from concurrent.futures import ThreadPoolExecutor

# Import UserJourney components
from asciidoc_dita_toolkit.asciidoc_dita.plugins.UserJourney import (
    WorkflowState, WorkflowManager, UserJourneyProcessor,
    ExecutionResult, WorkflowProgress, ModuleExecutionState,
    UserJourneyError, WorkflowError, WorkflowNotFoundError,
    WorkflowExistsError, WorkflowStateError, InvalidDirectoryError,
    WorkflowExecutionError, WorkflowPlanningError
)

from modules.user_journey import UserJourney


class TestFixtureLoader:
    """Utility class for loading test fixtures."""
    
    @staticmethod
    def get_fixture_path():
        """Get path to UserJourney test fixtures."""
        return Path(__file__).parent / "fixtures" / "UserJourney"
    
    @staticmethod
    def load_workflow_state_fixture(name):
        """Load a workflow state fixture by name."""
        fixture_path = TestFixtureLoader.get_fixture_path() / "workflow_states" / f"{name}.json"
        with open(fixture_path) as f:
            return json.load(f)
    
    @staticmethod
    def load_mock_response_fixture(name):
        """Load a mock response fixture by name."""
        fixture_path = TestFixtureLoader.get_fixture_path() / "mock_responses" / f"{name}.json"
        with open(fixture_path) as f:
            return json.load(f)
    
    @staticmethod
    def get_test_directory_fixture(name):
        """Get path to a test directory fixture."""
        return TestFixtureLoader.get_fixture_path() / "test_directories" / name


class MockModuleSequencerFactory:
    """Factory for creating consistent ModuleSequencer mocks."""
    
    @staticmethod
    def create_standard_mock():
        """Create standard mock with successful sequence."""
        from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleState
        
        mock = Mock()
        fixture_data = TestFixtureLoader.load_mock_response_fixture("standard_sequence")
        
        # Convert fixture data to Mock objects with proper enum states
        resolutions = []
        for res in fixture_data["resolutions"]:
            mock_res = Mock()
            mock_res.name = res["name"]
            # Convert string state to enum
            if res["state"] == "enabled":
                mock_res.state = ModuleState.ENABLED
            elif res["state"] == "disabled":
                mock_res.state = ModuleState.DISABLED  
            else:
                mock_res.state = res["state"]  # Keep as-is if not recognized
            mock_res.dependencies = res["dependencies"]
            resolutions.append(mock_res)
        
        mock.sequence_modules.return_value = (resolutions, fixture_data["errors"])
        mock.available_modules = {res.name: Mock(name=res.name) for res in resolutions}
        
        return mock
    
    @staticmethod
    def create_error_mock():
        """Create mock with sequencing errors."""
        from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleState
        
        mock = Mock()
        fixture_data = TestFixtureLoader.load_mock_response_fixture("error_sequence")
        
        resolutions = []
        for res in fixture_data["resolutions"]:
            mock_res = Mock()
            mock_res.name = res["name"]
            # Convert string state to enum
            if res["state"] == "enabled":
                mock_res.state = ModuleState.ENABLED
            elif res["state"] == "disabled":
                mock_res.state = ModuleState.DISABLED
            else:
                mock_res.state = res["state"]
            mock_res.dependencies = res["dependencies"]
            resolutions.append(mock_res)
        
        mock.sequence_modules.return_value = (resolutions, fixture_data["errors"])
        mock.available_modules = {res.name: Mock(name=res.name) for res in resolutions}
        
        return mock


class TestStatePersistenceAdvanced(unittest.TestCase):
    """Advanced test cases for state persistence following Chunk 4 spec."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_dir = Path(self.temp_dir) / ".adt" / "workflows"
        self.storage_dir.mkdir(parents=True)
        
        # Configure storage directory for testing
        WorkflowState._default_storage_dir = self.storage_dir
        
        self.workflow_name = "test_workflow"
    
    def tearDown(self):
        """Clean up test environment.""" 
        # Reset storage directory
        WorkflowState._default_storage_dir = None
        shutil.rmtree(self.temp_dir)
    
    def test_atomic_save_success(self):
        """Test atomic save pattern works correctly."""
        modules = ["DirectoryConfig", "ContentType", "CrossReference"]
        workflow = WorkflowState(self.workflow_name, "/test/docs", modules)
        
        # Save to disk
        workflow.save_to_disk()
        
        # Verify final file exists
        expected_path = self.storage_dir / f"{self.workflow_name}.json"
        self.assertTrue(expected_path.exists())
        
        # Verify no temp files remain
        self.assertFalse((expected_path.with_suffix('.tmp')).exists())
        self.assertFalse((expected_path.with_suffix('.backup')).exists())
    
    def test_atomic_save_with_existing_backup(self):
        """Test atomic save when previous backup exists."""
        modules = ["DirectoryConfig", "ContentType"]
        workflow = WorkflowState(self.workflow_name, "/test/docs", modules)
        
        # First create and save the workflow to create initial state
        workflow.save_to_disk()
        
        # Create existing backup file (simulating previous backup)
        backup_path = self.storage_dir / f"{self.workflow_name}.backup"  # Changed from .json.backup to .backup
        backup_path.write_text('{"old": "backup"}')
        
        # Modify and save workflow again
        workflow.mark_module_completed("DirectoryConfig", ExecutionResult("success", "Done"))
        workflow.save_to_disk()
        
        # Verify backup was cleaned up (since a new one was created and then removed)
        self.assertFalse(backup_path.exists())
        
        # Verify workflow saved correctly
        expected_path = self.storage_dir / f"{self.workflow_name}.json" 
        self.assertTrue(expected_path.exists())
        data = json.loads(expected_path.read_text())
        self.assertEqual(data["name"], self.workflow_name)
    
    def test_save_failure_recovery(self):
        """Test backup recovery when save fails."""
        modules = ["DirectoryConfig"]
        workflow = WorkflowState(self.workflow_name, "/test/docs", modules)
        
        # Create initial state
        workflow.save_to_disk()
        original_data = json.loads((self.storage_dir / f"{self.workflow_name}.json").read_text())
        
        # Modify workflow
        workflow.mark_module_completed("DirectoryConfig", ExecutionResult("success", "Done"))
        
        # Mock file write failure
        with patch('builtins.open', side_effect=PermissionError("Disk full")):
            with self.assertRaises(WorkflowStateError):
                workflow.save_to_disk()
        
        # Verify original state still exists
        current_data = json.loads((self.storage_dir / f"{self.workflow_name}.json").read_text())
        self.assertEqual(current_data, original_data)
    
    def test_load_with_corruption_recovery(self):
        """Test loading corrupted state file with recovery."""
        # Copy corrupted fixture
        corrupted_fixture = TestFixtureLoader.get_fixture_path() / "workflow_states" / "corrupted_workflow.json"
        corrupted_target = self.storage_dir / f"{self.workflow_name}.json"
        shutil.copy2(corrupted_fixture, corrupted_target)
        
        # Attempt to load should raise WorkflowStateError (not WorkflowNotFoundError)
        with self.assertRaises(WorkflowStateError):
            WorkflowState.load_from_disk(self.workflow_name)
    
    def test_state_migration_version_upgrade(self):
        """Test state format migration for version upgrades."""
        # Create old format state (missing new fields)
        old_state = {
            "name": self.workflow_name,
            "directory": "/test/docs",
            "status": "active",
            "modules": {"DirectoryConfig": {"status": "pending"}},
            # Missing: created, last_activity, files_discovered, metadata
        }
        
        state_file = self.storage_dir / f"{self.workflow_name}.json"
        with open(state_file, 'w') as f:
            json.dump(old_state, f)
        
        # Load should handle migration gracefully
        workflow = WorkflowState.load_from_disk(self.workflow_name)
        
        # Verify migrated fields have defaults
        self.assertIsNotNone(workflow.created)
        self.assertIsNotNone(workflow.last_activity)
        self.assertEqual(workflow.files_discovered, [])
        self.assertIn("version", workflow.to_dict()["metadata"])
    
    def test_concurrent_access_safety(self):
        """Test concurrent access to workflow state."""
        modules = ["DirectoryConfig", "ContentType"]
        workflow1 = WorkflowState(self.workflow_name, "/test/docs", modules)
        workflow1.save_to_disk()
        
        # Function to modify and save workflow
        def modify_workflow(module_name, delay=0):
            time.sleep(delay)
            wf = WorkflowState.load_from_disk(self.workflow_name)
            wf.mark_module_completed(module_name, ExecutionResult("success", f"Completed {module_name}"))
            wf.save_to_disk()
            return wf
        
        # Run concurrent modifications
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(modify_workflow, "DirectoryConfig", 0.1)
            future2 = executor.submit(modify_workflow, "ContentType", 0.2)
            
            result1 = future1.result()
            result2 = future2.result()
        
        # Load final state - should have both modifications or one overwrote other
        final_workflow = WorkflowState.load_from_disk(self.workflow_name)
        completed_modules = [name for name, state in final_workflow.modules.items() 
                           if state.status == "completed"]
        
        # At least one should be completed (depending on timing)
        self.assertGreaterEqual(len(completed_modules), 1)


class TestWorkflowStateMethods(unittest.TestCase):
    """Unit tests for WorkflowState methods."""
    
    def setUp(self):
        """Set up test environment."""
        self.modules = ["DirectoryConfig", "ContentType", "CrossReference"]
        self.workflow = WorkflowState("test", "/docs", self.modules)
    
    def test_get_next_module_dependency_order(self):
        """Test get_next_module respects dependency order."""
        # Complete DirectoryConfig first
        self.workflow.mark_module_completed(
            "DirectoryConfig", 
            ExecutionResult("success", "Done", files_processed=5)
        )
        
        next_module = self.workflow.get_next_module()
        self.assertIn(next_module, ["ContentType", "CrossReference"])
    
    def test_progress_calculation_accuracy(self):
        """Test progress calculation with various states."""
        # Initial state - all pending
        progress = self.workflow.get_progress_summary()
        self.assertEqual(progress.completion_percentage, 0.0)
        self.assertEqual(progress.completed_modules, 0)
        self.assertEqual(progress.total_modules, 3)
        
        # Complete one module
        self.workflow.mark_module_completed(
            "DirectoryConfig",
            ExecutionResult("success", "Done", files_processed=5)
        )
        
        progress = self.workflow.get_progress_summary()
        self.assertAlmostEqual(progress.completion_percentage, 33.33, places=1)
        self.assertEqual(progress.completed_modules, 1)
        self.assertEqual(progress.processed_files, 5)
        
        # Fail one module 
        self.workflow.mark_module_failed(
            "ContentType",
            ExecutionResult("error", "Processing failed", error_message="Test error")
        )
        
        progress = self.workflow.get_progress_summary()
        self.assertEqual(progress.failed_modules, 1)
        self.assertEqual(progress.pending_modules, 1)
    
    def test_state_transitions_complete_cycle(self):
        """Test complete state transition cycle."""
        module_name = "DirectoryConfig"
        
        # Start module
        self.workflow.mark_module_started(module_name)
        state = self.workflow.modules[module_name]
        self.assertEqual(state.status, "running")
        self.assertIsNotNone(state.started_at)
        
        # Complete module  
        result = ExecutionResult("success", "Completed successfully", 
                               files_processed=10, execution_time=30.5)
        self.workflow.mark_module_completed(module_name, result)
        
        state = self.workflow.modules[module_name]
        self.assertEqual(state.status, "completed")
        self.assertEqual(state.files_processed, 10)
        self.assertEqual(state.execution_time, 30.5)
        self.assertIsNotNone(state.completed_at)
    
    def test_retry_count_tracking(self):
        """Test retry count increments correctly."""
        module_name = "ContentType"
        
        # First failure
        result = ExecutionResult("error", "First failure", error_message="Network timeout")
        self.workflow.mark_module_failed(module_name, result)
        self.assertEqual(self.workflow.modules[module_name].retry_count, 1)
        
        # Second failure
        result = ExecutionResult("error", "Second failure", error_message="Invalid input")
        self.workflow.mark_module_failed(module_name, result)
        self.assertEqual(self.workflow.modules[module_name].retry_count, 2)
        
        # Success resets retry count
        result = ExecutionResult("success", "Finally worked")
        self.workflow.mark_module_completed(module_name, result)
        self.assertEqual(self.workflow.modules[module_name].retry_count, 0)


class TestModuleSequencerIntegration(unittest.TestCase):
    """Integration tests for ModuleSequencer interaction."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_directory = Path(self.temp_dir) / "test_docs"
        self.test_directory.mkdir(parents=True)
        
        # Create test .adoc files for file discovery
        (self.test_directory / "doc1.adoc").write_text("= Document 1\nContent")
        (self.test_directory / "doc2.adoc").write_text("= Document 2\nContent")
        
        # Set up workflow storage
        self.workflow_dir = Path(self.temp_dir) / ".adt" / "workflows" 
        self.workflow_dir.mkdir(parents=True)
        WorkflowState._default_storage_dir = self.workflow_dir
        
    def tearDown(self):
        """Clean up test environment."""
        WorkflowState._default_storage_dir = None
        shutil.rmtree(self.temp_dir)
    
    def test_workflow_manager_standard_sequence(self):
        """Test WorkflowManager with standard module sequence."""
        mock_sequencer = MockModuleSequencerFactory.create_standard_mock()
        manager = WorkflowManager(mock_sequencer)
        manager._storage_dir = self.workflow_dir
        
        # Start workflow should call sequence_modules
        workflow = manager.start_workflow("test_standard", str(self.test_directory))
        
        mock_sequencer.sequence_modules.assert_called_once()
        self.assertEqual(len(workflow.modules), 3)  # DirectoryConfig, ContentType, CrossReference
        
        # All modules should start as pending
        for module_state in workflow.modules.values():
            self.assertEqual(module_state.status, "pending")
    
    def test_workflow_manager_sequencing_errors(self):
        """Test WorkflowManager handles sequencing errors."""
        mock_sequencer = MockModuleSequencerFactory.create_error_mock()
        manager = WorkflowManager(mock_sequencer)
        manager._storage_dir = self.workflow_dir
        
        with self.assertRaises(WorkflowPlanningError) as context:
            manager.start_workflow("test_errors", str(self.test_directory))
        
        # Error message should include sequencing errors
        error_msg = str(context.exception)
        self.assertIn("ContentType module not found", error_msg)
        self.assertIn("Circular dependency detected", error_msg)
    
    def test_module_execution_context_propagation(self):
        """Test proper context propagation to modules."""
        mock_sequencer = MockModuleSequencerFactory.create_standard_mock()
        manager = WorkflowManager(mock_sequencer)
        manager._storage_dir = self.workflow_dir
        
        # Create test files
        (self.test_directory / "doc1.adoc").write_text("= Doc 1\nContent")
        (self.test_directory / "doc2.adoc").write_text("= Doc 2\nContent")
        
        workflow = manager.start_workflow("test_context", str(self.test_directory))
        
        # Mock the _execute_module_with_context method directly
        # Note: We also mock save_to_disk to avoid Mock object serialization issues
        # when the test framework tries to serialize Mock objects to JSON state files.
        # This test focuses on context propagation, not disk persistence functionality.
        with patch.object(manager, '_execute_module_with_context') as mock_execute, \
             patch.object(workflow, 'save_to_disk') as mock_save:
            
            mock_execute.return_value = ExecutionResult(
                status="success",
                message="Processed successfully",
                files_processed=2,
                execution_time=0.1
            )
            
            # Execute next module
            result = manager.execute_next_module(workflow)
            
            # Verify module was called with proper context
            self.assertIsNotNone(result)
            self.assertEqual(result.status, "success")
            
            # Verify _execute_module_with_context was called with proper parameters
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args
            self.assertEqual(call_args[0][1], "DirectoryConfig")  # module name
            self.assertEqual(call_args[0][0], workflow)  # workflow state
    
    def test_directory_config_special_handling(self):
        """Test DirectoryConfig receives special handling."""
        mock_sequencer = MockModuleSequencerFactory.create_standard_mock()
        manager = WorkflowManager(mock_sequencer)
        manager._storage_dir = self.workflow_dir
        
        # Mock DirectoryConfig module with proper ADT interface
        mock_directory_config = Mock()
        mock_directory_config.execute.return_value = {
            "status": "success",
            "files_discovered": ["/test/doc1.adoc", "/test/doc2.adoc"],
            "config": {"source_dir": "/test", "output_dir": "/output"}
        }
        mock_directory_config._initialized = True  # Skip initialization
        mock_sequencer.available_modules["DirectoryConfig"] = mock_directory_config
        
        workflow = manager.start_workflow("test_dirconfig", str(self.test_directory))
        
        # Execute DirectoryConfig
        result = manager.execute_next_module(workflow)
        
        # Verify DirectoryConfig was executed with directory context
        mock_directory_config.execute.assert_called_once()
        
        # Verify workflow state updated with discovered files
        self.assertGreater(len(workflow.files_discovered), 0)


class TestCLICommandsComprehensive(unittest.TestCase):
    """Comprehensive CLI command testing following Chunk 4 patterns."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_directory = TestFixtureLoader.get_test_directory_fixture("simple_project")
        
        self.mock_sequencer = MockModuleSequencerFactory.create_standard_mock()
        self.manager = WorkflowManager(self.mock_sequencer)
        self.processor = UserJourneyProcessor(self.manager)
        
        # Configure workflow storage for testing
        self.workflow_dir = Path(self.temp_dir) / ".adt" / "workflows"
        self.workflow_dir.mkdir(parents=True)
        
        WorkflowState._default_storage_dir = self.workflow_dir
        self.manager._storage_dir = self.workflow_dir
    
    def tearDown(self):
        """Clean up test environment."""
        # Reset storage configuration
        WorkflowState._default_storage_dir = None
        shutil.rmtree(self.temp_dir)
    
    def test_start_command_validation_pattern(self):
        """Test start command follows validation pattern."""
        # Test missing arguments
        args = Mock(spec=[])  # No attributes
        
        result = self.processor.process_start_command(args)
        self.assertEqual(result, 1)  # Should fail validation
        
        # Test invalid directory
        args = Mock()
        args.name = "test_workflow"
        args.directory = "/nonexistent/path"
        
        result = self.processor.process_start_command(args)
        self.assertEqual(result, 1)  # Should fail validation
        
        # Test duplicate workflow
        args = Mock()
        args.name = "existing_workflow"
        args.directory = str(self.test_directory)
        
        # Create workflow first
        self.manager.start_workflow(args.name, args.directory)
        
        result = self.processor.process_start_command(args)
        self.assertEqual(result, 1)  # Should fail precondition check
    
    def test_start_command_success_feedback(self):
        """Test start command provides proper success feedback."""
        args = Mock()
        args.name = "success_workflow"
        args.directory = str(self.test_directory)
        
        # Capture output
        with patch('builtins.print') as mock_print:
            with patch('builtins.input', return_value='y'):  # Confirm file processing
                result = self.processor.process_start_command(args)
        
        self.assertEqual(result, 0)  # Success
        
        # Verify success feedback contains emojis and next steps
        output_calls = [str(call) for call in mock_print.call_args_list]
        output_text = ' '.join(output_calls)
        
        self.assertIn('✅', output_text)  # Success emoji
        self.assertIn('workflow', output_text.lower())  # Mentions workflow
    
    def test_status_command_rich_display(self):
        """Test status command provides rich visual display."""
        # Create workflow with mixed progress
        workflow_name = "status_test_workflow"
        
        workflow = self.manager.start_workflow(workflow_name, str(self.test_directory))
        workflow.mark_module_completed("DirectoryConfig", 
                                     ExecutionResult("success", "Done", files_processed=2))
        workflow.mark_module_failed("ContentType",
                                  ExecutionResult("error", "Failed", error_message="Test error"))
        workflow.save_to_disk()
        
        args = Mock()
        args.name = workflow_name
        
        # Capture output
        with patch('builtins.print') as mock_print:
            result = self.processor.process_status_command(args)
        
        self.assertEqual(result, 0)  # Success
        
        # Verify rich display elements
        output_calls = [str(call) for call in mock_print.call_args_list]
        output_text = ' '.join(output_calls)
        
        # Check for visual indicators
        self.assertIn('✅', output_text)  # Completed module
        self.assertIn('❌', output_text)  # Failed module  
        self.assertIn('⏸️', output_text)  # Pending module
        self.assertIn('%', output_text)   # Progress percentage
    
    def test_continue_command_error_handling(self):
        """Test continue command handles various error conditions."""
        # Test non-existent workflow
        args = Mock()
        args.name = "nonexistent"
        
        result = self.processor.process_continue_command(args)
        self.assertEqual(result, 1)  # Error
        
        # Test completed workflow
        workflow_name = "completed_workflow"
        workflow = self.manager.start_workflow(workflow_name, str(self.test_directory))
        
        # Mark all modules completed
        for module_name in workflow.modules.keys():
            workflow.mark_module_completed(module_name, ExecutionResult("success", "Done"))
        workflow.save_to_disk()
        
        args.name = workflow_name
        result = self.processor.process_continue_command(args)
        self.assertEqual(result, 0)  # Should handle gracefully but indicate completion
    
    def test_list_command_formatting(self):
        """Test list command provides properly formatted output."""
        # Create multiple workflows
        workflows = ["workflow1", "workflow2", "workflow3"]
        for i, wf_name in enumerate(workflows):
            wf = self.manager.start_workflow(wf_name, str(self.test_directory))
            if i % 2 == 0:  # Complete some modules in alternate workflows
                wf.mark_module_completed("DirectoryConfig", ExecutionResult("success", "Done"))
            wf.save_to_disk()
        
        args = Mock()
        
        # Capture output
        with patch('builtins.print') as mock_print:
            result = self.processor.process_list_command(args)
        
        self.assertEqual(result, 0)  # Success
        
        # Verify all workflows listed with proper formatting
        output_calls = [str(call) for call in mock_print.call_args_list]
        output_text = ' '.join(output_calls)
        
        for wf_name in workflows:
            self.assertIn(wf_name, output_text)
        
        # Check for visual indicators  
        self.assertIn('ℹ️', output_text)  # Info indicator (actual emoji used)


class TestScenarioTests(unittest.TestCase):
    """Scenario-based tests for complete workflow execution."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.simple_project = TestFixtureLoader.get_test_directory_fixture("simple_project")
        self.complex_project = TestFixtureLoader.get_test_directory_fixture("complex_project")
        
        self.workflow_dir = Path(self.temp_dir) / ".adt" / "workflows"
        self.workflow_dir.mkdir(parents=True)
        
        # Configure storage for testing
        WorkflowState._default_storage_dir = self.workflow_dir
    
    def tearDown(self):
        """Clean up test environment."""
        WorkflowState._default_storage_dir = None
        shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow_execution_simple(self):
        """Test complete workflow execution on simple project."""
        mock_sequencer = MockModuleSequencerFactory.create_standard_mock()
        manager = WorkflowManager(mock_sequencer)
        manager._storage_dir = self.workflow_dir
        
        workflow_name = "simple_complete"
        
        # Start workflow
        workflow = manager.start_workflow(workflow_name, str(self.simple_project))
        self.assertEqual(workflow.status, "active")
        
        # Execute all modules
        while workflow.get_next_module():
            next_module = workflow.get_next_module()
            
            # Mock successful execution
            result = ExecutionResult("success", f"Processed {next_module}",
                                   files_processed=2, execution_time=10.0)
            workflow.mark_module_completed(next_module, result)
        
        # Verify completion
        progress = workflow.get_progress_summary()
        self.assertEqual(progress.completion_percentage, 100.0)
        self.assertEqual(progress.completed_modules, 3)
    
    def test_interruption_and_resume_scenario(self):
        """Test workflow interruption and resume scenario."""
        mock_sequencer = MockModuleSequencerFactory.create_standard_mock()
        manager = WorkflowManager(mock_sequencer)
        manager._storage_dir = self.workflow_dir
        
        workflow_name = "interrupted_workflow"
        
        # Start and partially execute workflow
        workflow = manager.start_workflow(workflow_name, str(self.complex_project))
        
        # Complete first module
        workflow.mark_module_completed("DirectoryConfig", 
                                     ExecutionResult("success", "Config complete", files_processed=6))
        
        # Start second module but don't complete (simulating interruption)
        workflow.mark_module_started("ContentType")
        workflow.save_to_disk()
        
        # Simulate process restart - reload workflow
        reloaded_workflow = WorkflowState.load_from_disk(workflow_name)
        
        # Verify state preserved
        self.assertEqual(reloaded_workflow.modules["DirectoryConfig"].status, "completed")
        self.assertEqual(reloaded_workflow.modules["ContentType"].status, "running")
        self.assertEqual(reloaded_workflow.modules["CrossReference"].status, "pending")
        
        # Resume and complete
        reloaded_workflow.mark_module_completed("ContentType",
                                              ExecutionResult("success", "Content complete", files_processed=6))
        reloaded_workflow.mark_module_completed("CrossReference", 
                                              ExecutionResult("success", "Refs complete", files_processed=6))
        
        # Verify final completion
        progress = reloaded_workflow.get_progress_summary()
        self.assertEqual(progress.completion_percentage, 100.0)
    
    def test_module_failure_and_retry_scenario(self):
        """Test module failure and retry handling."""
        mock_sequencer = MockModuleSequencerFactory.create_standard_mock()
        manager = WorkflowManager(mock_sequencer)
        manager._storage_dir = self.workflow_dir
        
        workflow_name = "retry_workflow"
        
        workflow = manager.start_workflow(workflow_name, str(self.simple_project))
        
        # Complete DirectoryConfig
        workflow.mark_module_completed("DirectoryConfig",
                                     ExecutionResult("success", "Config complete"))
        
        # Fail ContentType multiple times
        for i in range(3):
            workflow.mark_module_failed("ContentType",
                                      ExecutionResult("error", f"Attempt {i+1} failed", 
                                                    error_message=f"Test error {i+1}"))
            self.assertEqual(workflow.modules["ContentType"].retry_count, i + 1)
        
        # Finally succeed
        workflow.mark_module_completed("ContentType",
                                     ExecutionResult("success", "Finally worked"))
        
        # Verify retry count reset and progress continues
        self.assertEqual(workflow.modules["ContentType"].retry_count, 0)
        self.assertEqual(workflow.modules["ContentType"].status, "completed")
        
        # Complete remaining module
        workflow.mark_module_completed("CrossReference",
                                     ExecutionResult("success", "Refs complete"))
        
        progress = workflow.get_progress_summary()
        self.assertEqual(progress.completion_percentage, 100.0)


class TestPerformanceValidation(unittest.TestCase):
    """Performance validation tests following Chunk 4 targets."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.workflow_dir = Path(self.temp_dir) / ".adt" / "workflows"
        self.workflow_dir.mkdir(parents=True)
        
        # Configure storage for testing
        WorkflowState._default_storage_dir = self.workflow_dir
    
    def tearDown(self):
        """Clean up test environment."""
        WorkflowState._default_storage_dir = None
        shutil.rmtree(self.temp_dir)
    
    def test_workflow_creation_performance(self):
        """Test workflow creation meets <1 second target."""
        mock_sequencer = MockModuleSequencerFactory.create_standard_mock()
        manager = WorkflowManager(mock_sequencer)
        manager._storage_dir = self.workflow_dir
        
        # Create test directory
        test_dir = self.workflow_dir.parent / "test_docs"
        test_dir.mkdir(exist_ok=True)
        
        start_time = time.time()
        workflow = manager.start_workflow("perf_test", str(test_dir))
        creation_time = time.time() - start_time
        
        self.assertLess(creation_time, 1.0, "Workflow creation took longer than 1 second")
        self.assertIsNotNone(workflow)
    
    def test_status_display_performance(self):
        """Test status display meets <0.5 second target."""
        # Create workflow with some progress
        modules = ["DirectoryConfig", "ContentType", "CrossReference"] 
        workflow = WorkflowState("perf_test", "/test/docs", modules)
        workflow.mark_module_completed("DirectoryConfig", ExecutionResult("success", "Done"))
        workflow.save_to_disk()
        
        start_time = time.time()
        progress = workflow.get_progress_summary()
        display_time = time.time() - start_time
        
        self.assertLess(display_time, 0.5, "Status display took longer than 0.5 seconds")
        self.assertIsNotNone(progress)
    
    def test_state_save_performance(self):
        """Test state save meets <0.1 second target."""
        modules = ["DirectoryConfig", "ContentType", "CrossReference"]
        workflow = WorkflowState("perf_test", "/test/docs", modules)
        
        # Add some data to make save more realistic
        workflow.files_discovered = [f"/test/doc{i}.adoc" for i in range(10)]
        workflow.mark_module_completed("DirectoryConfig", 
                                     ExecutionResult("success", "Done", files_processed=10))
        
        start_time = time.time()
        workflow.save_to_disk()
        save_time = time.time() - start_time
        
        self.assertLess(save_time, 0.1, "State save took longer than 0.1 seconds")


if __name__ == '__main__':
    unittest.main()
