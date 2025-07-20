# ADT UserJourney Plugin MVP Implementation Guide

This document provides step-by-step instructions for implementing the ADT UserJourney plugin using AI-assisted development tools such as GitHub Copilot or Claude Sonnet 4. The plugin orchestrates multi-module document processing workflows for technical writers.

**IMPORTANT**: Feed these instructions in sequential chunks to maintain context and ensure successful implementation.

---

## MVP Scope Definition

### Core MVP Features (Phase 1)
1. **Basic workflow state management** - Start, resume, status tracking with JSON persistence
2. **Simple module sequencing** - Execute modules using ModuleSequencer in dependency order  
3. **Checkpoint persistence** - Atomic saves survive interruptions and system restarts
4. **CLI interface** - `adt journey` commands integrated with main ADT CLI
5. **Progress visualization** - Clear status display with emoji indicators and next actions

### Explicitly Excluded from MVP
- Git integration (branches, PRs, merges) → Phase 2
- Interactive module flagging/resolution → Phase 3  
- Workflow templates and team collaboration → Phase 4
- External tool integrations (Jira, etc.) → Phase 4

**Key Insight**: UserJourney differs from content-processing plugins - it **orchestrates other plugins** rather than processing AsciiDoc content directly.

---

## CHUNK 1: Initial Setup and Architecture

### Plugin Overview
Create the **UserJourney** plugin that provides opinionated workflow orchestration for technical writers processing large document sets through multiple ADT modules.

**Critical Architecture Decision**: UserJourney is a **CLI orchestrator**, not a module in the sequencing chain. It uses ModuleSequencer to execute other modules but is not executed by ModuleSequencer.

### Required Files Structure
```
modules/user_journey.py                                # UserJourneyModule wrapper (for CLI integration only)
asciidoc_dita_toolkit/asciidoc_dita/plugins/UserJourney.py  # Core workflow orchestration logic
tests/fixtures/UserJourney/                           # Test fixtures
├── workflow_basic.json                               # Basic workflow state test
├── workflow_interrupted.json                        # Interruption/resume test  
├── workflow_dependencies.json                       # Module dependency test
├── module_execution_success.test                    # Successful execution scenario
├── module_execution_failure.test                    # Error handling scenario
└── cli_integration_*.test                           # CLI command integration tests
```

### Architecture Pattern Differences
**Unlike content-processing plugins**, UserJourney has these unique characteristics:

1. **CLI-First**: Primary interface is `adt journey` commands, not module execution
2. **Orchestrator Role**: Calls ModuleSequencer to execute other modules
3. **State-Heavy**: Maintains complex workflow state across sessions
4. **No AsciiDoc Processing**: Does not directly process content files
5. **User Interaction**: Provides status, guidance, and progress tracking

### Key Implementation Classes
```python
# Workflow state management (persistent JSON)
class WorkflowState:
    def __init__(self, name: str, directory: str, modules: List[str])
    def save_to_disk(self) -> None                     # Atomic JSON persistence
    def load_from_disk(cls, name: str) -> 'WorkflowState'
    def get_next_module(self) -> Optional[str]         # Dependency-aware next module
    def mark_module_completed(self, module_name: str) -> None
    def get_progress_summary(self) -> Dict[str, Any]   # For status display

# Workflow orchestration (ModuleSequencer integration)
class WorkflowManager:
    def __init__(self, module_sequencer: ModuleSequencer)
    def start_workflow(self, name: str, directory: str) -> WorkflowState
    def resume_workflow(self, name: str) -> WorkflowState
    def execute_next_module(self, workflow: WorkflowState) -> ExecutionResult
    def get_workflow_status(self, workflow: WorkflowState) -> StatusDisplay
    def list_available_workflows(self) -> List[str]

# CLI command processor (integrates with main ADT CLI)
class UserJourneyProcessor:
    def __init__(self, workflow_manager: WorkflowManager)
    def process_start_command(self, args: StartArgs) -> None
    def process_resume_command(self, args: ResumeArgs) -> None  
    def process_status_command(self, args: StatusArgs) -> None
    def process_continue_command(self, args: ContinueArgs) -> None
    def process_list_command(self, args: ListArgs) -> None
```

**Implementation Note**: Start with CHUNK 1-2 for core architecture, then proceed sequentially through remaining chunks.

---

## CHUNK 2: Workflow State Management

### Critical State Management Requirements
The UserJourney plugin must handle complex state persistence across interruptions:

