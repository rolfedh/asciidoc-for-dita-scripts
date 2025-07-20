## Problem Statement

Technical writers working with the asciidoc-dita-toolkit currently face a fragmented workflow when processing large document sets. They must manually orchestrate multiple plugin executions, track progress across hundreds of files, manage git branches for review cycles, and remember where they left off in complex multi-step processes.

### Current Pain Points
- **Manual orchestration**: Users run `adt EntityReference`, then `adt CrossReference`, etc., individually
- **No progress tracking**: No memory of what's been completed across sessions
- **Git integration gaps**: Manual branch creation, PR management, and merge cycles
- **Context switching overhead**: Users lose track of where they are in multi-module workflows
- **Review cycle complexity**: Difficult to isolate changes from individual modules for review

## User Journey & Workflow Requirements

### Typical End-User Process (Technical Writers)
1. **Start processing** a large document set (hundreds of files)
2. **Run first module** (e.g., EntityReference) - usually deterministic, no interaction needed
3. **Review changes** in a dedicated git branch/PR to ensure quality
4. **Make manual corrections** if needed, commit refinements
5. **Merge PR** when satisfied with module's changes
6. **Move to next module** (e.g., CrossReference) - may depend on EntityReference completion
7. **Repeat process** through the full module dependency chain
8. **Handle interruptions** - resume work days/weeks later from exact stopping point

### Module Interaction Types
- **Deterministic modules**: Run fully automated (EntityReference, ContentType)
- **Interactive/Automated modules**: Can run either way (CrossReference with --validate-refs)
- **Interactive-only modules**: Require user decisions (ContextMigrator for complex cases)

## Proposed Solution: ADT UserJourney Plugin

Create a new ADTModule plugin called "UserJourney" that provides opinionated, git-integrated workflow management for end users.

### Core Features

#### 1. Workflow State Management
```bash
# Start a new workflow
adt journey start --name="docs-migration" --directory=./technical-docs

# Resume existing workflow  
adt journey resume --name="docs-migration"

# Show current status
adt journey status
```

**State Tracking:**
- Which modules have been completed
- Which files have been processed by each module
- Git branch/PR status for each module
- Checkpoint data for resuming interrupted work
- User decisions and manual corrections applied

#### 2. Git Integration
```bash
# Automatic branch management per module
git checkout -b workflow/docs-migration/entity-reference
# ... module runs, creates changes ...
# User reviews, makes corrections
# Orchestrator helps create PR: \"EntityReference processing for docs-migration\"
# After the merge, moves to the next module/branch
```

**Git Workflow:**
- Creates feature branches per module: `workflow/{name}/{module}`
- Generates descriptive commit messages: "Apply EntityReference processing to 47 files"
- Assists with PR creation with module-specific templates
- Tracks PR merge status before proceeding to the next module
- Maintains audit trail of all changes

#### 3. Progress Visualization
```bash
adt journey status --name="docs-migration"

Workflow: docs-migration (./technical-docs)
├── ✅ EntityReference    [47 files] → PR #123 (merged 2 days ago)
├── ✅ CrossReference     [45 files] → PR #124 (merged 1 day ago)  
├── 🔄 ContextAnalyzer    [43 files] → Branch: workflow/docs-migration/context-analyzer
│   └── ⚠️  Manual review needed: 3 files with complex contexts
├── ⏸️  ContextMigrator   [pending: depends on ContextAnalyzer]
└── ⏸️  ExampleBlock      [pending: depends on ContextMigrator]

Next action: Review ContextAnalyzer results and resolve 3 flagged files
Resume with: adt journey continue --name="docs-migration"
```

#### 4. Opinionated Workflow Design
- **One module at a time**: Enforces dependency order, prevents parallel confusion
- **Required review cycles**: Won't proceed until PR is merged (configurable)  
- **Checkpoint persistence**: Workflow state survives interruptions, system restarts
- **Smart resumption**: Returns user to the exact next action needed
- **Failure recovery**: Can restart failed modules without losing completed work

#### 5. Module Integration Points
```python
# UserJourney integrates with ModuleSequencer
class UserJourneyModule(ADTModule):
    def execute_workflow_step(self, workflow_state, current_module):
        # Use ModuleSequencer for dependency resolution
        # Execute module with progress tracking
        # Handle git operations
        # Update workflow state
        # Determine next action
```

### Example User Experience

#### Starting a New Workflow
```bash
$ adt journey start --name="q2-docs-update" --directory=./q2-documentation
✨ Created workflow 'q2-docs-update' for 156 files
📊 Planned modules: EntityReference → CrossReference → ContextAnalyzer → ContextMigrator
🔄 Starting with EntityReference (deterministic)...

[EntityReference runs automatically]

✅ EntityReference completed successfully
   - Processed: 156 files  
   - Changes: 342 entity references converted
   - Branch: workflow/q2-docs-update/entity-reference
   - Commit: "Apply EntityReference processing to Q2 documentation (156 files)"

📋 Next: Review changes and create PR
   Run: gh pr create --title="EntityReference: Q2 documentation update" --body="Auto-generated PR for EntityReference module processing"
   
   When ready to continue: adt journey continue --name="q2-docs-update"
```

