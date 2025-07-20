# ADT UserJourney Plugin MVP Implementation Guide for AI-Assisted Development

This document provides structured instructions for AI assistants to help implement the ADT UserJourney plugin. The plugin orchestrates multi-module document processing workflows for technical writers.

**USAGE**: Feed these instructions to AI assistants in sequential chunks. Each chunk is self-contained with clear objectives and success criteria.

---

## Executive Summary

### What is UserJourney?
A workflow orchestration plugin that guides technical writers through multi-module document processing, providing state management, progress tracking, and interruption recovery.

### Key Differentiator
Unlike other ADT plugins that process content, UserJourney **orchestrates other plugins** - it's a conductor, not a performer.

### MVP Deliverables
1. Persistent workflow state management
2. Module execution orchestration via ModuleSequencer
3. CLI command interface (`adt journey`)
4. Progress visualization and status tracking
5. Interruption recovery and resume capability

---

## Implementation Chunks Overview

| Chunk | Focus Area | Dependencies | Estimated Effort |
|-------|------------|--------------|------------------|
| 1 | Architecture & Setup | None | 2-3 hours |
| 2 | State Management | Chunk 1 | 3-4 hours |
| 3 | Module Orchestration & CLI | Chunks 1-2 | 4-5 hours |
| 4 | Testing Framework | Chunks 1-3 | 3-4 hours |
| 5 | Integration & Debugging | All previous | 2-3 hours |
| 6 | Validation & Polish | All previous | 1-2 hours |

---

## CHUNK 1: Architecture and Initial Setup

### Objective
Establish the foundational architecture and file structure for UserJourney plugin.

### Key Concepts to Understand
1. **UserJourney is NOT a module** - It's a CLI-first orchestrator
2. **It uses ModuleSequencer** - But isn't sequenced itself
3. **State persistence is critical** - Workflows must survive interruptions
4. **DirectoryConfig integration** - Required first module in chain

### Required File Structure
```
modules/user_journey.py                              # Minimal wrapper for CLI integration
asciidoc_dita_toolkit/asciidoc_dita/plugins/UserJourney.py  # Core implementation
tests/test_user_journey.py                          # Test suite
tests/fixtures/UserJourney/                         # Test data
```

### Core Classes to Implement

#### 1. WorkflowState
**Purpose**: Persistent state management across sessions
**Key Methods**:
- `__init__(name, directory, modules)` - Initialize with workflow metadata
- `save_to_disk()` - Atomic persistence with backup
- `load_from_disk(name)` - Load with validation and migration
- `get_next_module()` - Dependency-aware module selection
- `mark_module_completed/failed()` - State transitions

**Critical Requirements**:
- Must use atomic write pattern (temp file → rename)
- Must handle corruption recovery
- Must track detailed execution metrics
- Must integrate with DirectoryConfig

#### 2. WorkflowManager
**Purpose**: Orchestrate module execution via ModuleSequencer
**Key Methods**:
- `start_workflow(name, directory)` - Create new workflow
- `resume_workflow(name)` - Load and continue existing
- `execute_next_module(workflow)` - Run next pending module
- `get_planned_modules()` - Get sequence from ModuleSequencer

**Critical Requirements**:
- Must properly initialize ModuleSequencer
- Must handle DirectoryConfig as special case (interactive)
- Must propagate full context to modules
- Must handle module failures gracefully

#### 3. UserJourneyProcessor
**Purpose**: Handle CLI commands with rich user feedback
**Commands to Implement**:
- `start` - Create new workflow
- `resume` - Continue existing workflow
- `status` - Show workflow progress
- `continue` - Execute next module
- `list` - Show all workflows
- `cleanup` - Remove old workflows

**Critical Requirements**:
- Rich feedback with emojis and clear messages
- Helpful error messages with suggested actions
- Handle edge cases (no files, bad paths, etc.)
- Natural integration with ADT CLI structure

### Implementation Checklist for Chunk 1
- [ ] Create file structure
- [ ] Define all exception classes
- [ ] Implement class skeletons with docstrings
- [ ] Define data structures (ExecutionResult, ModuleState, etc.)
- [ ] Add type hints throughout
- [ ] Ensure no circular imports

### Success Criteria
- All classes defined with clear responsibilities
- File structure matches ADT conventions
- Type hints and docstrings complete
- Can be imported without errors

---

## CHUNK 2: State Management Implementation

### Objective
Implement robust workflow state persistence that survives interruptions and system failures.

### Key Implementation Details

#### Atomic Persistence Pattern
```python
# MUST implement this pattern for save_to_disk():
1. Write to temp file (.tmp)
2. Create backup of existing (.backup)
3. Atomic rename temp → final
4. Delete backup on success
5. Restore from backup on failure
```