1. **Atomic Persistence**: Every state change must be atomically saved to prevent corruption
2. **Module Dependencies**: Leverage ModuleSequencer for correct dependency ordering
3. **File Discovery**: Use DirectoryConfig integration for scoped file discovery
4. **Progress Tracking**: Detailed metrics for user progress visualization
5. **Error Recovery**: Graceful handling of module failures with retry capabilities

### Essential State Management Implementation
**CRITICAL**: DirectoryConfig is now required and first in the module chain. UserJourney must integrate with it.

```python
class WorkflowState:
    def __init__(self, name: str, directory: str, modules: List[str]):
        self.name = name
        self.directory = Path(directory).resolve()
        self.created = datetime.now().isoformat()
        self.last_activity = self.created
        self.status = "active"  # active, completed, failed, paused
        self.modules = self._initialize_module_states(modules)
        self.files_discovered = self._discover_target_files()
        self.directory_config = self._load_directory_config()
    
    def _initialize_module_states(self, modules: List[str]) -> Dict[str, ModuleState]:
        """Create state tracking for each module with detailed metrics."""
        return {
            module: {
                "status": "pending",  # pending, running, completed, failed, skipped
                "started_at": None,
                "completed_at": None, 
                "files_processed": 0,
                "files_modified": 0,
                "execution_time": None,
                "error_message": None,
                "retry_count": 0,
                "user_interaction_required": False
            }
            for module in modules
        }
    
    def _discover_target_files(self) -> List[str]:
        """Discover .adoc files using DirectoryConfig if available."""
        try:
            # Import DirectoryConfig functionality
            from asciidoc_dita_toolkit.asciidoc_dita.plugins.DirectoryConfig import (
                load_directory_config, get_filtered_adoc_files
            )
            from asciidoc_dita_toolkit.asciidoc_dita.file_utils import find_adoc_files
            
            # Try DirectoryConfig first (it's required now)
            config = load_directory_config()
            if config:
                return get_filtered_adoc_files(str(self.directory), config, find_adoc_files)
            else:
                # Fallback to simple discovery
                return list(self.directory.rglob("*.adoc"))
        except ImportError:
            # Fallback if DirectoryConfig not available
            return list(self.directory.rglob("*.adoc"))
    
    def _load_directory_config(self) -> Optional[Dict]:
        """Load DirectoryConfig for workflow context."""
        try:
            from asciidoc_dita_toolkit.asciidoc_dita.plugins.DirectoryConfig import load_directory_config
            return load_directory_config()
        except ImportError:
            return None
    
    def get_storage_path(self) -> Path:
        """Get storage path with proper directory creation."""
        storage_dir = Path.home() / ".adt" / "workflows"
        storage_dir.mkdir(parents=True, exist_ok=True)
        return storage_dir / f"{self.name}.json"
```

### Atomic State Persistence Pattern
```python
def save_to_disk(self) -> None:
    """Save workflow state with atomic write and error recovery."""
    self.last_activity = datetime.now().isoformat()
    storage_path = self.get_storage_path()
    
    # Atomic write pattern: temp file → rename
    temp_path = storage_path.with_suffix('.tmp')
    backup_path = storage_path.with_suffix('.backup')
    
    try:
        # Create backup of existing state
        if storage_path.exists():
            shutil.copy2(storage_path, backup_path)
        
        # Write to temp file
        with open(temp_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, sort_keys=True)
        
        # Atomic rename
        temp_path.rename(storage_path)
        
        # Clean up backup on success
        if backup_path.exists():
            backup_path.unlink()
            
    except Exception as e:
        # Restore from backup if available
        if backup_path.exists() and not storage_path.exists():
            shutil.copy2(backup_path, storage_path)
        raise WorkflowStateError(f"Failed to save workflow state: {e}")

@classmethod
def load_from_disk(cls, name: str) -> 'WorkflowState':
    """Load workflow state with validation and migration."""
    storage_path = Path.home() / ".adt" / "workflows" / f"{name}.json"
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
```

### State Management Checklist
- [ ] Atomic state persistence with temp file + rename pattern
- [ ] Backup and recovery for corrupted state files
- [ ] State format validation and migration support
- [ ] DirectoryConfig integration for file discovery
- [ ] Detailed module execution metrics tracking
- [ ] Error recovery with retry count tracking
- [ ] Clean storage directory management

---

## CHUNK 3: Module Orchestration and Integration

### Module Execution Logic
**CRITICAL**: UserJourney orchestrates existing ADT modules, not content processing directly.

