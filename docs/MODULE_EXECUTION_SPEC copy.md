# Module Execution Management System - Use Cases

## Use Case 1: Developer Module Configuration

**Actor:** Software Developer  
**Goal:** Configure the execution order of modules and whether they required.
**Non-goals:** The default state is specified elsewhere  
**Preconditions:** Developer has access to project configuration files  

### Primary Flow:
1. Developer opens `.adt-modules.json` configuration file in project root
2. Developer specifies the execution order by listing modules in desired sequence
3. Developer marks each module as either "required" or "optional"
4. Developer sets default enabled state for each module (on/off by default)
5. Developer saves the configuration file
6. System validates the configuration and applies the settings

### Success Criteria:
- Modules execute in the specified order
- Required modules cannot be disabled by end users
- Optional modules respect their default enabled/disabled state
- Configuration changes take effect immediately

### Example Configuration:
```json
{
  "version": "1.0",
  "modules": [
    {
      "name": "EntityReference",
      "required": true,
      "defaultEnabled": true
    },
    {
      "name": "ContentType", 
      "required": false,
      "defaultEnabled": false
    }
  ]
}
```

---

## Use Case 2: End User Module Management

**Actor:** End User  
**Goal:** Enable, disable, and reset optional modules to customize processing behavior  
**Preconditions:** System has modules configured by developers  

### Primary Flow:
1. User views current module status with `adt --list-modules`
2. User enables/disables individual optional modules using CLI commands
3. User can enable/disable all optional modules at once
4. User can reset modules to their default state (as configured by developers)
5. System persists user preferences for future sessions

### Alternative Flows:
- **Bulk Operations:** User enables/disables all preview modules at once
- **Reset to Defaults:** User restores all modules to developer-configured defaults
- **Project Override:** User sets project-specific module preferences

### Success Criteria:
- Optional modules can be toggled on/off by users
- Required modules remain enabled and cannot be disabled
- User preferences persist across sessions
- Users can easily reset to known-good default states
- Bulk operations work correctly for module groups

### Example Commands:
```bash
# View current status
adt --list-modules

# Individual module control
adt --enable-module ContentType
adt --disable-module DirectoryConfig

# Bulk operations
adt --enable-all-optional
adt --disable-all-preview

# Reset functionality
adt --reset-modules
adt --reset-module ContentType
```