#### State Structure
```json
{
  "name": "workflow-name",
  "directory": "/path/to/docs",
  "created": "ISO-8601-timestamp",
  "last_activity": "ISO-8601-timestamp",
  "status": "active|completed|failed|paused",
  "modules": {
    "ModuleName": {
      "status": "pending|running|completed|failed|skipped",
      "started_at": "ISO-8601-timestamp",
      "completed_at": "ISO-8601-timestamp",
      "files_processed": 0,
      "files_modified": 0,
      "execution_time": 0.0,
      "error_message": null,
      "retry_count": 0
    }
  },
  "files_discovered": ["list", "of", "paths"],
  "directory_config": {},
  "metadata": {
    "version": "1.0",
    "adt_version": "x.y.z"
  }
}
```

#### Critical Methods to Implement

1. **File Discovery Integration**
   - Must try DirectoryConfig first (it's required)
   - Fallback to simple `*.adoc` discovery
   - Store results in workflow state

2. **State Transitions**
   - `mark_module_started()` - Set running state, timestamp
   - `mark_module_completed()` - Update metrics, clear errors
   - `mark_module_failed()` - Track error, increment retry count

3. **Progress Calculation**
   - Total/completed/failed module counts
   - Execution time summaries
   - Files processed metrics
   - Can-continue status

### Implementation Checklist for Chunk 2
- [ ] Implement atomic save/load with backup recovery
- [ ] Add state format validation
- [ ] Implement state migration for version upgrades
- [ ] Integrate DirectoryConfig for file discovery
- [ ] Add comprehensive progress tracking
- [ ] Handle all state transitions
- [ ] Test corruption recovery

### Success Criteria
- State persists across process restarts
- Corrupted state files are recovered
- DirectoryConfig integration works
- All metrics tracked accurately
- Migration from old formats works

---

## CHUNK 3: Module Orchestration and CLI Integration

### Objective
Connect UserJourney to ModuleSequencer and implement all CLI commands with excellent UX.

### Key Integration Points

#### ModuleSequencer Integration
1. **Initialization**: Load configs, discover modules
2. **Sequencing**: Get module order respecting dependencies
3. **Execution**: Pass proper context to each module
4. **Special Cases**: Handle DirectoryConfig interactivity

#### CLI Command Patterns

Each command should follow this pattern:
1. **Validate inputs** - Clear error messages
2. **Check preconditions** - Workflow exists? Can continue?
3. **Execute action** - With proper error handling
4. **Provide feedback** - Rich, helpful output
5. **Suggest next steps** - What should user do next?

#### User Experience Requirements
- Use emojis for visual status (✅ ❌ 🔄 📋 📁 etc.)
- Show progress bars/percentages where applicable
- Provide helpful error messages with solutions
- Always suggest the next command to run
- Handle interrupts gracefully (Ctrl+C)

### Critical Implementation Details

1. **DirectoryConfig Special Handling**
   - It's interactive - warn user
   - Refresh file discovery after completion
   - Update workflow state with new config

2. **Error Recovery**
   - Show retry count and max retries
   - Suggest --skip-current for stuck modules
   - Provide --verbose flag for debugging

3. **Status Display**
   - Show module tree with status icons
   - Include timing information
   - Show file counts and progress
   - Highlight next action clearly

### Implementation Checklist for Chunk 3
- [ ] Integrate with ModuleSequencer properly
- [ ] Implement all CLI commands
- [ ] Add rich status displays
- [ ] Handle DirectoryConfig specially
- [ ] Implement retry logic
- [ ] Add interrupt handling
- [ ] Provide helpful error messages

### Success Criteria
- All CLI commands work end-to-end
- ModuleSequencer integration works
- DirectoryConfig updates file discovery
- Rich UI provides clear guidance
- Errors are handled gracefully

---

## CHUNK 4: Test Framework Implementation

### Objective
Create comprehensive test coverage ensuring reliability and maintainability.

### Testing Strategy

#### 1. Unit Tests
- State persistence (save/load/corrupt/recover)
- Module state transitions
- Progress calculations
- Error handling

#### 2. Integration Tests
- ModuleSequencer integration
- DirectoryConfig integration
- CLI command processing
- Workflow execution flows

#### 3. Scenario Tests
- Complete workflow execution
- Interruption and resume
- Module failures and retries
- Concurrent workflows

### Test Fixtures Structure
```
tests/fixtures/UserJourney/
├── workflow_states/          # Various state files
│   ├── fresh_workflow.json   # Just created
│   ├── partial_workflow.json # Some modules complete
│   ├── failed_workflow.json  # Has failures
│   └── corrupted_workflow.json  # Invalid JSON
├── mock_responses/           # ModuleSequencer mocks
│   ├── standard_sequence.json
│   └── error_sequence.json
└── test_directories/         # Test .adoc files
    ├── simple_project/
    └── complex_project/
```

### Key Test Patterns

#### Mock ModuleSequencer
```python
# Create consistent mock for testing
mock_sequencer = Mock()
mock_sequencer.sequence_modules.return_value = (resolutions, errors)
mock_sequencer.execute_module.return_value = mock_result
```

#### Test State Persistence
```python
# Test atomic saves, corruption recovery
# Test state migration from old versions
# Test concurrent access handling
```

#### Test CLI Commands
```python
# Test each command with various inputs
# Test error conditions and edge cases
# Verify output formatting
```

### Implementation Checklist for Chunk 4
- [ ] Create test fixtures directory structure
- [ ] Implement state persistence tests
- [ ] Add ModuleSequencer integration tests
- [ ] Test all CLI commands
- [ ] Add scenario-based tests
- [ ] Test error conditions
- [ ] Add performance tests

### Success Criteria
- >90% code coverage
- All edge cases tested
- Tests run quickly (<30s)
- Clear test naming
- Good test isolation

---

## CHUNK 5: System Integration and Debugging

### Objective
Integrate UserJourney with the ADT system and provide debugging tools.

### Integration Points

#### 1. Update pyproject.toml
```toml
[project.entry-points."adt.modules"]
UserJourney = "modules.user_journey:UserJourneyModule"
```

#### 2. CLI Integration
Add to main ADT CLI parser:
- Main command: `journey`
- Subcommands: `start`, `resume`, `status`, `continue`, `list`, `cleanup`
- Proper help text and argument validation

#### 3. Module Wrapper
Create minimal `UserJourneyModule` that:
- Implements ADTModule interface
- Delegates to UserJourneyProcessor
- Handles CLI argument parsing

### Debug Utilities

Create `debug_user_journey.py` with commands:
- `list` - Show all workflows
- `workflow <name>` - Debug specific workflow
- `sequencing` - Test ModuleSequencer integration
- `directory-config` - Test DirectoryConfig integration

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| State corruption | Implement backup recovery |
| Module not found | Verify .adt-modules.json |
| Permission errors | Check ~/.adt/workflows/ |
| DirectoryConfig missing | Set ADT_ENABLE_DIRECTORY_CONFIG=true |

### Implementation Checklist for Chunk 5
- [ ] Update pyproject.toml
- [ ] Integrate with main CLI
- [ ] Create module wrapper
- [ ] Add debug utilities
- [ ] Document common issues
- [ ] Test full integration
- [ ] Add logging support

### Success Criteria
- `adt journey` commands available
- Debug utilities work
- Integration tests pass
- No import conflicts
- Clear error messages

---

## CHUNK 6: Validation and Polish

### Objective
Ensure MVP meets all requirements and provides excellent user experience.

### MVP Validation Checklist

#### Core Functionality
- [ ] Workflows persist across restarts
- [ ] Module execution follows dependencies
- [ ] DirectoryConfig integration works
- [ ] Interruption recovery works
- [ ] All CLI commands function correctly

#### User Experience
- [ ] Clear, helpful error messages
- [ ] Rich status displays with emojis
- [ ] Always shows next action
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

#### Code Quality
- [ ] Type hints throughout
- [ ] Comprehensive docstrings
- [ ] No TODO/FIXME in code
- [ ] Proper error handling
- [ ] Follows ADT patterns

### Performance Targets
- Workflow creation: <1 second
- Status display: <0.5 seconds
- Module execution overhead: <0.1 seconds
- State save: <0.1 seconds

### Documentation Requirements
- [x] All commands documented in user-guide/
- [x] Error messages helpful
- [x] Code well-commented
- [x] Test coverage >90%
- [x] Debug utilities documented

### Future Enhancement Paths
1. **Phase 2**: Git integration (branches, PRs)
2. **Phase 3**: Interactive module resolution
3. **Phase 4**: Templates and collaboration

### Final Checklist
- [ ] All tests passing
- [ ] Manual testing complete
- [ ] Documentation updated
- [ ] Code review complete
- [ ] Ready for user testing

---

## Appendix: Key Implementation Principles

### 1. State Management is Critical
- Every operation must be atomic
- Always have backup recovery
- Validate on load, migrate if needed

### 2. User Experience First
- Clear, actionable error messages
- Visual progress indicators
- Always suggest next steps
- Handle interruptions gracefully

### 3. Integration Over Implementation
- UserJourney orchestrates, doesn't process
- Leverage existing ADT infrastructure
- Follow established patterns

### 4. Test Everything
- State persistence edge cases
- Module execution failures
- CLI command variations
- Concurrent access scenarios

### 5. Plan for Growth
- State format versioning
- Extension points for phases 2-4
- Clean separation of concerns
- Well-documented interfaces

---

## How to Use This Guide

### For Implementers
1. Read the executive summary and overview
2. Implement chunks sequentially
3. Run tests after each chunk
4. Use debug utilities for troubleshooting

### For AI Assistants
1. Process one chunk at a time
2. Focus on the implementation checklist
3. Verify success criteria before proceeding
4. Ask for clarification if needed

### For Reviewers
1. Check each chunk's success criteria
2. Verify integration points
3. Test user experience flows
4. Validate error handling

This guide provides a complete roadmap for implementing the UserJourney plugin MVP. Follow the chunks sequentially for best results.