```python
class WorkflowManager:
    def __init__(self, module_sequencer: ModuleSequencer):
        self.sequencer = module_sequencer
        self.sequencer.load_configurations()  # Load ADT module configs
        self.sequencer.discover_modules()     # Discover available modules
    
    def execute_next_module(self, workflow: WorkflowState) -> ExecutionResult:
        """Execute the next pending module in dependency order."""
        next_module = workflow.get_next_module()
        if not next_module:
            return ExecutionResult(status="completed", message="All modules completed")
        
        # Update workflow state
        workflow.mark_module_started(next_module)
        workflow.save_to_disk()
        
        try:
            # Execute module through ModuleSequencer
            execution_context = {
                "directory": str(workflow.directory),
                "recursive": True,
                "files": [str(f) for f in workflow.files_discovered]
            }
            
            module_result = self.sequencer.execute_module(next_module, execution_context)
            
            # Update workflow state with results
            workflow.mark_module_completed(next_module, module_result)
            workflow.save_to_disk()
            
            return ExecutionResult(
                status="success",
                message=f"{next_module} completed successfully",
                files_processed=module_result.files_processed,
                next_action=workflow.get_next_action()
            )
            
        except Exception as e:
            workflow.mark_module_failed(next_module, str(e))
            workflow.save_to_disk()
            raise WorkflowExecutionError(f"Module {next_module} failed: {e}")
```

### CLI Command Processing with Enhanced UX
Model after existing ADT CLI patterns with rich user feedback:

