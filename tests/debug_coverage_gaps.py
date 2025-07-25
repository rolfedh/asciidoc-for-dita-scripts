#!/usr/bin/env python3
"""
Debug script for coverage gap test issues
"""
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock


# Test the specific failing scenario
def debug_module_crash_test():
    """Debug why the module crash test isn't working."""
    print("🔍 Debugging module crash test...")

    # Set up test environment
    temp_dir = Path(tempfile.mkdtemp())
    temp_storage = temp_dir / "workflows"
    temp_storage.mkdir()
    test_project = temp_dir / "project"
    test_project.mkdir()

    # Create test files
    (test_project / "doc1.adoc").write_text("= Doc 1\nContent")
    (test_project / "doc2.adoc").write_text("= Doc 2\nContent")

    try:
        from asciidoc_dita_toolkit.modules.user_journey import (
            WorkflowManager,
            WorkflowState,
            WorkflowExecutionError,
        )
        from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleState

        # Set storage for testing
        WorkflowState._default_storage_dir = temp_storage
        WorkflowManager.set_storage_directory(temp_storage)

        # Create mock sequencer
        mock_sequencer = Mock()
        mock_resolution = Mock()
        mock_resolution.name = "DirectoryConfig"
        mock_resolution.state = ModuleState.ENABLED

        mock_sequencer.sequence_modules.return_value = ([mock_resolution], [])

        print(f"✅ Mock sequencer set up: {mock_sequencer}")
        print(f"✅ Resolution: {mock_resolution.name}, state: {mock_resolution.state}")

        # Mock available modules with a crashing module
        crashing_module = Mock()
        crashing_module.execute.side_effect = RuntimeError("Module crashed!")
        crashing_module.initialize.return_value = {"status": "success"}
        crashing_module._initialized = False

        mock_sequencer.available_modules = {"DirectoryConfig": crashing_module}

        print(f"✅ Crashing module set up: {crashing_module}")

        # Create manager and workflow
        manager = WorkflowManager(mock_sequencer)
        workflow = manager.start_workflow("crash_test", str(test_project))

        print(f"✅ Workflow created: {workflow.name}")
        print(f"   Modules: {list(workflow.modules.keys())}")
        print(f"   Next module: {workflow.get_next_module()}")

        # Try to execute next module
        try:
            print("🔄 Executing next module...")
            result = manager.execute_next_module(workflow)
            print(f"❌ Expected exception but got result: {result}")
        except WorkflowExecutionError as e:
            print(f"✅ Got expected WorkflowExecutionError: {e}")
        except Exception as e:
            print(f"❓ Got unexpected exception: {type(e).__name__}: {e}")
            import traceback

            traceback.print_exc()

    except Exception as e:
        print(f"❌ Setup error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    debug_module_crash_test()