#### Resuming After Interruption
```bash
$ adt journey resume --name="q2-docs-update"
📖 Resuming workflow 'q2-docs-update'...

✅ EntityReference → PR #156 (merged 3 days ago)
✅ CrossReference → PR #157 (merged 2 days ago)
🔄 ContextAnalyzer → Currently in progress

⚠️  Manual attention required:
   - 7 files flagged for complex context decisions
   - Branch: workflow/q2-docs-update/context-analyzer  
   - Files needing review: src/api-guide.adoc, src/troubleshooting.adoc, ...

📋 Next actions:
   1. Review flagged files in your editor
   2. Make manual corrections as needed
   3. Run: adt journey continue --name="q2-docs-update" (when ready)
```

### Technical Implementation

#### Data Storage
```json
// ~/.adt/workflows/q2-docs-update.json
{
  "name": "q2-docs-update",
  "directory": "./q2-documentation", 
  "created": "2025-01-15T10:30:00Z",
  "last_activity": "2025-01-17T14:22:00Z",
  "modules": [
    {
      "name": "EntityReference",
      "status": "completed",
      "completed_at": "2025-01-15T11:15:00Z",
      "files_processed": 156,
      "git_branch": "workflow/q2-docs-update/entity-reference",
      "pr_number": 156,
      "pr_status": "merged"
    },
    {
      "name": "ContextAnalyzer", 
      "status": "in_progress",
      "started_at": "2025-01-17T09:00:00Z",
      "files_processed": 149,
      "files_flagged": 7,
      "git_branch": "workflow/q2-docs-update/context-analyzer",
      "user_decisions": {
        "src/api-guide.adoc": {"context_id": "manual_123", "applied_at": "2025-01-17T14:22:00Z"}
      }
    }
  ]
}
```

#### Configuration Options
```json
// User config: ~/.adt/workflow-config.json
{
  "pr_auto_create": true,
  "require_pr_merge": true,
  "git_commit_signing": true,
  "interactive_prompts": true,
  "checkpoint_frequency": "per_module",
  "branch_naming": "workflow/{name}/{module}"
}
```

## Benefits

### For Technical Writers
- **Cognitive load reduction**: One clear workflow, no orchestration decisions
- **Progress visibility**: Always know where you are and what's next
- **Interruption resilience**: Resume complex workflows seamlessly
- **Quality assurance**: Built-in review cycles prevent rushed changes
- **Audit trail**: Complete history of what was changed when and why

### For Teams
- **Consistent process**: Everyone follows same opinionated workflow
- **Review integration**: Natural PR-based review cycles
- **Progress tracking**: Managers can see workflow status across team
- **Knowledge sharing**: Workflow state can be shared/transferred between team members

### For Tool Evolution
- **Usage analytics**: Learn how workflows are actually used in practice
- **Module improvement**: Identify which modules need better automation/interaction
- **Process optimization**: Data-driven workflow refinements

## Implementation Strategy

### Phase 1: Core Workflow Engine
- Basic workflow state management
- Simple module sequencing
- Checkpoint/resume functionality  
- CLI commands: `start`, `continue`, `status`, `resume`

### Phase 2: Git Integration  
- Automatic branch creation/management
- PR creation assistance
- Merge status tracking
- Audit trail generation

### Phase 3: Advanced Features
- Interactive file flagging/resolution
- Workflow templates for common scenarios  
- Team collaboration features
- Performance analytics and optimization

### Phase 4: Enterprise Features
- Workflow sharing and templates
- Integration with external tools (Jira, etc.)
- Advanced reporting and analytics
- Custom module integration

## Success Metrics

- **Adoption rate**: % of users who switch from manual to workflow orchestration
- **Completion rate**: % of workflows that complete successfully vs. abandoned
- **Interruption recovery**: Time to resume after interruption vs. starting over
- **Error reduction**: Fewer mistakes due to missed steps or wrong module order
- **User satisfaction**: Qualitative feedback on workflow experience

## Future Considerations

- **Workflow templates**: Pre-defined workflows for common scenarios
- **Team coordination**: Multiple users working on the same workflow
- **CI/CD integration**: Automated workflow triggers  
- **Plugin marketplace**: Community-contributed workflow extensions
- **Cross-repository workflows**: Handle workflows spanning multiple repos

This ADT UserJourney plugin would transform the asciidoc-dita-toolkit from a collection of individual tools into a cohesive, user-friendly document processing platform that guides technical writers through complex multi-step transformations with confidence and clarity.