```python
class UserJourneyProcessor:
    def process_start_command(self, args: StartArgs) -> None:
        """Handle: adt journey start --name=X --directory=Y"""
        if self.workflow_exists(args.name):
            raise WorkflowExistsError(f"Workflow '{args.name}' already exists. Use 'adt journey resume --name={args.name}' to continue.")
        
        # Validate directory with helpful error messages
        directory = Path(args.directory).resolve()
        if not directory.exists():
            raise InvalidDirectoryError(f"Directory '{directory}' not found. Please check the path and try again.")
        if not directory.is_dir():
            raise InvalidDirectoryError(f"'{directory}' is not a directory. Please specify a directory path.")
        
        # Check for .adoc files
        adoc_files = list(directory.rglob("*.adoc"))
        if not adoc_files:
            print(f"⚠️  No .adoc files found in '{directory}'. Are you sure this is the right directory?")
            response = input("Continue anyway? (y/n): ").lower()
            if response != 'y':
                print("Cancelled.")
                return
        
        # Determine module sequence using ModuleSequencer
        planned_modules = self.workflow_manager.get_planned_modules()
        
        # Create and start workflow
        workflow = self.workflow_manager.start_workflow(args.name, directory)
        
        # Rich user feedback with emojis and clear next steps
        print(f"✨ Created workflow '{args.name}'")
        print(f"📁 Directory: {directory}")
        print(f"📄 Files discovered: {len(workflow.files_discovered)}")
        print(f"📊 Planned modules: {' → '.join(planned_modules)}")
        print()
        
        # Handle DirectoryConfig as special case (it's interactive)
        if planned_modules and planned_modules[0] == "DirectoryConfig":
            print("🔧 First step: Directory Configuration")
            print("   DirectoryConfig will help you define which directories to process.")
            print("   This is an interactive setup that may ask for your input.")
            print()
            
            try:
                result = self.workflow_manager.execute_next_module(workflow)
                if result.status == "success":
                    print(f"✅ DirectoryConfig completed")
                    remaining_modules = [m for m in planned_modules if m != "DirectoryConfig"]
                    if remaining_modules:
                        print(f"📋 Next: {remaining_modules[0]}")
                        print(f"   Run: adt journey continue --name='{args.name}'")
                    else:
                        print("🎉 Workflow completed!")
                else:
                    print(f"❌ DirectoryConfig failed: {result.error_message}")
                    print("   Fix the issue and run: adt journey continue --name='{args.name}'")
            except Exception as e:
                print(f"❌ Error during DirectoryConfig: {e}")
                print("   Check the error above and run: adt journey continue --name='{args.name}'")
        else:
            # Non-interactive first module
            print(f"🔄 Starting with {planned_modules[0]}...")
            try:
                result = self.workflow_manager.execute_next_module(workflow)
                print(f"✅ {result.message}")
                print(f"📋 Next: {result.next_action}")
            except Exception as e:
                print(f"❌ Error: {e}")
                print(f"   Run: adt journey continue --name='{args.name}' to retry")
    
    def process_status_command(self, args: StatusArgs) -> None:
        """Handle: adt journey status [--name=X]"""
        if args.name:
            # Show specific workflow status
            try:
                workflow = WorkflowState.load_from_disk(args.name)
                self._display_workflow_status(workflow)
            except WorkflowNotFoundError:
                print(f"❌ Workflow '{args.name}' not found.")
                available = self.workflow_manager.list_available_workflows()
                if available:
                    print(f"Available workflows: {', '.join(available)}")
                else:
                    print("No workflows found. Create one with: adt journey start --name=<name> --directory=<path>")
        else:
            # Show all workflows
            workflows = self.workflow_manager.list_available_workflows()
            if not workflows:
                print("No workflows found.")
                print("Create your first workflow with: adt journey start --name=<name> --directory=<path>")
                return
            
            print("Active Workflows:")
            print("=" * 50)
            for workflow_name in workflows:
                try:
                    workflow = WorkflowState.load_from_disk(workflow_name)
                    status_emoji = self._get_status_emoji(workflow.status)
                    last_activity = datetime.fromisoformat(workflow.last_activity).strftime("%Y-%m-%d %H:%M")
                    print(f"{status_emoji} {workflow_name} ({workflow.status}) - {last_activity}")
                except Exception:
                    print(f"⚠️  {workflow_name} (corrupted state)")
    
    def _display_workflow_status(self, workflow: WorkflowState) -> None:
        """Display detailed workflow status with visual progress."""
        print(f"Workflow: {workflow.name} ({workflow.directory})")
        print(f"Created: {workflow.created}")
        print(f"Last activity: {workflow.last_activity}")
        print(f"Status: {self._get_status_emoji(workflow.status)} {workflow.status}")
        print(f"Files: {len(workflow.files_discovered)} .adoc files")
        print()
        
        # Module progress with visual indicators
        for module_name, module_state in workflow.modules.items():
            status = module_state["status"]
            emoji = self._get_module_emoji(status)
            
            if status == "completed":
                completed_time = module_state.get("completed_at", "")
                if completed_time:
                    time_str = datetime.fromisoformat(completed_time).strftime("%m-%d %H:%M")
                    print(f"├── {emoji} {module_name} [completed {time_str}]")
                else:
                    print(f"├── {emoji} {module_name} [completed]")
            elif status == "failed":
                error = module_state.get("error_message", "Unknown error")
                retry_count = module_state.get("retry_count", 0)
                retry_info = f" (retry {retry_count})" if retry_count > 0 else ""
                print(f"├── {emoji} {module_name} [failed{retry_info}]")
                print(f"│   └── Error: {error}")
            elif status == "running":
                started = module_state.get("started_at", "")
                if started:
                    time_str = datetime.fromisoformat(started).strftime("%H:%M")
                    print(f"├── {emoji} {module_name} [running since {time_str}]")
                else:
                    print(f"├── {emoji} {module_name} [running]")
            else:  # pending
                print(f"├── {emoji} {module_name} [pending]")
        
        # Next action guidance
        next_module = workflow.get_next_module()
        if next_module:
            print()
            print(f"📋 Next action: Run {next_module}")
            print(f"   Command: adt journey continue --name='{workflow.name}'")
        elif workflow.status == "active":
            print()
            print("🎉 All modules completed!")
        
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for workflow status."""
        return {
            "active": "🔄",
            "completed": "✅", 
            "failed": "❌",
            "paused": "⏸️"
        }.get(status, "❓")
    
    def _get_module_emoji(self, status: str) -> str:
        """Get emoji for module status."""
        return {
            "pending": "⏸️",
            "running": "🔄", 
            "completed": "✅",
            "failed": "❌",
            "skipped": "⏭️"
        }.get(status, "❓")
```

