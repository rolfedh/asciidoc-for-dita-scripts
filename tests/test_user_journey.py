"""
Test suite for UserJourney plugin.

This file tests the core functionality of the UserJourney workflow orchestration
system, including state persistence, workflow management, and CLI integration.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Import UserJourney components
from asciidoc_dita_toolkit.modules.user_journey import (
    WorkflowState, WorkflowManager, UserJourneyProcessor,
    ExecutionResult, WorkflowProgress, ModuleExecutionState,
    UserJourneyError, WorkflowError, WorkflowNotFoundError,
    WorkflowExistsError, WorkflowStateError, InvalidDirectoryError,
    WorkflowExecutionError, WorkflowPlanningError
)


class TestUserJourneyProcessor(unittest.TestCase):
    """Test UserJourneyProcessor CLI functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_directory = Path(self.temp_dir) / "test_docs"
        self.test_directory.mkdir(parents=True)

        # Create test .adoc files
        (self.test_directory / "doc1.adoc").write_text("= Document 1\nContent")
        (self.test_directory / "doc2.adoc").write_text("= Document 2\nContent")

        # Mock ModuleSequencer
        from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleState
        self.mock_sequencer = Mock()

        # Create properly configured mock resolution objects
        mock_directory_config = Mock()
        mock_directory_config.name = "DirectoryConfig"
        mock_directory_config.state = ModuleState.ENABLED

        mock_content_type = Mock()
        mock_content_type.name = "ContentType"
        mock_content_type.state = ModuleState.ENABLED

        self.mock_sequencer.sequence_modules.return_value = (
            [mock_directory_config, mock_content_type],
            []  # No errors
        )

        self.manager = WorkflowManager(self.mock_sequencer)
        self.processor = UserJourneyProcessor(self.manager)

        # Set up isolated storage directory
        self.workflow_dir = Path(self.temp_dir) / ".adt" / "workflows"
        self.workflow_dir.mkdir(parents=True)

        # Configure both WorkflowManager and WorkflowState to use test storage
        WorkflowManager.set_storage_directory(self.workflow_dir)

    def tearDown(self):
        """Clean up test environment."""
        # Reset storage directories
        WorkflowManager._storage_dir = None
        WorkflowState._default_storage_dir = None
        shutil.rmtree(self.temp_dir)

    def test_start_command_success(self):
        """Test successful workflow start command."""
        # Create mock args
        args = Mock()
        args.name = "test_workflow"
        args.directory = str(self.test_directory)

        # Mock user input for file confirmation
        with patch('builtins.input', return_value='y'):
            result = self.processor.process_start_command(args)

        self.assertEqual(result, 0)  # Success
        self.assertTrue(self.manager.workflow_exists("test_workflow"))

    def test_start_command_missing_args(self):
        """Test start command with missing arguments."""
        # Test missing name
        args = Mock()
        args.directory = str(self.test_directory)
        del args.name  # Remove name attribute

        result = self.processor.process_start_command(args)
        self.assertEqual(result, 1)  # Error

        # Test missing directory
        args = Mock()
        args.name = "test_workflow"
        del args.directory  # Remove directory attribute

        result = self.processor.process_start_command(args)
        self.assertEqual(result, 1)  # Error

    def test_start_command_existing_workflow(self):
        """Test start command when workflow already exists."""
        # Create workflow first
        self.manager.start_workflow("test_workflow", str(self.test_directory))

        # Try to create again
        args = Mock()
        args.name = "test_workflow"
        args.directory = str(self.test_directory)

        result = self.processor.process_start_command(args)
        self.assertEqual(result, 1)  # Error

    def test_start_command_invalid_directory(self):
        """Test start command with invalid directory."""
        args = Mock()
        args.name = "test_workflow"
        args.directory = "/nonexistent/directory"

        result = self.processor.process_start_command(args)
        self.assertEqual(result, 1)  # Error

    def test_resume_command_success(self):
        """Test successful workflow resume command."""
        # Create workflow first
        workflow = self.manager.start_workflow("test_workflow", str(self.test_directory))

        # Resume it
        args = Mock()
        args.name = "test_workflow"

        result = self.processor.process_resume_command(args)
        self.assertEqual(result, 0)  # Success

    def test_resume_command_not_found(self):
        """Test resume command with non-existent workflow."""
        args = Mock()
        args.name = "nonexistent_workflow"

        result = self.processor.process_resume_command(args)
        self.assertEqual(result, 1)  # Error

    def test_continue_command_success(self):
        """Test successful continue command."""
        # Create workflow
        workflow = self.manager.start_workflow("test_workflow", str(self.test_directory))

        # Mock successful module execution
        with patch.object(self.manager, 'execute_next_module') as mock_execute:
            mock_execute.return_value = ExecutionResult(
                status="success",
                message="Module completed",
                files_processed=2,
                next_action="Run next module"
            )

            args = Mock()
            args.name = "test_workflow"

            result = self.processor.process_continue_command(args)
            self.assertEqual(result, 0)  # Success
            mock_execute.assert_called_once()

    def test_continue_command_completed_workflow(self):
        """Test continue command on already completed workflow."""
        # Create and complete workflow
        workflow = self.manager.start_workflow("test_workflow", str(self.test_directory))

        # Mark all modules as completed
        for module_name in workflow.modules:
            result = ExecutionResult("success", "Done", files_processed=1)
            workflow.mark_module_completed(module_name, result)
        workflow.save_to_disk()

        args = Mock()
        args.name = "test_workflow"

        result = self.processor.process_continue_command(args)
        self.assertEqual(result, 0)  # Success (but already completed)

    def test_status_command_specific_workflow(self):
        """Test status command for specific workflow."""
        # Create workflow
        workflow = self.manager.start_workflow("test_workflow", str(self.test_directory))

        args = Mock()
        args.name = "test_workflow"

        result = self.processor.process_status_command(args)
        self.assertEqual(result, 0)  # Success

    def test_status_command_all_workflows(self):
        """Test status command for all workflows."""
        # Create multiple workflows
        self.manager.start_workflow("workflow1", str(self.test_directory))
        self.manager.start_workflow("workflow2", str(self.test_directory))

        args = Mock()
        del args.name  # No specific workflow

        result = self.processor.process_status_command(args)
        self.assertEqual(result, 0)  # Success

    def test_list_command(self):
        """Test list command."""
        # Create workflow
        self.manager.start_workflow("test_workflow", str(self.test_directory))

        args = Mock()

        result = self.processor.process_list_command(args)
        self.assertEqual(result, 0)  # Success

    def test_list_command_no_workflows(self):
        """Test list command with no workflows."""
        args = Mock()

        result = self.processor.process_list_command(args)
        self.assertEqual(result, 0)  # Success (but empty)

    def test_cleanup_command_specific_workflow(self):
        """Test cleanup command for specific workflow."""
        # Create workflow
        self.manager.start_workflow("test_workflow", str(self.test_directory))

        # Mock user confirmation
        with patch('builtins.input', return_value='y'):
            args = Mock()
            args.name = "test_workflow"

            result = self.processor.process_cleanup_command(args)
            self.assertEqual(result, 0)  # Success

            # Verify workflow was deleted
            self.assertFalse(self.manager.workflow_exists("test_workflow"))

    def test_cleanup_command_cancelled(self):
        """Test cleanup command when user cancels."""
        # Create workflow
        self.manager.start_workflow("test_workflow", str(self.test_directory))

        # Mock user cancellation
        with patch('builtins.input', return_value='n'):
            args = Mock()
            args.name = "test_workflow"

            result = self.processor.process_cleanup_command(args)
            self.assertEqual(result, 0)  # Success (but cancelled)

            # Verify workflow still exists
            self.assertTrue(self.manager.workflow_exists("test_workflow"))

    def test_cleanup_command_completed_workflows(self):
        """Test cleanup of completed workflows."""
        # Create and complete workflow
        workflow = self.manager.start_workflow("completed_workflow", str(self.test_directory))
        for module_name in workflow.modules:
            result = ExecutionResult("success", "Done", files_processed=1)
            workflow.mark_module_completed(module_name, result)
        workflow.save_to_disk()

        # Create incomplete workflow
        self.manager.start_workflow("incomplete_workflow", str(self.test_directory))

        # Mock user confirmation
        with patch('builtins.input', return_value='y'):
            args = Mock()
            args.completed = True
            del args.name  # No specific workflow
            del args.all   # Not all workflows

            result = self.processor.process_cleanup_command(args)
            self.assertEqual(result, 0)  # Success

            # Verify only completed workflow was deleted
            self.assertFalse(self.manager.workflow_exists("completed_workflow"))
            self.assertTrue(self.manager.workflow_exists("incomplete_workflow"))


