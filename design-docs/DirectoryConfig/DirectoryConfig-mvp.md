# ADT Directory Configuration MVP

## MVP Scope
Deliver essential directory-scoped processing capabilities that provide immediate value while keeping implementation simple for rapid development and team feedback.

## Core Features (Must-Have Only)

**From the Requirements section:**
- **Repository Root Selection**: Specify the root directory of documentation repository
- **Configuration Persistence**: Remember user choices between sessions
- **Scope Compliance**: Honor configuration choices during all operations
- **Directory Inclusion/Exclusion**: Specify which directories to process or skip

## Simplified Configuration Schema

Store configuration in `.adtconfig.json` in the project root or user's home directory:

```json
{
  "version": "1.0",
  "repoRoot": "/path/to/docs",
  "includeDirs": ["docs/user-guide"],
  "excludeDirs": ["docs/legacy"],
  "lastUpdated": "2024-07-04T12:00:00Z"
}
```

## Minimal CLI Interface
```bash
# Essential commands only
adt directory-config         # Interactive setup wizard
adt directory-config --show  # Display current configuration
adt ContentType              # All plugins use the configured directory scope
adt ContentType ./something  # Plugins can override the directory scope
```

## MVP Implementation Strategy
1. **Configuration Discovery**: Check for `.adtconfig.json` in current directory and home directory. If multiple instances of the file are present, display information about each instance and prompt the user to select one. Preselect the instance with the most recent "last used date".
2. **Lazy Initialization**: Prompt for configuration only when needed
3. **Validation Pipeline**: Verify repository root and directories exist
4. **User confirmation**: Display current configuration to user and prompt for acceptance or modification
5. **Filtered Processing**: Apply include/exclude directory patterns during content discovery phase
6. **Directory Scoping**: Process only files within configured directories

## MVP User Experience
```
$ adt directory-config
Repository root: /home/user/docs-project
Include directories: docs/user-guide
Exclude directories: docs/legacy,archive
Configuration saved!

$ adt ContentType .
✓ Using directory configuration from ~/.adtconfig.json
✓ Processing 1 directory, excluding 2
✓ Found 23 .adoc files to process
```

## Excluded from MVP
- Glob pattern support (`*`, `**`, `?`)
- Direct CLI parameter setting (--repo-root, --include-dirs, etc.)
- Configuration reset functionality
- Advanced patterns (include/exclude file patterns)
- Performance caching
- Dry run mode
- Git branch integration (separate plugin)
- GitHub integration features
- Web interface and advanced features

## MVP Value Delivery
This MVP delivers focused **Directory Processing Benefits**:
- **Save Processing Time**: Process only configured directories
- **Eliminate Repetitive Tasks**: Configure once, use repeatedly
- **Ensure Documentation Consistency**: Team uses same directory scope settings
- **Avoid Unwanted Changes**: Skip legacy or draft directories automatically

## Implementation Priority
The MVP focuses on the fundamental workflow: **configure directory scope → persist settings → honor scope during operations**, providing immediate productivity benefits while establishing the foundation for future enhancements.

## Next Steps
1. Implement basic directory configuration wizard (`adt directory-config`)
2. Add JSON configuration file handling
3. Integrate directory scope filtering into existing plugins
4. Add configuration display (`adt directory-config --show`)
5. Test with team and gather feedback for iteration

---

*This MVP is focused on directory configuration only. Git branch configuration will be handled by a separate `git-branch-config` plugin.*
