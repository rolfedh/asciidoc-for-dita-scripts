# ADT Configuration Design: Directory and Branch Selection

## Executive Summary

The AsciiDoc-DITA Toolkit (ADT) needs enhanced configuration capabilities to allow users to selectively process documentation based on directories and git branches. This design outlines how users will specify inclusion/exclusion patterns and selected branches for processing, with configuration persistence between sessions.

## Use Case & User Journey

As a documentation maintainer, I need to configure ADT to operate selectively on my repository:

1. **Initial Setup**: Launch ADT and configure repository root and target branches
2. **Directory Selection**: Optionally specify directories to include/exclude from processing
3. **Persistent Configuration**: ADT remembers choices between sessions
4. **Selective Operations**: All plugin executions honor the configured scope
5. **Configuration Updates**: Modify settings as needed through the same interface

## Core Value Proposition

- **Save Processing Time**: Process only relevant directories (e.g., `/docs/user-guide`) instead of scanning the entire repository, reducing conversion time by up to 80%
- **Prevent Accidental Changes**: Lock operations to specific branches like `main` or `develop` to avoid unintended modifications to release documentation
- **Eliminate Repetitive Tasks**: Configure once and automatically apply the same processing rules across hundreds of files without manual selection each time
- **Ensure Documentation Consistency**: All team members use identical directory scopes and branch targets, eliminating inconsistent conversion results between team members

## Requirements

### Must-Have Features
- **Repository Root Selection**: Specify the root directory of documentation repository
- **Branch Targeting**: Select one or more git branches for operations
- **Configuration Persistence**: Remember user choices between sessions
- **Scope Compliance**: Honor configuration choices during all operations
- **Directory Inclusion/Exclusion**: Specify which directories to process or skip

### Should-Have Features
- **Pattern Support**: Use glob patterns for flexible directory matching
- **Configuration Validation**: Validate paths and branches exist
- **Clear Feedback**: Provide informative error messages for invalid configurations

### Could-Have Features
- **Multiple Profiles**: Save and switch between configuration sets for different projects
- **Progress Tracking**: Resume interrupted operations across directories/branches
- **Plugin Ordering**: Customize execution sequence of plugins

## Technical Design

### Configuration Storage

Store configuration in `.adtconfig.json` in the project root or user's home directory:

```json
{
  "version": "1.0",
  "repoRoot": "/path/to/docs",
  "branches": ["main", "develop"],
  "includeDirs": ["docs/user-guide", "docs/api"],
  "excludeDirs": ["docs/legacy", "docs/drafts"],
  "patterns": {
    "include": ["*.adoc", "*.md"],
    "exclude": ["**/temp/**", "**/backup/**"]
  },
  "lastUpdated": "2024-07-04T12:00:00Z"
}
```

### Command-Line Interface

```bash
# Configuration management
adt config                    # Interactive setup wizard
adt config --show            # Display current configuration
adt config --reset           # Reset to defaults

# Direct parameter setting
adt config --repo-root /path/to/docs
adt config --branches main,develop
adt config --include-dirs docs/guide,docs/api
adt config --exclude-dirs docs/legacy

# Run with configuration
adt ContentType               # Uses configured scope
adt --ignore-config ContentType  # Bypass configuration
```

### Implementation Strategy

1. **Configuration Discovery**: Check for `.adtconfig.json` in current directory, then home directory
2. **Lazy Initialization**: Prompt for configuration only when needed
3. **Validation Pipeline**: Verify repository root, branches exist, and paths are valid
4. **Filtered Processing**: Apply include/exclude patterns during file discovery
5. **Branch Awareness**: Skip operations when current branch is not in configured list

## User Experience

### Initial Setup Flow
```
$ adt config
┌─ ADT Configuration Setup ─────────────────────────────────┐
│ Repository root: /home/user/docs-project                  │
│ Target branches: main, develop                            │
│ Include directories: docs/user-guide, docs/api           │
│ Exclude directories: docs/legacy                         │
│                                                           │
│ Configuration saved to .adtconfig.json                   │
└───────────────────────────────────────────────────────────┘
```

### Subsequent Operations
```
$ adt ContentType
✓ Using configuration from .adtconfig.json
✓ Current branch 'main' matches configured branches
✓ Processing 2 directories, excluding 1
✓ Found 47 .adoc files to process

Checking proc_install.adoc...
  ✓ Content type already set: PROCEDURE
...
```

### Configuration Review
```
$ adt config --show
Current ADT Configuration:
  Repository: /home/user/docs-project
  Branches: main, develop
  Include: docs/user-guide, docs/api
  Exclude: docs/legacy
  Last updated: 2024-07-04 12:00:00
```

## Implementation Considerations

### Technical Constraints
- **Path Resolution**: Store paths relative to repository root for portability
- **Branch Validation**: Verify branches exist before saving configuration
- **Pattern Matching**: Support standard glob patterns (`*`, `**`, `?`)
- **Performance**: Cache file discovery results for large repositories
- **Error Handling**: Graceful degradation when configuration is invalid

### Security & Safety
- **Path Traversal**: Prevent directory traversal attacks in configuration
- **Branch Protection**: Warn users when targeting protected branches
- **Backup Strategy**: Create backup before bulk operations
- **Dry Run Mode**: Allow preview of operations before execution

## Future Enhancements

### GitHub Integration
- **Repository Discovery**: Browse and select GitHub repositories via API
- **Branch Management**: Auto-detect and select from remote branches
- **PR-Based Processing**: Process only files changed in specific pull requests
- **Webhook Integration**: Trigger ADT automatically on documentation changes
- **Team Collaboration**: Share configurations across organization members

### Advanced Features
- **Web Interface**: Browser-based configuration and monitoring
- **CI/CD Integration**: Generate pipeline configurations from ADT settings
- **Plugin Marketplace**: Discover and configure third-party plugins
- **Analytics Dashboard**: Track documentation quality metrics over time
