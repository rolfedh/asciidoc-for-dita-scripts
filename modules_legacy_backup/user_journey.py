"""
UserJourney Module Wrapper for ADT Module System

This module provides the ADTModule interface wrapper for the UserJourney plugin.
Unlike other ADT modules that process content directly, UserJourney orchestrates
other modules and provides CLI workflow management.

The UserJourney plugin is designed to work outside the normal module sequencing
chain as a CLI orchestrator that uses ModuleSequencer to execute other modules.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

# Import ADT base class
try:
    from asciidoc_dita_toolkit.adt_core.module_sequencer import ADTModule
except ImportError:
    # Handle case where we're running from different context
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
    from asciidoc_dita_toolkit.adt_core.module_sequencer import ADTModule

# Import UserJourney plugin core
from asciidoc_dita_toolkit.asciidoc_dita.plugins.UserJourney import (
    UserJourneyProcessor,
    WorkflowManager,
    UserJourneyError,
)


class UserJourney(ADTModule):
    """
    UserJourney ADTModule wrapper.

    This provides the ADTModule interface for system compatibility,
    but the main functionality is through the CLI processor and
    workflow manager classes.
    """

    def __init__(self):
        """Initialize UserJourney module wrapper."""
        super().__init__()
        self._processor = None
        self._workflow_manager = None

    @property
    def name(self) -> str:
        """Return module name."""
        return "UserJourney"

    @property
    def version(self) -> str:
        """Return module version."""
        return "2.0.0"

    @property
    def dependencies(self) -> List[str]:
        """
        Return module dependencies.

        UserJourney doesn't have dependencies in the traditional sense
        since it orchestrates other modules rather than being sequenced with them.
        However, it requires DirectoryConfig to be available for file discovery.
        """
        return ["DirectoryConfig"]  # Soft dependency for file discovery

    def initialize(self, **kwargs) -> Dict[str, Any]:
        """
        Initialize the UserJourney module.

        Args:
            **kwargs: Initialization parameters

        Returns:
            Dict containing initialization status
        """
        try:
            # Initialize core components
            self._workflow_manager = WorkflowManager()
            self._processor = UserJourneyProcessor(self._workflow_manager)

            return {
                "status": "initialized",
                "message": "UserJourney module initialized successfully",
                "cli_available": True,
                "workflow_management": True,
            }

        except Exception as e:
            logging.error(f"Failed to initialize UserJourney module: {e}")
            return {
                "status": "error",
                "message": f"Initialization failed: {e}",
                "cli_available": False,
                "workflow_management": False,
            }

    def execute(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the UserJourney module.

        Note: UserJourney is designed as a CLI orchestrator, not as a file processor.
        This method provides compatibility with the ADTModule interface but
        typical usage is through CLI commands.

        Args:
            file_path: File path (not used in UserJourney context)
            **kwargs: Additional parameters

        Returns:
            Dict containing execution results
        """
        try:
            # UserJourney doesn't process individual files
            # It orchestrates workflows across entire directories
            logging.info(
                "UserJourney.execute() called - this module works at the workflow level"
            )

            # Check if we have workflow context from CLI
            workflow_name = kwargs.get('workflow_name')
            if workflow_name and self._workflow_manager:
                # This could be called from within a workflow execution
                return {
                    "status": "success",
                    "message": f"UserJourney context for workflow: {workflow_name}",
                    "files_processed": 0,
                    "workflow_orchestration": True,
                }
            else:
                return {
                    "status": "info",
                    "message": "UserJourney operates through CLI commands. Use: adt journey --help",
                    "files_processed": 0,
                    "recommendation": "Use 'adt journey start' to begin a workflow",
                }

        except Exception as e:
            logging.error(f"UserJourney execution error: {e}")
            return {
                "status": "error",
                "message": f"Execution failed: {e}",
                "files_processed": 0,
            }

    def get_processor(self) -> Optional[UserJourneyProcessor]:
        """
        Get the CLI processor instance.

        Returns:
            UserJourneyProcessor instance if initialized, None otherwise
        """
        return self._processor

    def get_workflow_manager(self) -> Optional[WorkflowManager]:
        """
        Get the workflow manager instance.

        Returns:
            WorkflowManager instance if initialized, None otherwise
        """
        return self._workflow_manager

    def create_workflow(self, name: str, directory: str) -> Dict[str, Any]:
        """
        Create a new workflow (convenience method).

        Args:
            name: Workflow name
            directory: Target directory

        Returns:
            Dict containing creation results
        """
        if not self._workflow_manager:
            return {"status": "error", "message": "Module not initialized"}

        try:
            workflow = self._workflow_manager.start_workflow(name, directory)
            return {
                "status": "success",
                "message": f"Workflow '{name}' created successfully",
                "workflow_name": workflow.name,
                "directory": str(workflow.directory),
                "modules_planned": len(workflow.modules),
            }
        except UserJourneyError as e:
            return {"status": "error", "message": str(e)}

    def list_workflows(self) -> Dict[str, Any]:
        """
        List available workflows (convenience method).

        Returns:
            Dict containing workflow list
        """
        if not self._workflow_manager:
            return {"status": "error", "message": "Module not initialized"}

        try:
            workflows = self._workflow_manager.list_available_workflows()
            return {
                "status": "success",
                "workflows": workflows,
                "count": len(workflows),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Module factory function for ADT system
def create_user_journey_module() -> UserJourney:
    """Create and return a UserJourney module instance."""
    return UserJourney()


# Export the module class for direct import
__all__ = ['UserJourney', 'create_user_journey_module']
