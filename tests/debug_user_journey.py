#!/usr/bin/env python3
"""
Debug utilities for UserJourney Plugin.

This script provides debugging commands to troubleshoot UserJourney workflows,
test integration with ModuleSequencer and DirectoryConfig, and diagnose
common issues.

Usage:
    python debug_user_journey.py list
    python debug_user_journey.py workflow <name>
    python debug_user_journey.py sequencing
    python debug_user_journey.py directory-config
    python debug_user_journey.py test-storage
"""

import argparse
import json
import os
import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from asciidoc_dita_toolkit.asciidoc_dita.plugins.UserJourney import (
        WorkflowState, WorkflowManager, UserJourneyProcessor, UserJourneyModule,
        WorkflowNotFoundError, WorkflowStateError
    )
    from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleSequencer, ModuleState
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project root directory")
    IMPORTS_SUCCESSFUL = False


def debug_list_workflows():
    """Debug command: List all workflows with detailed information."""
    print("🔍 Debug: List Workflows")
    print("=" * 50)
    
    try:
        workflow_manager = WorkflowManager()
        workflows = workflow_manager.list_available_workflows()
        
        if not workflows:
            print("No workflows found.")
            print(f"Storage directory: {Path.home() / '.adt' / 'workflows'}")
            return 0
        
        print(f"Found {len(workflows)} workflow(s):\n")
        
        for workflow_name in sorted(workflows):
            try:
                print(f"📁 Workflow: {workflow_name}")
                
                # Load and show detailed state
                workflow = workflow_manager.resume_workflow(workflow_name)
                progress = workflow.get_progress_summary()
                
                print(f"   Status: {workflow.status}")
                print(f"   Directory: {workflow.directory}")
                print(f"   Created: {workflow.created}")
                print(f"   Last Activity: {workflow.last_activity}")
                print(f"   Progress: {progress.completed_modules}/{progress.total_modules} modules")
                print(f"   Files: {len(workflow.files_discovered)} discovered, {progress.processed_files} processed")
                
                # Show module states
                print("   Modules:")
                for module_name, state in workflow.modules.items():
                    status_icon = {"completed": "✅", "running": "🔄", "failed": "❌", "pending": "⏸️"}.get(state.status, "❓")
                    print(f"     {status_icon} {module_name}: {state.status}")
                    if state.error_message:
                        print(f"       Error: {state.error_message}")
                
                # Show storage info
                storage_path = workflow.get_storage_path()
                if storage_path.exists():
                    size = storage_path.stat().st_size
                    print(f"   Storage: {storage_path} ({size} bytes)")
                else:
                    print(f"   ⚠️  Storage file missing: {storage_path}")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Error loading {workflow_name}: {e}")
                print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to list workflows: {e}")
        traceback.print_exc()
        return 1


