"""
UserJourney Plugin for ADT - Workflow Orchestration System

This plugin provides opinionated workflow orchestration for technical writers
processing large document sets through multiple ADT modules. Unlike other ADT
plugins that process content, UserJourney orchestrates other plugins.

Key Features:
- Persistent workflow state management across sessions
- Module execution orchestration via ModuleSequencer
- CLI command interface with rich user feedback
- Progress visualization and interruption recovery
- DirectoryConfig integration for scoped file discovery

Architecture:
UserJourney is a CLI-first orchestrator that uses ModuleSequencer to execute
other modules but is not itself executed by ModuleSequencer.
"""

import json
import logging
import shutil
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

# Import from ADT core
try:
    from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleSequencer, ModuleState, ModuleResolution, ADTModule
except ImportError as e:
    raise ImportError(
        f"Failed to import from asciidoc_dita_toolkit.adt_core.module_sequencer: {e}. "
        f"This is required for UserJourney plugin to function properly."
    )


# ============================================================================
# Exception Classes
# ============================================================================

class UserJourneyError(Exception):
    """Base exception for UserJourney plugin errors."""
    pass


class WorkflowError(UserJourneyError):
    """Base exception for workflow-related errors."""
    pass


class WorkflowNotFoundError(WorkflowError):
    """Raised when a workflow cannot be found."""
    pass


class WorkflowExistsError(WorkflowError):
    """Raised when trying to create a workflow that already exists."""
    pass


class WorkflowStateError(WorkflowError):
    """Raised when workflow state is corrupted or invalid."""
    pass


class WorkflowExecutionError(WorkflowError):
    """Raised when workflow execution fails."""
    pass


class WorkflowPlanningError(WorkflowError):
    """Raised when workflow planning fails (e.g., module sequencing issues)."""
    pass


class InvalidDirectoryError(UserJourneyError):
    """Raised when directory path is invalid."""
    pass


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class ModuleExecutionState:
    """State tracking for individual module execution."""
    status: str  # pending, running, completed, failed, skipped
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    files_processed: int = 0
    files_modified: int = 0
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    user_interaction_required: bool = False


@dataclass
class ExecutionResult:
    """Result of module or workflow execution."""
    status: str  # success, failed, completed
    message: str
    files_processed: int = 0
    files_modified: int = 0
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    next_action: Optional[str] = None
    module_name: Optional[str] = None


@dataclass
class WorkflowProgress:
    """Progress summary for a workflow."""
    total_modules: int
    completed_modules: int
    failed_modules: int
    pending_modules: int
    current_module: Optional[str]
    total_files: int
    processed_files: int
    completion_percentage: float
    estimated_remaining_time: Optional[float] = None


# ============================================================================
# Core Classes
# ============================================================================