### Integration Points with Current ADT Architecture
```python
# Integration with existing ModuleSequencer and DirectoryConfig
def get_planned_modules(self) -> List[str]:
    """Get module execution order from ModuleSequencer."""
    try:
        resolutions, errors = self.module_sequencer.sequence_modules()
        if errors:
            raise WorkflowPlanningError(f"Module sequencing failed: {errors}")
        
        # Filter to enabled modules in dependency order
        enabled_modules = [r.name for r in resolutions if r.state == ModuleState.ENABLED]
        
        # Verify DirectoryConfig is first (it's required now)
        if enabled_modules and enabled_modules[0] != "DirectoryConfig":
            raise WorkflowPlanningError("DirectoryConfig must be the first module in the sequence")
        
        return enabled_modules
        
    except Exception as e:
        raise WorkflowPlanningError(f"Failed to determine module sequence: {e}")

def execute_module_with_context(self, workflow: WorkflowState, module_name: str) -> ExecutionResult:
    """Execute a specific module with full workflow context."""
    try:
        # Build execution context from workflow state
        execution_context = {
            "directory": str(workflow.directory),
            "recursive": True,
            "files": [str(f) for f in workflow.files_discovered],
            "workflow_name": workflow.name,
            "workflow_state": workflow.to_dict(),
            "directory_config": workflow.directory_config
        }
        
        # Special handling for DirectoryConfig (interactive)
        if module_name == "DirectoryConfig":
            # DirectoryConfig may update the file discovery
            result = self.sequencer.execute_module(module_name, execution_context)
            
            # Refresh file discovery after DirectoryConfig
            workflow.files_discovered = workflow._discover_target_files()
            workflow.directory_config = workflow._load_directory_config()
            
            return result
        else:
            # Standard module execution
            return self.sequencer.execute_module(module_name, execution_context)
            
    except Exception as e:
        return ExecutionResult(
            status="failed", 
            error_message=str(e),
            module_name=module_name
        )
```

**Critical Implementation Notes**:
1. **DirectoryConfig First**: Always execute DirectoryConfig first - it's required and interactive
2. **File Discovery Refresh**: After DirectoryConfig, refresh the file list
3. **Context Propagation**: Pass full workflow context to each module
4. **Error Isolation**: Module failures don't crash the entire workflow

---

## CHUNK 4: Test-Driven Development

### Testing Architecture
Use workflow-focused testing approach:

1. **State Persistence Testing**:
   - Test workflow save/load cycles
   - Test interruption/resume scenarios
   - Validate state consistency

2. **Module Integration Testing**:
   - Mock ModuleSequencer for predictable results
   - Test module execution orchestration
   - Validate dependency resolution

3. **CLI Integration Testing**:
   - Test all CLI commands end-to-end
   - Validate error handling and user feedback
   - Test concurrent workflow scenarios

### Test Implementation Pattern
```python
class TestUserJourney:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.workflow_dir = Path(self.temp_dir) / "workflows"
        self.workflow_dir.mkdir()
        
        # Mock ModuleSequencer
        self.mock_sequencer = Mock()
        self.mock_sequencer.sequence_modules.return_value = (
            [ModuleResolution(name="EntityReference", state=ModuleState.ENABLED, ...)],
            []
        )
        
        self.workflow_manager = WorkflowManager(self.mock_sequencer)
    
    def test_start_workflow_basic(self):
        """Test basic workflow creation."""
        # Create test directory with .adoc files
        test_docs_dir = Path(self.temp_dir) / "test-docs"
        test_docs_dir.mkdir()
        (test_docs_dir / "doc1.adoc").write_text("= Test Document 1")
        (test_docs_dir / "doc2.adoc").write_text("= Test Document 2")
        
        # Start workflow
        workflow = self.workflow_manager.start_workflow("test-workflow", test_docs_dir)
        
        # Verify state
        assert workflow.name == "test-workflow"
        assert len(workflow.files_discovered) == 2
        assert workflow.status == "active"
        assert all(m["status"] == "pending" for m in workflow.modules.values())
        
        # Verify persistence
        loaded_workflow = WorkflowState.load_from_disk("test-workflow")
        assert loaded_workflow.name == workflow.name
        assert loaded_workflow.files_discovered == workflow.files_discovered
    
    def test_resume_interrupted_workflow(self):
        """Test resuming after interruption."""
        # Create and partially execute workflow
        workflow = self.workflow_manager.start_workflow("interrupted-test", self.temp_dir)
        
        # Simulate partial execution
        workflow.mark_module_started("EntityReference")
        workflow.mark_module_completed("EntityReference", mock_result)
        workflow.save_to_disk()
        
        # Resume workflow
        resumed_workflow = self.workflow_manager.resume_workflow("interrupted-test")
        
        # Verify state continuity
        assert resumed_workflow.modules["EntityReference"]["status"] == "completed"
        assert resumed_workflow.get_next_module() == "CrossReference"
    
    def test_cli_commands(self):
        """Test CLI command processing."""
        processor = UserJourneyProcessor(self.workflow_manager)
        
        # Test start command
        start_args = StartArgs(name="cli-test", directory=str(self.temp_dir))
        processor.process_start_command(start_args)
        
        # Verify workflow was created
        workflow = WorkflowState.load_from_disk("cli-test")
        assert workflow.name == "cli-test"
        
        # Test status command
        status_args = StatusArgs(name="cli-test")
        output = processor.process_status_command(status_args)
        assert "cli-test" in output
        assert "pending" in output or "completed" in output
```