def debug_specific_workflow(workflow_name: str):
    """Debug command: Analyze a specific workflow in detail."""
    print(f"🔍 Debug: Workflow '{workflow_name}'")
    print("=" * 50)
    
    try:
        workflow_manager = WorkflowManager()
        
        # Check if workflow exists
        if not workflow_manager.workflow_exists(workflow_name):
            print(f"❌ Workflow '{workflow_name}' not found")
            
            # Show available workflows
            available = workflow_manager.list_available_workflows()
            if available:
                print("\nAvailable workflows:")
                for name in available:
                    print(f"  - {name}")
            else:
                print("No workflows available.")
            
            return 1
        
        # Load workflow
        workflow = workflow_manager.resume_workflow(workflow_name)
        
        # Basic info
        print(f"📋 Basic Information:")
        print(f"   Name: {workflow.name}")
        print(f"   Status: {workflow.status}")
        print(f"   Directory: {workflow.directory}")
        print(f"   Created: {workflow.created}")
        print(f"   Last Activity: {workflow.last_activity}")
        print(f"   Version: {workflow.metadata.get('version', 'unknown')}")
        print(f"   ADT Version: {workflow.metadata.get('adt_version', 'unknown')}")
        
        # Directory validation
        print(f"\n📂 Directory Validation:")
        if workflow.directory.exists():
            print(f"   ✅ Directory exists: {workflow.directory}")
            if workflow.directory.is_dir():
                print(f"   ✅ Is directory: True")
                
                # Count .adoc files
                adoc_files = list(workflow.directory.rglob("*.adoc"))
                print(f"   📄 .adoc files found: {len(adoc_files)}")
                
                if adoc_files:
                    print(f"   📄 Sample files:")
                    for f in adoc_files[:5]:  # Show first 5
                        print(f"      - {f.relative_to(workflow.directory)}")
                    if len(adoc_files) > 5:
                        print(f"      ... and {len(adoc_files) - 5} more")
            else:
                print(f"   ❌ Not a directory")
        else:
            print(f"   ❌ Directory does not exist")
        
        # File discovery
        print(f"\n🔍 File Discovery:")
        print(f"   Discovered files: {len(workflow.files_discovered)}")
        if workflow.files_discovered:
            print(f"   Sample discovered files:")
            for f in workflow.files_discovered[:5]:
                print(f"      - {Path(f).name}")
            if len(workflow.files_discovered) > 5:
                print(f"      ... and {len(workflow.files_discovered) - 5} more")
        
        # DirectoryConfig integration
        print(f"\n⚙️  DirectoryConfig Integration:")
        if workflow.directory_config:
            print(f"   ✅ DirectoryConfig loaded")
            if isinstance(workflow.directory_config, dict):
                print(f"   📋 Config keys: {list(workflow.directory_config.keys())}")
            else:
                print(f"   📋 Config type: {type(workflow.directory_config)}")
        else:
            print(f"   ⚠️  No DirectoryConfig loaded")
        
        # Module analysis
        progress = workflow.get_progress_summary()
        print(f"\n🧩 Module Analysis:")
        print(f"   Total modules: {progress.total_modules}")
        print(f"   Completed: {progress.completed_modules}")
        print(f"   Failed: {progress.failed_modules}")
        print(f"   Pending: {progress.pending_modules}")
        print(f"   Progress: {progress.completion_percentage:.1f}%")
        print(f"   Current module: {progress.current_module or 'None (completed)'}")
        
        print(f"\n📊 Module Details:")
        for module_name, state in workflow.modules.items():
            status_icon = {"completed": "✅", "running": "🔄", "failed": "❌", "pending": "⏸️"}.get(state.status, "❓")
            print(f"   {status_icon} {module_name}")
            print(f"      Status: {state.status}")
            
            if state.started_at:
                print(f"      Started: {state.started_at}")
            if state.completed_at:
                print(f"      Completed: {state.completed_at}")
            if state.execution_time:
                print(f"      Execution time: {state.execution_time:.2f}s")
            if state.files_processed:
                print(f"      Files processed: {state.files_processed}")
            if state.files_modified:
                print(f"      Files modified: {state.files_modified}")
            if state.retry_count > 0:
                print(f"      Retry count: {state.retry_count}")
            if state.error_message:
                print(f"      Error: {state.error_message}")
        
        # Storage analysis
        print(f"\n💾 Storage Analysis:")
        storage_path = workflow.get_storage_path()
        print(f"   Storage path: {storage_path}")
        
        if storage_path.exists():
            stat = storage_path.stat()
            print(f"   ✅ File exists: {stat.st_size} bytes")
            print(f"   Modified: {datetime.fromtimestamp(stat.st_mtime)}")
            
            # Check for backup
            backup_path = storage_path.with_suffix('.backup')
            if backup_path.exists():
                backup_stat = backup_path.stat()
                print(f"   📄 Backup exists: {backup_stat.st_size} bytes")
            
            # Validate JSON
            try:
                with open(storage_path) as f:
                    data = json.load(f)
                print(f"   ✅ JSON valid: {len(data)} top-level keys")
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON invalid: {e}")
        else:
            print(f"   ❌ Storage file does not exist")
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to debug workflow: {e}")
        traceback.print_exc()
        return 1