class WorkflowState:
    """
    Persistent state management for workflows across sessions.

    Handles atomic persistence, corruption recovery, and state transitions.
    Integrates with DirectoryConfig for file discovery.
    """

    # Class-level storage configuration for testing
    _default_storage_dir: Optional[Path] = None

    def __init__(self, name: str, directory: str, modules: List[str]):
        """
        Initialize workflow state.

        Args:
            name: Unique workflow identifier
            directory: Target directory containing .adoc files
            modules: List of module names to execute in order
        """
        self.name = name
        self.directory = Path(directory).resolve()
        self.created = datetime.now().isoformat()
        self.last_activity = self.created
        self.status = "active"  # active, completed, failed, paused
        self.modules = self._initialize_module_states(modules)
        self.files_discovered: List[str] = []
        self.directory_config: Optional[Dict] = None
        self.metadata = {
            "version": "1.0",
            "adt_version": self._get_adt_version()
        }

        # Initialize file discovery and directory config
        self._refresh_file_discovery()
        self._load_directory_config()

    def _get_adt_version(self) -> str:
        """Get ADT version from package metadata."""
        try:
            # Try modern importlib.metadata first
            from importlib.metadata import version
            return version("asciidoc-dita-toolkit")
        except ImportError:
            # Fallback to pkg_resources for older Python versions
            try:
                import pkg_resources
                return pkg_resources.get_distribution("asciidoc-dita-toolkit").version
            except Exception:
                pass
        except Exception:
            pass

        # Final fallback version if package not installed or detection fails
        return "2.0.0"

    def _initialize_module_states(self, modules: List[str]) -> Dict[str, ModuleExecutionState]:
        """Create state tracking for each module with detailed metrics."""
        # Use OrderedDict to preserve execution order
        return OrderedDict([
            (module, ModuleExecutionState(status="pending"))
            for module in modules
        ])

    def _refresh_file_discovery(self) -> None:
        """Discover .adoc files using DirectoryConfig if available."""
        try:
            # Try DirectoryConfig first (it's required now)
            from asciidoc_dita_toolkit.modules.directory_config import (
                load_directory_config, get_filtered_adoc_files
            )
            from asciidoc_dita_toolkit.asciidoc_dita.file_utils import find_adoc_files

            config = load_directory_config()
            if config:
                self.files_discovered = get_filtered_adoc_files(
                    str(self.directory), config, find_adoc_files
                )
            else:
                # Fallback to simple discovery
                self.files_discovered = [
                    str(f) for f in self.directory.rglob("*.adoc")
                ]
        except (ImportError, Exception) as e:
            # Fallback if DirectoryConfig not available or fails
            logging.debug(f"DirectoryConfig not available, using simple discovery: {e}")
            self.files_discovered = [
                str(f) for f in self.directory.rglob("*.adoc")
            ]

    def _load_directory_config(self) -> None:
        """Load DirectoryConfig for workflow context."""
        try:
            from asciidoc_dita_toolkit.modules.directory_config import load_directory_config
            self.directory_config = load_directory_config()
        except (ImportError, Exception) as e:
            logging.debug(f"DirectoryConfig not available: {e}")
            self.directory_config = None

    def get_storage_path(self) -> Path:
        """Get storage path with proper directory creation."""
        if self._default_storage_dir is not None:
            storage_dir = self._default_storage_dir
        else:
            storage_dir = Path.home() / ".adt" / "workflows"
        storage_dir.mkdir(parents=True, exist_ok=True)
        return storage_dir / f"{self.name}.json"

    def get_next_module(self) -> Optional[str]:
        """Get the next module to execute based on dependency order."""
        for module_name, module_state in self.modules.items():
            if module_state.status == "pending":
                return module_name
        return None

    def mark_module_started(self, module_name: str) -> None:
        """Mark module as started with timestamp."""
        if module_name in self.modules:
            state = self.modules[module_name]
            state.status = "running"
            state.started_at = datetime.now().isoformat()
            self.last_activity = state.started_at

    def mark_module_completed(self, module_name: str, result: ExecutionResult) -> None:
        """Mark module as completed with execution results."""
        if module_name in self.modules:
            state = self.modules[module_name]
            state.status = "completed"
            state.completed_at = datetime.now().isoformat()
            state.files_processed = result.files_processed
            state.files_modified = result.files_modified
            state.execution_time = result.execution_time
            state.error_message = None  # Clear any previous errors
            state.retry_count = 0  # Reset retry count on success
            self.last_activity = state.completed_at

    def mark_module_failed(self, module_name: str, error_message: str) -> None:
        """Mark module as failed with error details."""
        if module_name in self.modules:
            state = self.modules[module_name]
            state.status = "failed"
            state.completed_at = datetime.now().isoformat()
            state.error_message = error_message
            state.retry_count += 1
            self.last_activity = state.completed_at

    def get_progress_summary(self) -> WorkflowProgress:
        """Get current progress summary."""
        total = len(self.modules)
        completed = sum(1 for s in self.modules.values() if s.status == "completed")
        failed = sum(1 for s in self.modules.values() if s.status == "failed")
        pending = sum(1 for s in self.modules.values() if s.status in ["pending", "running"])

        processed_files = sum(s.files_processed for s in self.modules.values())
        completion_pct = (completed / total * 100) if total > 0 else 0

        return WorkflowProgress(
            total_modules=total,
            completed_modules=completed,
            failed_modules=failed,
            pending_modules=pending,
            current_module=self.get_next_module(),
            total_files=len(self.files_discovered),
            processed_files=processed_files,
            completion_percentage=completion_pct
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow state to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "directory": str(self.directory),
            "created": self.created,
            "last_activity": self.last_activity,
            "status": self.status,
            "module_order": list(self.modules.keys()),  # Preserve module execution order
            "modules": {
                name: asdict(state) for name, state in self.modules.items()
            },
            "files_discovered": self.files_discovered,
            "directory_config": self.directory_config,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowState':
        """Create WorkflowState from dictionary (loaded from JSON)."""
        # Extract module names from the data
        module_names = list(data.get("modules", {}).keys())

        # Create instance with basic info
        workflow = cls(
            name=data["name"],
            directory=data["directory"],
            modules=module_names
        )

        # Restore state
        workflow.created = data.get("created", workflow.created)
        workflow.last_activity = data.get("last_activity", workflow.last_activity)
        workflow.status = data.get("status", "active")
        workflow.files_discovered = data.get("files_discovered", [])
        workflow.directory_config = data.get("directory_config")
        workflow.metadata = data.get("metadata", workflow.metadata)

        # Restore module states in correct order
        modules_data = data.get("modules", {})
        module_order = data.get("module_order", list(modules_data.keys()))  # Use saved order if available

        workflow.modules = OrderedDict()  # Initialize as OrderedDict
        for module_name in module_order:
            if module_name in modules_data:
                workflow.modules[module_name] = ModuleExecutionState(**modules_data[module_name])

        return workflow

    def save_to_disk(self) -> None:
        """Save workflow state with atomic write and error recovery."""
        self.last_activity = datetime.now().isoformat()
        storage_path = self.get_storage_path()

        # Atomic write pattern: temp file → rename
        temp_path = storage_path.with_suffix('.tmp')
        backup_path = storage_path.with_suffix('.backup')

        # Track if backup already existed
        backup_existed = backup_path.exists()

        try:
            # Create backup of existing state (only if current file exists)
            if storage_path.exists():
                shutil.copy2(storage_path, backup_path)

            # Write to temp file
            with open(temp_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)  # Removed sort_keys=True to preserve module order

            # Atomic rename
            temp_path.rename(storage_path)

            # Clean up any backup on success (whether it existed before or was created now)
            if backup_path.exists():
                backup_path.unlink()

        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass
            # Restore from backup if available and main file is missing
            if backup_path.exists() and not storage_path.exists():
                shutil.copy2(backup_path, storage_path)
            raise WorkflowStateError(f"Failed to save workflow state: {e}")

    @classmethod
    def load_from_disk(cls, name: str, storage_dir: Optional[Path] = None) -> 'WorkflowState':
        """Load workflow state with validation and migration."""
        if storage_dir is None:
            if cls._default_storage_dir is not None:
                storage_dir = cls._default_storage_dir
            else:
                storage_dir = Path.home() / ".adt" / "workflows"
        storage_path = storage_dir / f"{name}.json"
        if not storage_path.exists():
            raise WorkflowNotFoundError(f"Workflow '{name}' not found")

        try:
            with open(storage_path) as f:
                data = json.load(f)

            # Validate and migrate data format if needed
            data = cls._migrate_state_format(data)
            cls._validate_state_data(data)

            return cls.from_dict(data)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Try backup recovery
            backup_path = storage_path.with_suffix('.backup')
            if backup_path.exists():
                try:
                    with open(backup_path) as f:
                        data = json.load(f)
                    return cls.from_dict(data)
                except Exception:
                    pass

            raise WorkflowStateError(f"Corrupted workflow state for '{name}': {e}")

    @staticmethod
    def _migrate_state_format(data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate old state formats to current version."""
        # Handle version migration here
        current_version = data.get("metadata", {}).get("version", "1.0")
        if current_version == "1.0":
            # No migration needed for current version
            pass
        return data

    @staticmethod
    def _validate_state_data(data: Dict[str, Any]) -> None:
        """Validate state data structure."""
        required_fields = ["name", "directory", "modules"]
        for field in required_fields:
            if field not in data:
                raise WorkflowStateError(f"Missing required field: {field}")


class WorkflowManager:
    """
    Orchestrate module execution via ModuleSequencer.

    Handles workflow lifecycle, module execution, and integration with
    the existing ADT module system.
    """

    # Storage configuration for testing
    _storage_dir: Optional[Path] = None

    def __init__(self, module_sequencer: Optional[ModuleSequencer] = None):
        """
        Initialize WorkflowManager.

        Args:
            module_sequencer: Optional pre-configured ModuleSequencer instance
        """
        if module_sequencer is None:
            self.sequencer = ModuleSequencer()
            # Load configurations and discover modules
            try:
                self.sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')
                self.sequencer.discover_modules()
            except Exception as e:
                # For help display and other non-critical operations, just discover modules without config
                logging.debug(f"Could not load full configuration, using discovery only: {e}")
                try:
                    self.sequencer.discover_modules()
                except Exception as discovery_error:
                    logging.warning(f"Failed to initialize ModuleSequencer: {discovery_error}")
        else:
            self.sequencer = module_sequencer

        # If we have a custom storage directory, apply it to WorkflowState as well
        if self._storage_dir is not None:
            WorkflowState._default_storage_dir = self._storage_dir

    @classmethod
    def set_storage_directory(cls, storage_dir: Path) -> None:
        """Set storage directory for testing or custom deployments."""
        cls._storage_dir = storage_dir
        WorkflowState._default_storage_dir = storage_dir

    def start_workflow(self, name: str, directory: str) -> WorkflowState:
        """
        Create and start a new workflow.

        Args:
            name: Unique workflow identifier
            directory: Target directory path

        Returns:
            WorkflowState: Initialized workflow state

        Raises:
            WorkflowExistsError: If workflow already exists
            InvalidDirectoryError: If directory is invalid
            WorkflowPlanningError: If module planning fails
        """
        # Check if workflow already exists
        if self.workflow_exists(name):
            raise WorkflowExistsError(f"Workflow '{name}' already exists")

        # Validate directory
        directory_path = Path(directory).resolve()
        if not directory_path.exists():
            raise InvalidDirectoryError(f"Directory '{directory_path}' not found")
        if not directory_path.is_dir():
            raise InvalidDirectoryError(f"'{directory_path}' is not a directory")

        # Get planned module sequence
        planned_modules = self.get_planned_modules()

        # Create workflow state
        workflow = WorkflowState(name, str(directory_path), planned_modules)
        workflow.save_to_disk()

        return workflow

    def resume_workflow(self, name: str) -> WorkflowState:
        """
        Load and resume an existing workflow.

        Args:
            name: Workflow identifier

        Returns:
            WorkflowState: Loaded workflow state

        Raises:
            WorkflowNotFoundError: If workflow doesn't exist
        """
        return WorkflowState.load_from_disk(name, self._storage_dir)

    def workflow_exists(self, name: str) -> bool:
        """Check if a workflow exists."""
        if self._storage_dir is not None:
            storage_path = self._storage_dir / f"{name}.json"
        else:
            storage_path = Path.home() / ".adt" / "workflows" / f"{name}.json"
        return storage_path.exists()

    def list_available_workflows(self) -> List[str]:
        """List all available workflow names."""
        if self._storage_dir is not None:
            workflow_dir = self._storage_dir
        else:
            workflow_dir = Path.home() / ".adt" / "workflows"
        if not workflow_dir.exists():
            return []

        workflow_files = workflow_dir.glob("*.json")
        return [f.stem for f in workflow_files if f.suffix == ".json"]

    def get_planned_modules(self) -> List[str]:
        """Get module execution order from ModuleSequencer."""
        try:
            resolutions, errors = self.sequencer.sequence_modules()
            if errors:
                raise WorkflowPlanningError(f"Module sequencing failed: {errors}")

            # Filter to enabled modules in dependency order
            enabled_modules = [
                r.name for r in resolutions
                if r.state == ModuleState.ENABLED
            ]

            # Verify DirectoryConfig is first (it's required now)
            if enabled_modules and enabled_modules[0] != "DirectoryConfig":
                raise WorkflowPlanningError(
                    "DirectoryConfig must be the first module in the sequence"
                )

            return enabled_modules

        except Exception as e:
            raise WorkflowPlanningError(f"Failed to determine module sequence: {e}")

    def execute_next_module(self, workflow: WorkflowState) -> ExecutionResult:
        """
        Execute the next pending module in dependency order.

        Args:
            workflow: Current workflow state

        Returns:
            ExecutionResult: Execution outcome

        Raises:
            WorkflowExecutionError: If module execution fails
        """
        next_module = workflow.get_next_module()
        if not next_module:
            return ExecutionResult(
                status="completed",
                message="All modules completed"
            )

        # Update workflow state
        workflow.mark_module_started(next_module)
        workflow.save_to_disk()

        try:
            # Execute module with full context
            result = self._execute_module_with_context(workflow, next_module)

            # Check result status and update workflow state appropriately
            if result.status == "failed":
                workflow.mark_module_failed(next_module, result.error_message or "Module execution failed")
                workflow.save_to_disk()
                raise WorkflowExecutionError(f"Module {next_module} failed: {result.error_message}")
            else:
                # Update workflow state with successful results
                workflow.mark_module_completed(next_module, result)
                workflow.save_to_disk()

            return ExecutionResult(
                status="success",
                message=f"{next_module} completed successfully",
                files_processed=result.files_processed,
                next_action=self._get_next_action(workflow)
            )

        except WorkflowExecutionError:
            # Re-raise WorkflowExecutionError (already handled above)
            raise
        except Exception as e:
            # Handle other unexpected exceptions
            workflow.mark_module_failed(next_module, str(e))
            workflow.save_to_disk()
            raise WorkflowExecutionError(f"Module {next_module} failed: {e}")

    def _execute_module_with_context(self, workflow: WorkflowState, module_name: str) -> ExecutionResult:
        """Execute a specific module with full workflow context."""
        try:
            # Build execution context from workflow state
            execution_context = {
                "directory": str(workflow.directory),
                "recursive": True,
                "files": workflow.files_discovered,
                "workflow_name": workflow.name,
                "workflow_state": workflow.to_dict(),
                "directory_config": workflow.directory_config
            }

            # Special handling for DirectoryConfig (interactive)
            if module_name == "DirectoryConfig":
                # DirectoryConfig may update the file discovery
                result = self._execute_directory_config(workflow, execution_context)

                # Refresh file discovery after DirectoryConfig
                workflow._refresh_file_discovery()
                workflow._load_directory_config()

                return result
            else:
                # Standard module execution
                return self._execute_standard_module(module_name, execution_context)

        except Exception as e:
            return ExecutionResult(
                status="failed",
                error_message=str(e),
                module_name=module_name
            )

    def _execute_directory_config(self, workflow: WorkflowState, context: Dict[str, Any]) -> ExecutionResult:
        """Execute DirectoryConfig module with special handling."""
        from datetime import datetime

        start_time = datetime.now()

        try:
            # Get DirectoryConfig module
            if "DirectoryConfig" not in self.sequencer.available_modules:
                raise WorkflowExecutionError("DirectoryConfig module not found or not available")

            directory_config_module = self.sequencer.available_modules["DirectoryConfig"]

            # Initialize if needed
            if not hasattr(directory_config_module, '_initialized') or not directory_config_module._initialized:
                init_result = directory_config_module.initialize()
                if init_result.get('status') == 'error':
                    raise WorkflowExecutionError(f"Failed to initialize DirectoryConfig: {init_result.get('message')}")

            # DirectoryConfig is interactive - log this info
            logging.info("DirectoryConfig module is interactive and may prompt for input")
            logging.info("This module will help configure which files to process")

            # Execute DirectoryConfig in the workflow directory context
            config_context = {
                **context,
                "interactive": True,
                "workflow_directory": str(workflow.directory)
            }

            # DirectoryConfig typically works on the directory as a whole, not individual files
            result = directory_config_module.execute(str(workflow.directory), **config_context)

            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            if result.get('status') in ['success', 'completed']:
                return ExecutionResult(
                    status="success",
                    message="DirectoryConfig completed successfully",
                    files_processed=len(workflow.files_discovered),
                    execution_time=execution_time,
                    module_name="DirectoryConfig"
                )
            else:
                return ExecutionResult(
                    status="failed",
                    message="DirectoryConfig execution failed",
                    error_message=result.get('message', 'Unknown error'),
                    execution_time=execution_time,
                    module_name="DirectoryConfig"
                )

        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            return ExecutionResult(
                status="failed",
                message="DirectoryConfig execution failed",
                error_message=str(e),
                execution_time=execution_time,
                module_name="DirectoryConfig"
            )

    def _execute_standard_module(self, module_name: str, context: Dict[str, Any]) -> ExecutionResult:
        """Execute a standard ADT module via ModuleSequencer."""
        from datetime import datetime

        start_time = datetime.now()

        try:
            # Get the module instance from ModuleSequencer
            if module_name not in self.sequencer.available_modules:
                raise WorkflowExecutionError(f"Module '{module_name}' not found or not available")

            module = self.sequencer.available_modules[module_name]

            # Initialize the module if not already done
            if not hasattr(module, '_initialized') or not module._initialized:
                init_result = module.initialize()
                if init_result.get('status') == 'error':
                    raise WorkflowExecutionError(f"Failed to initialize {module_name}: {init_result.get('message')}")

            # Execute module on discovered files
            files = context.get("files", [])
            files_processed = 0
            files_modified = 0

            for file_path in files:
                if not Path(file_path).exists():
                    continue

                try:
                    # Execute module on this file
                    result = module.execute(file_path, **context)

                    if result.get('status') in ['success', 'completed']:
                        files_processed += 1
                        if result.get('modified', False) or result.get('files_modified', 0) > 0:
                            files_modified += 1
                    elif result.get('status') == 'error':
                        # Log error but continue with other files
                        logging.warning(f"Module {module_name} failed on {file_path}: {result.get('message')}")

                except Exception as e:
                    # Log error but continue processing other files
                    logging.warning(f"Module {module_name} exception on {file_path}: {e}")
                    continue

            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            return ExecutionResult(
                status="success",
                message=f"{module_name} completed successfully",
                files_processed=files_processed,
                files_modified=files_modified,
                execution_time=execution_time,
                module_name=module_name
            )

        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            return ExecutionResult(
                status="failed",
                message=f"{module_name} execution failed",
                error_message=str(e),
                execution_time=execution_time,
                module_name=module_name
            )

    def _get_next_action(self, workflow: WorkflowState) -> str:
        """Get suggested next action for user."""
        next_module = workflow.get_next_module()
        if next_module:
            return f"Run: adt journey continue --name='{workflow.name}'"
        else:
            return "Workflow completed!"


class UserJourneyProcessor:
    """
    Handle CLI commands with rich user feedback.

    Provides the user interface for workflow management, including
    progress visualization and helpful error guidance.
    """

    def __init__(self, workflow_manager: Optional[WorkflowManager] = None):
        """Initialize UserJourneyProcessor."""
        self.workflow_manager = workflow_manager or WorkflowManager()

    def process_start_command(self, args) -> int:
        """
        Handle: adt journey start --name=X --directory=Y

        Args:
            args: Command line arguments with name and directory

        Returns:
            int: Exit code (0 for success, 1+ for error)
        """
        try:
            # Validate required arguments
            if not hasattr(args, 'name') or not args.name:
                self._print_error("Workflow name is required. Use --name=<workflow_name>")
                return 1

            if not hasattr(args, 'directory') or not args.directory:
                self._print_error("Directory is required. Use --directory=<path>")
                return 1

            # Normalize and validate directory path
            directory_path = Path(args.directory).resolve()

            self._print_info(f"Starting new workflow: '{args.name}'")
            self._print_info(f"Target directory: {directory_path}")

            # Check for existing workflow
            if self.workflow_manager.workflow_exists(args.name):
                self._print_error(f"Workflow '{args.name}' already exists!")
                self._print_info("Use 'adt journey resume' to continue an existing workflow")
                self._print_info("Or choose a different name with --name=<new_name>")
                return 1

            # Validate directory
            if not directory_path.exists():
                self._print_error(f"Directory '{directory_path}' does not exist")
                return 1

            if not directory_path.is_dir():
                self._print_error(f"'{directory_path}' is not a directory")
                return 1

            # Check for .adoc files
            adoc_files = list(directory_path.rglob("*.adoc"))
            if not adoc_files:
                self._print_warning(f"No .adoc files found in '{directory_path}'")
                response = input("Continue anyway? [Y/n]: ").strip().lower()
                if response in ['n', 'no']:
                    self._print_info("Operation cancelled.")
                    return 0

            # Get planned modules and show preview
            try:
                planned_modules = self.workflow_manager.get_planned_modules()
                self._print_info(f"\nPlanned module sequence:")
                for i, module in enumerate(planned_modules, 1):
                    self._print_info(f"  {i}. {module}")

                self._print_info(f"\nFound {len(adoc_files)} .adoc files to process")

            except WorkflowPlanningError as e:
                self._print_error(f"Module planning failed: {e}")
                return 1

            # Create workflow
            workflow = self.workflow_manager.start_workflow(args.name, str(directory_path))

            self._print_success(f"✅ Workflow '{args.name}' created successfully!")
            self._print_info(f"Workflow stored in: {workflow.get_storage_path()}")

            # Show next steps
            self._print_info("\nNext steps:")
            self._print_info(f"  adt journey continue --name='{args.name}'")
            self._print_info(f"  adt journey status --name='{args.name}'")

            return 0

        except WorkflowExistsError as e:
            self._print_error(str(e))
            return 1
        except InvalidDirectoryError as e:
            self._print_error(str(e))
            return 1
        except Exception as e:
            self._print_error(f"Unexpected error: {e}")
            logging.exception("Unexpected error in start_command")
            return 1

    def process_resume_command(self, args) -> int:
        """
        Handle: adt journey resume --name=X

        Args:
            args: Command line arguments with workflow name

        Returns:
            int: Exit code (0 for success, 1+ for error)
        """
        try:
            # Validate required arguments
            if not hasattr(args, 'name') or not args.name:
                self._print_error("Workflow name is required. Use --name=<workflow_name>")
                self._show_available_workflows()
                return 1

            self._print_info(f"Resuming workflow: '{args.name}'")

            # Load workflow
            try:
                workflow = self.workflow_manager.resume_workflow(args.name)
            except WorkflowNotFoundError:
                self._print_error(f"Workflow '{args.name}' not found")
                self._show_available_workflows()
                return 1

            # Show current status
            progress = workflow.get_progress_summary()
            self._show_workflow_status(workflow, progress)

            # Check if already completed
            if progress.pending_modules == 0:
                self._print_success("🎉 Workflow is already completed!")
                return 0

            # Show next action
            next_module = progress.current_module
            if next_module:
                self._print_info(f"\nNext module to execute: {next_module}")
                self._print_info(f"Run: adt journey continue --name='{args.name}'")

            return 0

        except WorkflowStateError as e:
            self._print_error(f"Workflow state error: {e}")
            return 1
        except Exception as e:
            self._print_error(f"Unexpected error: {e}")
            logging.exception("Unexpected error in resume_command")
            return 1

    def process_status_command(self, args) -> int:
        """
        Handle: adt journey status [--name=X]

        Args:
            args: Command line arguments, optionally with workflow name

        Returns:
            int: Exit code (0 for success, 1+ for error)
        """
        try:
            # If no specific workflow requested, show all workflows
            if not hasattr(args, 'name') or not args.name:
                return self._show_all_workflow_status()

            # Show specific workflow status
            try:
                workflow = self.workflow_manager.resume_workflow(args.name)
            except WorkflowNotFoundError:
                self._print_error(f"Workflow '{args.name}' not found")
                self._show_available_workflows()
                return 1

            progress = workflow.get_progress_summary()
            self._show_workflow_status(workflow, progress, detailed=True)

            return 0

        except Exception as e:
            self._print_error(f"Unexpected error: {e}")
            logging.exception("Unexpected error in status_command")
            return 1

    def process_continue_command(self, args) -> int:
        """
        Handle: adt journey continue --name=X

        Args:
            args: Command line arguments with workflow name

        Returns:
            int: Exit code (0 for success, 1+ for error)
        """
        try:
            # Validate required arguments
            if not hasattr(args, 'name') or not args.name:
                self._print_error("Workflow name is required. Use --name=<workflow_name>")
                self._show_available_workflows()
                return 1

            # Load workflow
            try:
                workflow = self.workflow_manager.resume_workflow(args.name)
            except WorkflowNotFoundError:
                self._print_error(f"Workflow '{args.name}' not found")
                self._show_available_workflows()
                return 1

            # Check if already completed
            progress = workflow.get_progress_summary()
            if progress.pending_modules == 0:
                self._print_success("🎉 Workflow is already completed!")
                self._show_workflow_status(workflow, progress)
                return 0

            # Execute next module
            next_module = progress.current_module
            if not next_module:
                self._print_success("🎉 All modules completed!")
                return 0

            self._print_info(f"Executing module: {next_module}")
            self._show_progress_bar(progress)

            try:
                result = self.workflow_manager.execute_next_module(workflow)

                if result.status == "success":
                    self._print_success(f"✅ {result.message}")
                    if result.files_processed > 0:
                        self._print_info(f"Files processed: {result.files_processed}")

                    # Show next action
                    if result.next_action:
                        self._print_info(f"\nNext: {result.next_action}")

                elif result.status == "completed":
                    self._print_success(f"🎉 {result.message}")
                    # Show final summary
                    final_progress = workflow.get_progress_summary()
                    self._show_workflow_summary(workflow, final_progress)

                return 0

            except WorkflowExecutionError as e:
                self._print_error(f"Module execution failed: {e}")
                self._print_info("Check the error above and fix any issues, then try again.")
                return 1

        except Exception as e:
            self._print_error(f"Unexpected error: {e}")
            logging.exception("Unexpected error in continue_command")
            return 1

    def process_list_command(self, args) -> int:
        """
        Handle: adt journey list

        Args:
            args: Command line arguments (unused for list)

        Returns:
            int: Exit code (0 for success, 1+ for error)
        """
        try:
            workflows = self.workflow_manager.list_available_workflows()

            if not workflows:
                self._print_info("No workflows found.")
                self._print_info("Create a new workflow with: adt journey start --name=<name> --directory=<path>")
                return 0

            self._print_info(f"Found {len(workflows)} workflow(s):")
            print()  # Empty line for formatting

            for workflow_name in sorted(workflows):
                try:
                    workflow = self.workflow_manager.resume_workflow(workflow_name)
                    progress = workflow.get_progress_summary()

                    # Status indicator
                    if progress.completion_percentage == 100:
                        status_icon = "🎉"
                        status_text = "COMPLETED"
                    elif progress.failed_modules > 0:
                        status_icon = "❌"
                        status_text = "FAILED"
                    elif progress.completed_modules > 0:
                        status_icon = "🔄"
                        status_text = "IN PROGRESS"
                    else:
                        status_icon = "⏸️"
                        status_text = "PENDING"

                    print(f"  {status_icon} {workflow_name:<20} {status_text}")
                    print(f"     Directory: {workflow.directory}")
                    print(f"     Progress:  {progress.completed_modules}/{progress.total_modules} modules ({progress.completion_percentage:.1f}%)")
                    print(f"     Files:     {progress.processed_files}/{progress.total_files}")
                    print(f"     Modified:  {workflow.last_activity[:19].replace('T', ' ')}")
                    print()

                except Exception as e:
                    print(f"  ⚠️  {workflow_name:<20} ERROR (corrupted state)")
                    print(f"     Error: {e}")
                    print()

            return 0

        except Exception as e:
            self._print_error(f"Unexpected error: {e}")
            logging.exception("Unexpected error in list_command")
            return 1

    def process_cleanup_command(self, args) -> int:
        """
        Handle: adt journey cleanup [--name=X] [--all] [--completed]

        Args:
            args: Command line arguments with cleanup options

        Returns:
            int: Exit code (0 for success, 1+ for error)
        """
        try:
            # Handle specific workflow cleanup
            if hasattr(args, 'name') and args.name:
                return self._cleanup_specific_workflow(args.name)

            # Handle bulk cleanup options
            cleanup_all = getattr(args, 'all', False)
            cleanup_completed = getattr(args, 'completed', False)

            if not cleanup_all and not cleanup_completed:
                self._print_error("Specify what to clean up:")
                self._print_info("  --name=<workflow>  Delete specific workflow")
                self._print_info("  --completed        Delete all completed workflows")
                self._print_info("  --all              Delete all workflows (use with caution!)")
                return 1

            workflows = self.workflow_manager.list_available_workflows()
            if not workflows:
                self._print_info("No workflows to clean up.")
                return 0

            to_delete = []

            if cleanup_all:
                to_delete = workflows
                self._print_warning(f"This will delete ALL {len(workflows)} workflows!")
            elif cleanup_completed:
                for workflow_name in workflows:
                    try:
                        workflow = self.workflow_manager.resume_workflow(workflow_name)
                        progress = workflow.get_progress_summary()
                        if progress.completion_percentage == 100:
                            to_delete.append(workflow_name)
                    except Exception:
                        pass  # Skip corrupted workflows

                if not to_delete:
                    self._print_info("No completed workflows to clean up.")
                    return 0

                self._print_info(f"Found {len(to_delete)} completed workflow(s) to delete:")
                for name in to_delete:
                    print(f"  - {name}")

            # Confirm deletion
            response = input(f"\nDelete {len(to_delete)} workflow(s)? [y/N]: ").strip().lower()
            if response not in ['y', 'yes']:
                self._print_info("Operation cancelled.")
                return 0

            # Perform deletion
            deleted_count = 0
            for workflow_name in to_delete:
                try:
                    if self.workflow_manager._storage_dir is not None:
                        storage_path = self.workflow_manager._storage_dir / f"{workflow_name}.json"
                    else:
                        storage_path = Path.home() / ".adt" / "workflows" / f"{workflow_name}.json"

                    if storage_path.exists():
                        storage_path.unlink()
                        deleted_count += 1
                        self._print_info(f"Deleted: {workflow_name}")

                    # Also delete backup if it exists
                    backup_path = storage_path.with_suffix('.backup')
                    if backup_path.exists():
                        backup_path.unlink()

                except Exception as e:
                    self._print_error(f"Failed to delete {workflow_name}: {e}")

            self._print_success(f"✅ Deleted {deleted_count} workflow(s)")
            return 0

        except Exception as e:
            self._print_error(f"Unexpected error: {e}")
            logging.exception("Unexpected error in cleanup_command")
            return 1

    # Helper methods for rich user feedback

    def _cleanup_specific_workflow(self, workflow_name: str) -> int:
        """Clean up a specific workflow."""
        if not self.workflow_manager.workflow_exists(workflow_name):
            self._print_error(f"Workflow '{workflow_name}' not found")
            self._show_available_workflows()
            return 1

        try:
            workflow = self.workflow_manager.resume_workflow(workflow_name)
            progress = workflow.get_progress_summary()

            self._print_info(f"Workflow: {workflow_name}")
            self._print_info(f"Status:   {progress.completion_percentage:.1f}% complete")
            self._print_info(f"Directory: {workflow.directory}")

        except Exception as e:
            self._print_warning(f"Could not load workflow details: {e}")

        response = input(f"\nDelete workflow '{workflow_name}'? [y/N]: ").strip().lower()
        if response not in ['y', 'yes']:
            self._print_info("Operation cancelled.")
            return 0

        try:
            if self.workflow_manager._storage_dir is not None:
                storage_path = self.workflow_manager._storage_dir / f"{workflow_name}.json"
            else:
                storage_path = Path.home() / ".adt" / "workflows" / f"{workflow_name}.json"

            if storage_path.exists():
                storage_path.unlink()

            backup_path = storage_path.with_suffix('.backup')
            if backup_path.exists():
                backup_path.unlink()

            self._print_success(f"✅ Deleted workflow: {workflow_name}")
            return 0

        except Exception as e:
            self._print_error(f"Failed to delete workflow: {e}")
            return 1

    def _show_available_workflows(self) -> None:
        """Show available workflows as a helpful hint."""
        try:
            workflows = self.workflow_manager.list_available_workflows()
            if workflows:
                self._print_info("Available workflows:")
                for name in sorted(workflows):
                    print(f"  - {name}")
            else:
                self._print_info("No workflows found. Create one with 'adt journey start'")
        except Exception:
            pass  # Don't fail if we can't show available workflows

    def _show_all_workflow_status(self) -> int:
        """Show status for all workflows."""
        workflows = self.workflow_manager.list_available_workflows()

        if not workflows:
            self._print_info("No workflows found.")
            return 0

        self._print_info(f"Status for {len(workflows)} workflow(s):\n")

        for workflow_name in sorted(workflows):
            try:
                workflow = self.workflow_manager.resume_workflow(workflow_name)
                progress = workflow.get_progress_summary()
                self._show_workflow_status(workflow, progress, compact=True)
                print()  # Empty line between workflows

            except Exception as e:
                self._print_error(f"Failed to load {workflow_name}: {e}")

        return 0

    def _show_workflow_status(self, workflow: WorkflowState, progress: WorkflowProgress,
                             detailed: bool = False, compact: bool = False) -> None:
        """Show formatted workflow status."""
        if compact:
            # Compact format for multi-workflow display
            status_indicator = "🎉" if progress.completion_percentage == 100 else "🔄" if progress.completed_modules > 0 else "⏸️"
            print(f"{status_indicator} {workflow.name}")
            print(f"   Progress: {progress.completed_modules}/{progress.total_modules} modules ({progress.completion_percentage:.1f}%)")
            if progress.failed_modules > 0:
                print(f"   Failed:   {progress.failed_modules} modules")
            return

        # Full status display
        print(f"\n{'='*50}")
        print(f"Workflow: {workflow.name}")
        print(f"Directory: {workflow.directory}")
        print(f"Created: {workflow.created[:19].replace('T', ' ')}")
        print(f"Last Activity: {workflow.last_activity[:19].replace('T', ' ')}")
        print(f"{'='*50}")

        # Progress overview
        print(f"\nProgress Overview:")
        print(f"  Total Modules:     {progress.total_modules}")
        print(f"  Completed:         {progress.completed_modules}")
        print(f"  Failed:            {progress.failed_modules}")
        print(f"  Pending:           {progress.pending_modules}")
        print(f"  Overall Progress:  {progress.completion_percentage:.1f}%")

        # File statistics
        print(f"\nFile Statistics:")
        print(f"  Total Files:       {progress.total_files}")
        print(f"  Processed Files:   {progress.processed_files}")

        # Current status
        if progress.current_module:
            print(f"\nCurrent Module:      {progress.current_module}")
        elif progress.completion_percentage == 100:
            print(f"\nStatus:              🎉 COMPLETED")
        else:
            print(f"\nStatus:              ⏸️  READY")

        # Detailed module status
        if detailed:
            print(f"\nModule Details:")
            for module_name, module_state in workflow.modules.items():
                status_icon = {
                    "completed": "✅",
                    "running": "🔄",
                    "failed": "❌",
                    "pending": "⏸️"
                }.get(module_state.status, "❓")

                print(f"  {status_icon} {module_name:<15} {module_state.status.upper()}")

                if module_state.status == "completed" and module_state.files_processed:
                    print(f"      Files processed: {module_state.files_processed}")
                    if module_state.execution_time:
                        print(f"      Execution time:  {module_state.execution_time:.2f}s")

                if module_state.status == "failed" and module_state.error_message:
                    print(f"      Error: {module_state.error_message}")

    def _show_workflow_summary(self, workflow: WorkflowState, progress: WorkflowProgress) -> None:
        """Show final workflow completion summary."""
        print(f"\n🎉 Workflow '{workflow.name}' completed successfully!")
        print(f"{'='*50}")
        print(f"Total modules executed: {progress.total_modules}")
        print(f"Total files processed:  {progress.processed_files}")
        print(f"Directory:             {workflow.directory}")
        print(f"{'='*50}")

    def _show_progress_bar(self, progress: WorkflowProgress) -> None:
        """Show a simple progress bar."""
        completed = progress.completed_modules
        total = progress.total_modules

        if total == 0:
            return

        bar_width = 30
        filled = int(bar_width * completed / total)
        bar = "█" * filled + "░" * (bar_width - filled)
        percentage = progress.completion_percentage

        print(f"Progress: [{bar}] {percentage:.1f}% ({completed}/{total} modules)")

    def _print_success(self, message: str) -> None:
        """Print success message with green color if supported."""
        print(f"✅ {message}")

    def _print_info(self, message: str) -> None:
        """Print info message."""
        print(f"ℹ️  {message}")

    def _print_warning(self, message: str) -> None:
        """Print warning message with yellow color if supported."""
        print(f"⚠️  {message}")

    def _print_error(self, message: str) -> None:
        """Print error message with red color if supported."""
        print(f"❌ {message}")

    def _format_time_duration(self, seconds: float) -> str:
        """Format execution time in human-readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"


# ============================================================================
# Module Integration (for ADT system compatibility)
# ============================================================================

class UserJourneyModule(ADTModule):
    """
    ADTModule implementation for UserJourney plugin.

    UserJourney is a CLI-first orchestrator that uses ModuleSequencer to execute
    other modules but is not itself executed by ModuleSequencer. This wrapper
    provides minimal ADTModule compatibility for system integration.
    """

    @property
    def name(self) -> str:
        """Module name identifier."""
        return "UserJourney"

    @property
    def version(self) -> str:
        """Module version using semantic versioning."""
        return "1.0.0"

    @property
    def dependencies(self) -> List[str]:
        """List of required module names."""
        return ["DirectoryConfig"]  # DirectoryConfig is required

    @property
    def release_status(self) -> str:
        """Release status: 'stable' for production-ready features."""
        return "stable"

    def initialize(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Initialize the module with configuration.

        Args:
            config: Configuration dictionary containing module settings

        Returns:
            Dict containing initialization status
        """
        if config is None:
            config = {}

        # Store configuration
        self.config = config
        self.verbose = config.get("verbose", False)

        # Set up logging
        self._setup_logging()

        # Initialize processor
        try:
            self.processor = UserJourneyProcessor()
            self._initialized = True

            if self.verbose:
                logging.info("UserJourney module initialized successfully")

            return {"status": "success", "message": "UserJourney initialized"}

        except Exception as e:
            logging.error(f"Failed to initialize UserJourney module: {e}")
            return {"status": "error", "message": f"Initialization failed: {e}"}

    def _setup_logging(self) -> None:
        """Set up logging for UserJourney operations."""
        # Create logger for UserJourney
        logger = logging.getLogger("UserJourney")

        # Set level based on configuration
        if self.verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        # Add console handler if not already present
        if not logger.handlers:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(logging.INFO if not self.verbose else logging.DEBUG)

            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)

            logger.addHandler(console_handler)

        # Also configure file logging if enabled
        log_file = self.config.get("log_file")
        if log_file:
            try:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)

                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)

                logger.addHandler(file_handler)
                logging.info(f"UserJourney logging to file: {log_file}")

            except Exception as e:
                logging.warning(f"Failed to set up file logging: {e}")

    def execute(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the module on a file.

        Note: UserJourney is a CLI orchestrator and should not be called
        as part of normal module execution. This method exists for
        ADTModule compatibility only.

        Args:
            file_path: Path to the file to process
            **kwargs: Additional arguments

        Returns:
            Dict containing execution status
        """
        return {
            "status": "skipped",
            "message": "UserJourney is a CLI orchestrator and should not be executed as a module",
            "modified": False
        }

    def get_cli_parser(self):
        """
        Get CLI argument parser for UserJourney commands.

        This is called by the main ADT CLI to add journey subcommands.

        Returns:
            Configured argument parser for journey commands
        """
        import argparse

        parser = argparse.ArgumentParser(
            prog="adt journey",
            description="Workflow orchestration for ADT processing pipelines"
        )

        subparsers = parser.add_subparsers(dest='journey_command', help='Journey commands')

        # Start command
        start_parser = subparsers.add_parser('start', help='Start a new workflow')
        start_parser.add_argument('--name', required=True, help='Workflow name')
        start_parser.add_argument('--directory', required=True, help='Target directory')

        # Resume command
        resume_parser = subparsers.add_parser('resume', help='Resume an existing workflow')
        resume_parser.add_argument('--name', required=True, help='Workflow name')

        # Status command
        status_parser = subparsers.add_parser('status', help='Show workflow status')
        status_parser.add_argument('--name', help='Workflow name (optional, shows all if omitted)')

        # Continue command
        continue_parser = subparsers.add_parser('continue', help='Continue workflow execution')
        continue_parser.add_argument('--name', required=True, help='Workflow name')

        # List command
        list_parser = subparsers.add_parser('list', help='List all workflows')

        # Cleanup command
        cleanup_parser = subparsers.add_parser('cleanup', help='Clean up workflows')
        cleanup_group = cleanup_parser.add_mutually_exclusive_group(required=True)
        cleanup_group.add_argument('--name', help='Delete specific workflow')
        cleanup_group.add_argument('--completed', action='store_true', help='Delete completed workflows')
        cleanup_group.add_argument('--all', action='store_true', help='Delete all workflows')

        return parser

    def process_cli_command(self, args) -> int:
        """
        Process CLI command for UserJourney.

        Args:
            args: Parsed command line arguments

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        if not hasattr(self, 'processor'):
            print("❌ UserJourney module not initialized")
            return 1

        # Dispatch to appropriate processor method
        command = getattr(args, 'journey_command', None)

        if command == 'start':
            return self.processor.process_start_command(args)
        elif command == 'resume':
            return self.processor.process_resume_command(args)
        elif command == 'status':
            return self.processor.process_status_command(args)
        elif command == 'continue':
            return self.processor.process_continue_command(args)
        elif command == 'list':
            return self.processor.process_list_command(args)
        elif command == 'cleanup':
            return self.processor.process_cleanup_command(args)
        else:
            print("❌ Unknown journey command")
            return 1


# The UserJourney plugin integrates with ADT as a CLI orchestrator,
# not as a standard ADTModule in the sequencing chain.
# The actual CLI integration is handled through the UserJourneyModule wrapper.