### Test Fixture Categories
- `workflow_*.json`: Workflow state test data at various stages
- `module_execution_*.test`: Mock module execution scenarios
- `cli_integration_*.test`: End-to-end CLI command tests
- `error_scenarios_*.test`: Error handling and recovery tests

---

## CHUNK 5: Integration and Debugging

### ADT System Integration
1. **Update `pyproject.toml`**:
   ```toml
   [project.entry-points."adt.modules"]
   UserJourney = "modules.user_journey:UserJourneyModule"
   ```

2. **CLI Command Registration** in main ADT CLI (`asciidoc_dita_toolkit/asciidoc_dita/cli.py`):
   ```python
   # Add UserJourney commands to main CLI
   def add_journey_commands(parser):
       """Add journey subcommands to main parser."""
       journey_parser = parser.add_parser('journey', 
                                          help='Workflow orchestration for multi-module processing',
                                          description='Guide technical writers through complete document processing workflows')
       journey_subparsers = journey_parser.add_subparsers(dest='journey_command', 
                                                          help='Available workflow commands')
       
       # journey start
       start_parser = journey_subparsers.add_parser('start', 
                                                   help='Start new workflow',
                                                   description='Create and start a new document processing workflow')
       start_parser.add_argument('--name', required=True, 
                               help='Unique workflow name (e.g., "q2-docs-update")')
       start_parser.add_argument('--directory', required=True, 
                               help='Target directory containing .adoc files')
       start_parser.add_argument('--force', action='store_true',
                               help='Overwrite existing workflow with same name')
       
       # journey resume  
       resume_parser = journey_subparsers.add_parser('resume', 
                                                    help='Resume interrupted workflow')
       resume_parser.add_argument('--name', required=True, 
                                help='Name of workflow to resume')
       
       # journey status
       status_parser = journey_subparsers.add_parser('status', 
                                                    help='Show workflow status')
       status_parser.add_argument('--name', 
                                help='Specific workflow name (shows all if omitted)')
       status_parser.add_argument('--verbose', '-v', action='store_true',
                                help='Show detailed module information')
       
       # journey continue
       continue_parser = journey_subparsers.add_parser('continue', 
                                                      help='Continue workflow execution')
       continue_parser.add_argument('--name', required=True, 
                                  help='Name of workflow to continue')
       continue_parser.add_argument('--skip-current', action='store_true',
                                  help='Skip current failed module and proceed')
       
       # journey list
       list_parser = journey_subparsers.add_parser('list', 
                                                  help='List all workflows')
       list_parser.add_argument('--status', 
                               choices=['active', 'completed', 'failed', 'paused'],
                               help='Filter by workflow status')
       
       # journey cleanup
       cleanup_parser = journey_subparsers.add_parser('cleanup',
                                                     help='Clean up old workflow files')
       cleanup_parser.add_argument('--older-than', type=int, default=30,
                                  help='Remove workflows older than N days (default: 30)')
       cleanup_parser.add_argument('--dry-run', action='store_true',
                                  help='Show what would be deleted without deleting')
   ```

3. **Module Configuration**: 
   ```json
   // UserJourney is NOT in .adt-modules.json - it's a CLI orchestrator, not a sequenced module
   // It orchestrates the modules defined in .adt-modules.json
   ```

### Debug Utilities for Development
Create `debug_user_journey.py` in project root:

```python
#!/usr/bin/env python3
"""Debug utilities for UserJourney plugin development."""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_workflow_state(workflow_name: str):
    """Debug workflow state and module dependencies."""
    try:
        from asciidoc_dita_toolkit.asciidoc_dita.plugins.UserJourney import WorkflowState
        
        workflow = WorkflowState.load_from_disk(workflow_name)
        print(f"🔍 Debugging Workflow: {workflow.name}")
        print(f"📁 Directory: {workflow.directory}")
        print(f"📄 Files discovered: {len(workflow.files_discovered)}")
        print(f"📊 Status: {workflow.status}")
        print(f"🕐 Created: {workflow.created}")
        print(f"🕐 Last activity: {workflow.last_activity}")
        print()
        
        print("📋 Module States:")
        for module_name, module_state in workflow.modules.items():
            status = module_state["status"] 
            emoji = {"pending": "⏸️", "running": "🔄", "completed": "✅", "failed": "❌"}.get(status, "❓")
            print(f"  {emoji} {module_name}: {status}")
            
            if module_state.get("error_message"):
                print(f"    💥 Error: {module_state['error_message']}")
            if module_state.get("files_processed"):
                print(f"    📊 Files processed: {module_state['files_processed']}")
                
        print()
        next_module = workflow.get_next_module()
        if next_module:
            print(f"➡️  Next module: {next_module}")
        else:
            print("✅ All modules completed!")
            
    except Exception as e:
        print(f"❌ Error loading workflow '{workflow_name}': {e}")
        list_available_workflows()

def list_available_workflows():
    """List all available workflows with status."""
    workflow_dir = Path.home() / ".adt" / "workflows"
    if not workflow_dir.exists():
        print("📂 No workflows directory found")
        return
        
    workflow_files = list(workflow_dir.glob("*.json"))
    if not workflow_files:
        print("📂 No workflows found")
        return
        
    print("📋 Available workflows:")
    for workflow_file in sorted(workflow_files):
        workflow_name = workflow_file.stem
        try:
            with open(workflow_file) as f:
                data = json.load(f)
            status = data.get("status", "unknown")
            last_activity = data.get("last_activity", "unknown")
            print(f"  • {workflow_name} ({status}) - {last_activity}")
        except Exception as e:
            print(f"  ⚠️ {workflow_name} (corrupted: {e})")

def debug_module_sequencing():
    """Debug ModuleSequencer integration."""
    try:
        from src.adt_core.module_sequencer import ModuleSequencer
        
        print("🔍 Debugging ModuleSequencer integration...")
        sequencer = ModuleSequencer()
        
        # Load configurations
        print("📋 Loading configurations...")
        sequencer.load_configurations()
        
        # Discover modules  
        print("🔍 Discovering modules...")
        sequencer.discover_modules()
        
        # Get sequence
        print("📊 Sequencing modules...")
        resolutions, errors = sequencer.sequence_modules()
        
        if errors:
            print(f"❌ Sequencing errors: {errors}")
        else:
            print("✅ Module sequence:")
            for i, resolution in enumerate(resolutions, 1):
                status_emoji = "✅" if resolution.state.value == "enabled" else "⏸️"
                print(f"  {i}. {status_emoji} {resolution.name} (v{resolution.version})")
                if resolution.dependencies:
                    print(f"     📋 Depends on: {', '.join(resolution.dependencies)}")
        
    except Exception as e:
        print(f"❌ Error debugging module sequencing: {e}")
        import traceback
        traceback.print_exc()

def debug_directory_config():
    """Debug DirectoryConfig integration."""
    try:
        from asciidoc_dita_toolkit.asciidoc_dita.plugins.DirectoryConfig import load_directory_config
        
        print("🔍 Debugging DirectoryConfig integration...")
        config = load_directory_config()
        
        if config:
            print("✅ DirectoryConfig loaded:")
            print(f"  📁 Repository root: {config.get('repoRoot', 'Not set')}")
            print(f"  📋 Include dirs: {config.get('includeDirs', []) or 'All directories'}")
            print(f"  🚫 Exclude dirs: {config.get('excludeDirs', []) or 'None'}")
        else:
            print("⚠️ No DirectoryConfig found")
            print("   Run: export ADT_ENABLE_DIRECTORY_CONFIG=true && adt DirectoryConfig")
            
    except Exception as e:
        print(f"❌ Error debugging DirectoryConfig: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python debug_user_journey.py list")
        print("  python debug_user_journey.py workflow <name>") 
        print("  python debug_user_journey.py sequencing")
        print("  python debug_user_journey.py directory-config")
        sys.exit(1)
    
    command = sys.argv[1]
    if command == "list":
        list_available_workflows()
    elif command == "workflow" and len(sys.argv) > 2:
        debug_workflow_state(sys.argv[2])
    elif command == "sequencing":
        debug_module_sequencing()
    elif command == "directory-config":
        debug_directory_config()
    else:
        print("Unknown command. Use: list, workflow <name>, sequencing, or directory-config")
```

### Common Implementation Issues and Solutions
1. **State Corruption**: Use atomic writes and backup recovery
2. **Module Integration**: Mock ModuleSequencer properly during testing
3. **CLI Integration**: Handle all argument parsing edge cases
4. **File Discovery**: Handle permissions, empty directories, non-existent paths
5. **DirectoryConfig Integration**: Handle both enabled and disabled states
6. **Concurrency**: Use file locking for workflow state if multiple processes possible