def debug_module_sequencing():
    """Debug command: Test ModuleSequencer integration."""
    print("🔍 Debug: ModuleSequencer Integration")
    print("=" * 50)
    
    try:
        print("🚀 Initializing ModuleSequencer...")
        sequencer = ModuleSequencer()
        
        # Load configurations
        print("⚙️  Loading configurations...")
        try:
            sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')
            print("   ✅ Configurations loaded")
        except Exception as e:
            print(f"   ⚠️  Configuration loading failed: {e}")
            print("   This may be normal if config files don't exist")
        
        # Discover modules
        print("🔍 Discovering modules...")
        try:
            sequencer.discover_modules()
            print(f"   ✅ Modules discovered: {len(sequencer.available_modules)}")
            
            # Show available modules
            print("   📋 Available modules:")
            for name, module in sequencer.available_modules.items():
                if hasattr(module, 'version'):
                    version = module.version
                else:
                    version = "unknown"
                print(f"      - {name} (v{version})")
            
        except Exception as e:
            print(f"   ❌ Module discovery failed: {e}")
            return 1
        
        # Test module sequencing
        print("\n🎯 Testing module sequencing...")
        try:
            resolutions, errors = sequencer.sequence_modules()
            
            if errors:
                print(f"   ⚠️  Sequencing errors: {len(errors)}")
                for error in errors:
                    print(f"      - {error}")
            else:
                print("   ✅ No sequencing errors")
            
            print(f"   📊 Module resolutions: {len(resolutions)}")
            
            # Show resolution details
            enabled_modules = []
            for resolution in resolutions:
                state_icon = {"ENABLED": "✅", "DISABLED": "❌", "ERROR": "⚠️"}.get(resolution.state.name, "❓")
                print(f"      {state_icon} {resolution.name}: {resolution.state.name}")
                
                if resolution.state == ModuleState.ENABLED:
                    enabled_modules.append(resolution.name)
            
            print(f"\n🎪 Planned execution order:")
            for i, module_name in enumerate(enabled_modules, 1):
                print(f"   {i}. {module_name}")
            
            # Validate DirectoryConfig is first
            if enabled_modules and enabled_modules[0] == "DirectoryConfig":
                print("   ✅ DirectoryConfig is first (required)")
            else:
                print("   ⚠️  DirectoryConfig should be first module")
            
        except Exception as e:
            print(f"   ❌ Module sequencing failed: {e}")
            traceback.print_exc()
            return 1
        
        # Test WorkflowManager integration
        print(f"\n🔗 Testing WorkflowManager integration...")
        try:
            workflow_manager = WorkflowManager(sequencer)
            planned_modules = workflow_manager.get_planned_modules()
            print(f"   ✅ WorkflowManager integration successful")
            print(f"   📋 Planned modules: {planned_modules}")
            
        except Exception as e:
            print(f"   ❌ WorkflowManager integration failed: {e}")
            traceback.print_exc()
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ ModuleSequencer debug failed: {e}")
        traceback.print_exc()
        return 1