class TestWorkflowState(unittest.TestCase):
    """Test WorkflowState class functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_directory = Path(self.temp_dir) / "test_docs"
        self.test_directory.mkdir(parents=True)

        # Create test .adoc files
        (self.test_directory / "doc1.adoc").write_text("= Document 1\nContent")
        (self.test_directory / "doc2.adoc").write_text("= Document 2\nContent")

        self.test_modules = ["DirectoryConfig", "ContentType", "EntityReference"]

        # Set up isolated storage directory
        self.workflow_dir = Path(self.temp_dir) / ".adt" / "workflows"
        self.workflow_dir.mkdir(parents=True)

        # Configure WorkflowState to use test storage
        WorkflowState._default_storage_dir = self.workflow_dir

    def tearDown(self):
        """Clean up test environment."""
        # Reset storage directory
        WorkflowState._default_storage_dir = None
        shutil.rmtree(self.temp_dir)

    def test_workflow_initialization(self):
        """Test basic workflow state initialization."""
        workflow = WorkflowState("test_workflow", str(self.test_directory), self.test_modules)

        self.assertEqual(workflow.name, "test_workflow")
        self.assertEqual(workflow.directory, self.test_directory)
        self.assertEqual(workflow.status, "active")
        self.assertEqual(len(workflow.modules), 3)

        # Check all modules are initialized as pending
        for module_name in self.test_modules:
            self.assertIn(module_name, workflow.modules)
            self.assertEqual(workflow.modules[module_name].status, "pending")

    def test_module_state_transitions(self):
        """Test module state transitions."""
        workflow = WorkflowState("test_workflow", str(self.test_directory), self.test_modules)

        # Test marking module as started
        workflow.mark_module_started("DirectoryConfig")
        state = workflow.modules["DirectoryConfig"]
        self.assertEqual(state.status, "running")
        self.assertIsNotNone(state.started_at)

        # Test marking module as completed
        result = ExecutionResult("success", "Completed successfully", files_processed=2, files_modified=1)
        workflow.mark_module_completed("DirectoryConfig", result)

        state = workflow.modules["DirectoryConfig"]
        self.assertEqual(state.status, "completed")
        self.assertEqual(state.files_processed, 2)
        self.assertEqual(state.files_modified, 1)
        self.assertIsNotNone(state.completed_at)

        # Test marking module as failed
        workflow.mark_module_failed("ContentType", "Test error")
        failed_state = workflow.modules["ContentType"]
        self.assertEqual(failed_state.status, "failed")
        self.assertEqual(failed_state.error_message, "Test error")
        self.assertEqual(failed_state.retry_count, 1)

    def test_get_next_module(self):
        """Test getting next module in sequence."""
        workflow = WorkflowState("test_workflow", str(self.test_directory), self.test_modules)

        # Should return first module initially
        next_module = workflow.get_next_module()
        self.assertEqual(next_module, "DirectoryConfig")

        # Mark first module as completed
        result = ExecutionResult("success", "Completed")
        workflow.mark_module_completed("DirectoryConfig", result)

        # Should return second module
        next_module = workflow.get_next_module()
        self.assertEqual(next_module, "ContentType")

        # Complete all modules
        workflow.mark_module_completed("ContentType", result)
        workflow.mark_module_completed("EntityReference", result)

        # Should return None when all complete
        next_module = workflow.get_next_module()
        self.assertIsNone(next_module)

    def test_progress_summary(self):
        """Test progress summary calculation."""
        workflow = WorkflowState("test_workflow", str(self.test_directory), self.test_modules)

        progress = workflow.get_progress_summary()
        self.assertEqual(progress.total_modules, 3)
        self.assertEqual(progress.completed_modules, 0)
        self.assertEqual(progress.pending_modules, 3)
        self.assertEqual(progress.completion_percentage, 0)

        # Complete one module
        result = ExecutionResult("success", "Done", files_processed=5)
        workflow.mark_module_completed("DirectoryConfig", result)

        progress = workflow.get_progress_summary()
        self.assertEqual(progress.completed_modules, 1)
        self.assertEqual(progress.pending_modules, 2)
        self.assertAlmostEqual(progress.completion_percentage, 33.33, places=1)
        self.assertEqual(progress.processed_files, 5)

    @patch('asciidoc_dita_toolkit.modules.user_journey.datetime')
    def test_serialization(self, mock_datetime):
        """Test workflow state serialization and deserialization."""
        # Mock datetime for consistent testing
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"

        workflow = WorkflowState("test_workflow", str(self.test_directory), self.test_modules)

        # Convert to dict
        data = workflow.to_dict()
        self.assertEqual(data["name"], "test_workflow")
        self.assertIn("modules", data)
        self.assertIn("metadata", data)

        # Recreate from dict
        restored_workflow = WorkflowState.from_dict(data)
        self.assertEqual(restored_workflow.name, workflow.name)
        self.assertEqual(restored_workflow.directory, workflow.directory)
        self.assertEqual(len(restored_workflow.modules), len(workflow.modules))

    def test_persistence(self):
        """Test saving and loading workflow state."""
        workflow = WorkflowState("test_workflow", str(self.test_directory), self.test_modules)

        # Mark some progress
        result = ExecutionResult("success", "Done", files_processed=2)
        workflow.mark_module_completed("DirectoryConfig", result)

        # Save to disk
        workflow.save_to_disk()

        # Load from disk
        loaded_workflow = WorkflowState.load_from_disk("test_workflow")

        # Verify state was preserved
        self.assertEqual(loaded_workflow.name, workflow.name)
        self.assertEqual(loaded_workflow.directory, workflow.directory)
        self.assertEqual(
            loaded_workflow.modules["DirectoryConfig"].status,
            "completed"
        )
        self.assertEqual(
            loaded_workflow.modules["DirectoryConfig"].files_processed,
            2
        )


class TestWorkflowManager(unittest.TestCase):
    """Test WorkflowManager functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_directory = Path(self.temp_dir) / "test_docs"
        self.test_directory.mkdir(parents=True)

        # Create test .adoc files
        (self.test_directory / "doc1.adoc").write_text("= Document 1")

        # Mock ModuleSequencer
        from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleState
        self.mock_sequencer = Mock()

        # Create properly configured mock resolution objects
        mock_directory_config = Mock()
        mock_directory_config.name = "DirectoryConfig"
        mock_directory_config.state = ModuleState.ENABLED

        mock_content_type = Mock()
        mock_content_type.name = "ContentType"
        mock_content_type.state = ModuleState.ENABLED

        self.mock_sequencer.sequence_modules.return_value = (
            [mock_directory_config, mock_content_type],
            []  # No errors
        )

        self.manager = WorkflowManager(self.mock_sequencer)

        # Set up isolated storage directory
        self.workflow_dir = Path(self.temp_dir) / ".adt" / "workflows"
        self.workflow_dir.mkdir(parents=True)

        # Configure both WorkflowManager and WorkflowState to use test storage
        WorkflowManager.set_storage_directory(self.workflow_dir)

    def tearDown(self):
        """Clean up test environment."""
        # Reset storage directories
        WorkflowManager._storage_dir = None
        WorkflowState._default_storage_dir = None
        shutil.rmtree(self.temp_dir)

    def test_start_workflow(self):
        """Test starting a new workflow."""
        workflow = self.manager.start_workflow("test_workflow", str(self.test_directory))

        self.assertEqual(workflow.name, "test_workflow")
        self.assertEqual(workflow.directory, self.test_directory)
        self.assertEqual(workflow.status, "active")
        self.assertIn("DirectoryConfig", workflow.modules)
        self.assertIn("ContentType", workflow.modules)

    def test_workflow_exists_check(self):
        """Test workflow existence checking."""
        # Initially doesn't exist
        self.assertFalse(self.manager.workflow_exists("test_workflow"))

        # Create workflow
        workflow = self.manager.start_workflow("test_workflow", str(self.test_directory))

        # Now it should exist
        self.assertTrue(self.manager.workflow_exists("test_workflow"))

    def test_duplicate_workflow_error(self):
        """Test error when creating duplicate workflow."""
        # Create first workflow
        self.manager.start_workflow("test_workflow", str(self.test_directory))

        # Try to create duplicate
        with self.assertRaises(WorkflowExistsError):
            self.manager.start_workflow("test_workflow", str(self.test_directory))

    def test_invalid_directory_error(self):
        """Test error for invalid directory."""
        invalid_dir = str(Path(self.temp_dir) / "nonexistent")

        with self.assertRaises(InvalidDirectoryError):
            self.manager.start_workflow("test_workflow", invalid_dir)

    def test_get_planned_modules(self):
        """Test getting planned modules from sequencer."""
        modules = self.manager.get_planned_modules()
        self.assertEqual(modules, ["DirectoryConfig", "ContentType"])

    def test_module_sequencing_error(self):
        """Test handling of module sequencing errors."""
        self.mock_sequencer.sequence_modules.return_value = ([], ["Error in sequencing"])

        with self.assertRaises(WorkflowPlanningError):
            self.manager.get_planned_modules()