### Development Workflow
1. **Start with state management**: Get WorkflowState working first
2. **Add CLI integration**: Basic start/status commands
3. **Integrate ModuleSequencer**: Mock it initially for testing
4. **Add rich UX**: Emojis, progress indicators, helpful error messages
5. **Test edge cases**: Corrupted state, missing modules, permission issues
6. **Debug utilities**: Essential for development and troubleshooting

---

## CHUNK 6: MVP Implementation Checklist

### Development Process
1. [ ] Create UserJourneyModule wrapper following ADTModule pattern
2. [ ] Implement WorkflowState class with persistence
3. [ ] Implement WorkflowManager class with ModuleSequencer integration
4. [ ] Implement UserJourneyProcessor for CLI commands
5. [ ] Create comprehensive test suite for all scenarios
6. [ ] Add debug utilities for development troubleshooting
7. [ ] Integrate CLI commands with main ADT command structure
8. [ ] Test end-to-end workflow scenarios

### MVP Quality Checklist
- [ ] Workflow state persists across system restarts
- [ ] Module dependencies resolved correctly via ModuleSequencer  
- [ ] All CLI commands work with proper error handling
- [ ] Interrupted workflows resume from correct state
- [ ] Clear progress display shows next actions
- [ ] Handle edge cases (no files, invalid directories, etc.)
- [ ] Comprehensive test coverage for core functionality

### MVP Success Criteria
1. **Basic Orchestration**: Can start workflow and execute modules in sequence
2. **State Persistence**: Survives interruptions and system restarts
3. **Progress Visibility**: Users always know current status and next actions
4. **Error Recovery**: Graceful handling of failures with clear error messages
5. **CLI Integration**: Natural integration with existing `adt` command structure

### Beyond MVP (Future Phases)
- **Phase 2**: Git integration (branches, PRs, merge tracking)
- **Phase 3**: Interactive module resolution and file flagging
- **Phase 4**: Workflow templates, team collaboration, external integrations

---

## Usage Instructions for AI-Assisted Implementation

### Implementation Sequence
1. **CHUNK 1-2 First**: Implement core state management and persistence - this is the foundation
2. **CHUNK 3**: Build module orchestration and CLI integration - the core functionality
3. **CHUNK 4**: Develop comprehensive test suite - essential for reliability
4. **CHUNK 5-6**: Integrate with ADT system and add debug utilities - polish and integration

### Critical Success Factors
1. **DirectoryConfig Integration**: Remember it's required, first, and interactive
2. **Atomic State Management**: Use temp file + rename pattern for all state saves  
3. **Rich User Experience**: Emojis, clear messages, helpful error guidance
4. **ModuleSequencer Integration**: UserJourney orchestrates, doesn't get orchestrated
5. **Error Recovery**: Graceful handling with backup/restore capabilities

### Key MVP Differences from Content Plugins
- **CLI-First Architecture**: Primary interface is commands, not module execution
- **Orchestrator Pattern**: Calls ModuleSequencer to execute other modules
- **State-Heavy Design**: Complex persistent workflow state vs. stateless processing
- **User Guidance Focus**: Progress tracking, next actions, error recovery
- **Integration Dependencies**: Success requires proper ModuleSequencer and DirectoryConfig integration

### Testing Strategy
- **State Persistence**: Save/load/resume cycles with corruption scenarios
- **Module Integration**: Mock ModuleSequencer for predictable test results  
- **CLI Integration**: Full end-to-end command testing
- **Error Scenarios**: Module failures, corrupted state, missing files
- **User Experience**: Progress display, helpful error messages

### Implementation Validation
Before marking MVP complete, verify:
- [ ] Workflow state survives system restarts
- [ ] DirectoryConfig integration works (interactive setup)
- [ ] Module execution follows dependency order
- [ ] Rich status display with emojis and guidance
- [ ] Error recovery with backup restoration
- [ ] CLI commands integrate naturally with main `adt` command
- [ ] Debug utilities work for troubleshooting

**Remember**: This plugin transforms ADT from individual tools into a cohesive workflow platform. Success is measured by user experience, not just technical functionality.

### Beyond MVP Enhancement Path
- **Phase 2**: Git integration (branches, PRs, merge tracking)
- **Phase 3**: Interactive module resolution and file flagging  
- **Phase 4**: Workflow templates, team collaboration, external integrations

The MVP provides the foundation for all future enhancements while delivering immediate value to technical writers processing large document sets.