def debug_directory_config():
    """Debug command: Test DirectoryConfig integration."""
    print("🔍 Debug: DirectoryConfig Integration")
    print("=" * 50)
    
    try:
        print("🚀 Testing DirectoryConfig import...")
        try:
            from asciidoc_dita_toolkit.asciidoc_dita.plugins.DirectoryConfig import (
                load_directory_config, get_filtered_adoc_files, DirectoryConfigModule
            )
            from asciidoc_dita_toolkit.asciidoc_dita.file_utils import find_adoc_files
            print("   ✅ DirectoryConfig imports successful")
        except ImportError as e:
            print(f"   ❌ DirectoryConfig import failed: {e}")
            return 1
        
        # Test configuration loading
        print("\n⚙️  Testing configuration loading...")
        try:
            config = load_directory_config()
            if config:
                print(f"   ✅ Configuration loaded: {type(config)}")
                if isinstance(config, dict):
                    print(f"   📋 Config keys: {list(config.keys())}")
            else:
                print("   ℹ️  No configuration found (this may be normal)")
        except Exception as e:
            print(f"   ⚠️  Configuration loading error: {e}")
        
        # Test file discovery in current directory
        print(f"\n📂 Testing file discovery in current directory...")
        current_dir = Path.cwd()
        print(f"   Current directory: {current_dir}")
        
        try:
            # Test basic file discovery
            basic_files = find_adoc_files(str(current_dir))
            print(f"   📄 Basic discovery: {len(basic_files)} .adoc files")
            
            # Test filtered discovery
            if config:
                filtered_files = get_filtered_adoc_files(str(current_dir), config, find_adoc_files)
                print(f"   🔍 Filtered discovery: {len(filtered_files)} .adoc files")
                
                if len(filtered_files) != len(basic_files):
                    print(f"   📊 Filtering effect: {len(basic_files) - len(filtered_files)} files filtered out")
            else:
                print("   ℹ️  No config available for filtered discovery")
            
            # Show sample files
            if basic_files:
                print(f"   📋 Sample files found:")
                for f in basic_files[:5]:
                    print(f"      - {Path(f).relative_to(current_dir)}")
                if len(basic_files) > 5:
                    print(f"      ... and {len(basic_files) - 5} more")
            
        except Exception as e:
            print(f"   ❌ File discovery failed: {e}")
            traceback.print_exc()
        
        # Test DirectoryConfig module initialization
        print(f"\n🧩 Testing DirectoryConfig module...")
        try:
            module = DirectoryConfigModule()
            print(f"   ✅ Module created: {module.name} v{module.version}")
            print(f"   📋 Dependencies: {module.dependencies}")
            print(f"   🏷️  Release status: {module.release_status}")
            
            # Test initialization
            init_result = module.initialize({})
            print(f"   🚀 Initialization: {init_result}")
            
        except Exception as e:
            print(f"   ❌ DirectoryConfig module test failed: {e}")
            traceback.print_exc()
        
        # Test environment variable
        print(f"\n🌍 Environment check...")
        env_var = "ADT_ENABLE_DIRECTORY_CONFIG"
        env_value = os.environ.get(env_var)
        if env_value:
            print(f"   ✅ {env_var}={env_value}")
        else:
            print(f"   ℹ️  {env_var} not set (DirectoryConfig may be disabled)")
            print(f"   💡 To enable: export {env_var}=true")
        
        return 0
        
    except Exception as e:
        print(f"❌ DirectoryConfig debug failed: {e}")
        traceback.print_exc()
        return 1