class TestUserJourneyModule(unittest.TestCase):
    """Test UserJourney ADTModule wrapper."""

    def setUp(self):
        """Set up test environment."""
        from asciidoc_dita_toolkit.modules.user_journey import UserJourneyModule
        self.module = UserJourneyModule()

    def test_module_properties(self):
        """Test module basic properties."""
        self.assertEqual(self.module.name, "UserJourney")
        self.assertEqual(self.module.version, "1.0.0")
        self.assertEqual(self.module.dependencies, ["DirectoryConfig"])

    def test_module_initialization(self):
        """Test module initialization."""
        with patch('asciidoc_dita_toolkit.modules.user_journey.WorkflowManager') as mock_manager:
            with patch('asciidoc_dita_toolkit.modules.user_journey.UserJourneyProcessor') as mock_processor:
                result = self.module.initialize()

                self.assertEqual(result["status"], "success")
                self.assertIn("message", result)
                mock_processor.assert_called_once()

    def test_module_execution(self):
        """Test module execution (compatibility mode)."""
        # Initialize first
        with patch('asciidoc_dita_toolkit.modules.user_journey.WorkflowManager'):
            with patch('asciidoc_dita_toolkit.modules.user_journey.UserJourneyProcessor'):
                self.module.initialize()

        # Test execution
        result = self.module.execute("dummy_file.adoc")

        # UserJourney returns "skipped" status because it's a CLI orchestrator
        self.assertIn(result["status"], ["info", "success", "skipped"])
        # UserJourney doesn't process files in normal execution mode
        self.assertFalse(result.get("modified", True))


class TestExceptions(unittest.TestCase):
    """Test UserJourney exception classes."""

    def test_exception_hierarchy(self):
        """Test exception class hierarchy."""
        self.assertTrue(issubclass(WorkflowError, UserJourneyError))
        self.assertTrue(issubclass(WorkflowNotFoundError, WorkflowError))
        self.assertTrue(issubclass(WorkflowExistsError, WorkflowError))
        self.assertTrue(issubclass(WorkflowStateError, WorkflowError))
        self.assertTrue(issubclass(WorkflowExecutionError, WorkflowError))
        self.assertTrue(issubclass(WorkflowPlanningError, WorkflowError))
        self.assertTrue(issubclass(InvalidDirectoryError, UserJourneyError))

    def test_exception_messages(self):
        """Test exception message handling."""
        error = WorkflowNotFoundError("Test workflow not found")
        self.assertEqual(str(error), "Test workflow not found")

        base_error = UserJourneyError("Base error")
        self.assertEqual(str(base_error), "Base error")


if __name__ == '__main__':
    # Set up test environment
    import sys
    from pathlib import Path

    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # Run tests
    unittest.main(verbosity=2)
