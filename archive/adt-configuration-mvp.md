# ADT Configuration MVP: Core Directory and Branch Selection

## MVP Scope
Deliver the essential configuration capabilities that provide immediate value while keeping implementation simple for rapid development and team feedback.

## Core Features (Must-Have Only)

**From the Requirements section:**
- **Repository Root Selection**: Specify the root directory of documentation repository
- **Branch Targeting**: Select one or more git branches for operations
- **Configuration Persistence**: Remember user choices between sessions
- **Scope Compliance**: Honor configuration choices during all operations
- **Directory Inclusion/Exclusion**: Specify which directories to process or skip

## Simplified Configuration Schema
```json
{
  "version": "1.0",
  "repoRoot": "/path/to/docs",
  "branches": ["main"],
  "includeDirs": ["docs/user-guide"],
  "excludeDirs": ["docs/legacy"]
}
```

## Minimal CLI Interface
```bash
# Essential commands only
adt config                    # Interactive setup wizard
adt config --show            # Display current configuration
adt ContentType               # Uses configured scope
```

## MVP Implementation Strategy
1. **Configuration Discovery**: Check for `.adtconfig.json` in current directory only
2. **Basic Validation**: Verify repository root exists and branches are valid
3. **Simple Filtering**: Apply include/exclude during file discovery
4. **Branch Checking**: Skip operations when current branch doesn't match

## MVP User Experience
```
$ adt config
Repository root: /home/user/docs-project
Target branches (comma-separated): main
Include directories: docs/user-guide
Exclude directories: docs/legacy
Configuration saved!

$ adt ContentType
✓ Using configuration from .adtconfig.json
✓ Current branch 'main' matches target branches
✓ Processing 1 directory, excluding 1
✓ Found 23 .adoc files to process
```

## Excluded from MVP
- Multiple configuration profiles
- Glob pattern support (`*`, `**`, `?`)
- Direct CLI parameter setting (--repo-root, --branches, etc.)
- Configuration reset functionality
- Advanced patterns (include/exclude file patterns)
- Home directory fallback for config
- Performance caching
- Dry run mode
- All GitHub integration features
- Web interface and advanced features

## MVP Value Delivery
This MVP delivers the **Core Value Proposition** from the main design document:
- **Save Processing Time**: Process only configured directories
- **Prevent Accidental Changes**: Lock operations to specific branches
- **Eliminate Repetitive Tasks**: Configure once, use repeatedly
- **Ensure Documentation Consistency**: Team uses same scope settings

## Implementation Priority
The MVP focuses on the fundamental workflow: **configure scope → persist settings → honor scope during operations**, providing immediate productivity benefits while establishing the foundation for future enhancements.

## Next Steps
1. Implement basic configuration wizard (`adt config`)
2. Add JSON configuration file handling
3. Integrate scope filtering into existing plugins
4. Add configuration display (`adt config --show`)
5. Test with team and gather feedback for iteration

---

*This MVP is derived from the full [ADT Configuration Design: Directory and Branch Selection](design-idea-user-selects-or-excludes-directories.md) document.*