def debug_test_storage():
    """Debug command: Test storage system and permissions."""
    print("🔍 Debug: Storage System")
    print("=" * 50)
    
    try:
        # Test storage directory
        print("📁 Testing storage directory...")
        storage_dir = Path.home() / ".adt" / "workflows"
        print(f"   Storage path: {storage_dir}")
        
        # Check if directory exists
        if storage_dir.exists():
            print(f"   ✅ Directory exists")
            print(f"   📊 Is directory: {storage_dir.is_dir()}")
            
            # Check permissions
            print(f"   🔐 Readable: {os.access(storage_dir, os.R_OK)}")
            print(f"   🔐 Writable: {os.access(storage_dir, os.W_OK)}")
            print(f"   🔐 Executable: {os.access(storage_dir, os.X_OK)}")
            
            # List existing workflows
            json_files = list(storage_dir.glob("*.json"))
            print(f"   📄 Existing workflows: {len(json_files)}")
            for f in json_files:
                print(f"      - {f.name}")
        else:
            print(f"   ℹ️  Directory does not exist (will be created on first use)")
            
            # Test creation
            try:
                storage_dir.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Directory created successfully")
                
                # Clean up test directory if it was empty
                if not list(storage_dir.glob("*")):
                    storage_dir.rmdir()
                    storage_dir.parent.rmdir() if not list(storage_dir.parent.glob("*")) else None
                    print(f"   🧹 Test directory cleaned up")
                    
            except Exception as e:
                print(f"   ❌ Cannot create directory: {e}")
                return 1
        
        # Test workflow state creation and persistence
        print(f"\n💾 Testing workflow state persistence...")
        
        test_workflow_name = f"debug_test_{int(datetime.now().timestamp())}"
        test_directory = Path.cwd()
        
        try:
            # Create test workflow
            print(f"   🚀 Creating test workflow: {test_workflow_name}")
            workflow = WorkflowState(test_workflow_name, str(test_directory), ["DirectoryConfig", "ContentType"])
            
            # Test save
            print(f"   💾 Testing save...")
            workflow.save_to_disk()
            
            storage_path = workflow.get_storage_path()
            if storage_path.exists():
                print(f"   ✅ Save successful: {storage_path}")
                print(f"   📊 File size: {storage_path.stat().st_size} bytes")
            else:
                print(f"   ❌ Save failed: file not created")
                return 1
            
            # Test load
            print(f"   📖 Testing load...")
            loaded_workflow = WorkflowState.load_from_disk(test_workflow_name)
            
            if loaded_workflow.name == test_workflow_name:
                print(f"   ✅ Load successful: {loaded_workflow.name}")
            else:
                print(f"   ❌ Load failed: name mismatch")
                return 1
            
            # Test data integrity
            print(f"   🔍 Testing data integrity...")
            if loaded_workflow.directory == workflow.directory:
                print(f"   ✅ Directory preserved: {loaded_workflow.directory}")
            else:
                print(f"   ❌ Directory mismatch: {loaded_workflow.directory} != {workflow.directory}")
            
            if len(loaded_workflow.modules) == len(workflow.modules):
                print(f"   ✅ Module count preserved: {len(loaded_workflow.modules)}")
            else:
                print(f"   ❌ Module count mismatch: {len(loaded_workflow.modules)} != {len(workflow.modules)}")
            
            # Test update and save
            print(f"   🔄 Testing update and save...")
            loaded_workflow.status = "test_updated"
            loaded_workflow.save_to_disk()
            
            # Load again and verify update
            updated_workflow = WorkflowState.load_from_disk(test_workflow_name)
            if updated_workflow.status == "test_updated":
                print(f"   ✅ Update successful: {updated_workflow.status}")
            else:
                print(f"   ❌ Update failed: {updated_workflow.status}")
            
            # Clean up test workflow
            print(f"   🧹 Cleaning up test workflow...")
            storage_path.unlink()
            print(f"   ✅ Test workflow deleted")
            
        except Exception as e:
            print(f"   ❌ Storage test failed: {e}")
            traceback.print_exc()
            
            # Try to clean up
            try:
                test_storage_path = storage_dir / f"{test_workflow_name}.json"
                if test_storage_path.exists():
                    test_storage_path.unlink()
            except:
                pass
            
            return 1
        
        print(f"\n✅ Storage system is working correctly")
        return 0
        
    except Exception as e:
        print(f"❌ Storage debug failed: {e}")
        traceback.print_exc()
        return 1


def main():
    """Main debug script entry point."""
    if not IMPORTS_SUCCESSFUL:
        print("Cannot run debug utilities due to import errors.")
        return 1
    
    parser = argparse.ArgumentParser(
        description="Debug utilities for UserJourney Plugin",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python debug_user_journey.py list                   # List all workflows
    python debug_user_journey.py workflow my-project    # Debug specific workflow
    python debug_user_journey.py sequencing             # Test ModuleSequencer
    python debug_user_journey.py directory-config       # Test DirectoryConfig
    python debug_user_journey.py test-storage           # Test storage system
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Debug commands')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List all workflows with detailed information')
    
    # workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Debug specific workflow')
    workflow_parser.add_argument('name', help='Workflow name to debug')
    
    # sequencing command
    sequencing_parser = subparsers.add_parser('sequencing', help='Test ModuleSequencer integration')
    
    # directory-config command
    dirconfig_parser = subparsers.add_parser('directory-config', help='Test DirectoryConfig integration')
    
    # test-storage command
    storage_parser = subparsers.add_parser('test-storage', help='Test storage system and permissions')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate debug function
    if args.command == 'list':
        return debug_list_workflows()
    elif args.command == 'workflow':
        return debug_specific_workflow(args.name)
    elif args.command == 'sequencing':
        return debug_module_sequencing()
    elif args.command == 'directory-config':
        return debug_directory_config()
    elif args.command == 'test-storage':
        return debug_test_storage()
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Debug interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)
