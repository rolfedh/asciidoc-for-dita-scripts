# Module Execution Management System - MVP Specification

## Overview

This specification defines an MVP (Minimum Viable Product) for a module execution management system that allows developers to control the order, requirement, and enablement of modules in the AsciiDoc DITA Toolkit.

## Background

The current system has a basic plugin discovery mechanism that loads all plugins and executes them individually via CLI commands. This specification extends the system to support:
- Execution ordering
- Required vs optional modules
- User-configurable module enablement
- Batch execution workflows

## Architecture Decision

**Implementation Approach: Single Module with Configuration Files**

The functionality will be implemented as a single module (`ModuleManager`) with external configuration files, rather than multiple separate modules. This approach provides:
- Centralized control and coordination
- Simpler dependency management
- Easier configuration validation
- Single point of truth for module state

## Use Cases

### UC1: Developer Module Configuration
**As a software developer, I must be able to specify the order of execution of each module, mark modules as required or optional, by editing a configuration file.**

### UC2: End User Module Control
**As an end user, I must be able to enable/disable optional modules, enable/disable all optional modules at once, and reset modules to their default state.**

## Core Components

### 1. Module Execution Manager (`ModuleManager`)

**Location:** `asciidoc_dita_toolkit/asciidoc_dita/module_manager.py`

**Responsibilities:**
- Load and validate module configuration
- Manage module execution order
- Handle module enablement state
- Provide batch execution capabilities
- Integrate with existing plugin system

### 2. Configuration Files

#### 2.1 Module Definition Configuration
**File:** `.adt-modules.json` (repository level)
**Purpose:** Developer-controlled module ordering and requirements

```json
{
  "version": "1.0",
  "modules": [
    {
      "name": "EntityReference",
      "order": 10,
      "required": true,
      "defaultEnabled": true,
      "category": "core",
      "description": "Replace unsupported HTML character entities"
    },
    {
      "name": "ContentType",
      "order": 20,
      "required": false,
      "defaultEnabled": false,
      "category": "preview",
      "description": "Add content type labels to AsciiDoc files"
    },
    {
      "name": "DirectoryConfig",
      "order": 5,
      "required": false,
      "defaultEnabled": false,
      "category": "preview",
      "description": "Configure directory scoping for processing"
    }
  ],
  "workflows": [
    {
      "name": "full-processing",
      "description": "Complete document processing workflow",
      "modules": ["DirectoryConfig", "EntityReference", "ContentType"]
    },
    {
      "name": "basic-processing",
      "description": "Essential processing only",
      "modules": ["EntityReference"]
    }
  ]
}
```

#### 2.2 User Module State Configuration
**File:** `~/.adt-module-state.json` (user level)
**Purpose:** User-controlled module enablement overrides

```json
{
  "version": "1.0",
  "userOverrides": {
    "ContentType": {
      "enabled": true,
      "lastModified": "2025-01-15T10:30:00Z"
    },
    "DirectoryConfig": {
      "enabled": false,
      "lastModified": "2025-01-15T10:30:00Z"
    }
  },
  "globalSettings": {
    "enableAllOptional": false,
    "enableAllPreview": true
  }
}
```

#### 2.3 Module State Configuration Management

The module state configuration follows the same hierarchy and conflict resolution pattern as the existing `.adtconfig.json` system:

1. **Local Configuration:** `./.adt-module-state.json` (project-specific module preferences)
2. **Global Configuration:** `~/.adt-module-state.json` (user's default module preferences)

When both local and global module state files exist, the system compares their `lastModified` timestamps and prompts the user to choose which configuration to use. This choice is saved as a user preference in `~/.adt-user-preferences.json` to avoid repeated prompts. The system supports non-interactive mode via the `ADT_MODULE_STATE_CHOICE` environment variable (values: "local", "global", or "1"/"2").

The module state configuration is loaded independently from the module definition configuration, allowing users to have different enablement preferences per project while maintaining a consistent global default. User state overrides take precedence over the `defaultEnabled` values specified in `.adt-modules.json`.

### 3. CLI Interface Extensions

#### 3.1 New Commands

```bash
# List all modules in execution order. Three columns: "name", "default status", "current status". Required modules show "module_name, required, enabled". Optional modules show (enabled/disabled) and (enabled/disabled).
adt --list-modules

# Enable/disable modules
adt --enable-module ContentType
adt --disable-module ContentType
adt --enable-all-modules
adt --disable-all-modules

# Reset to defaults
adt --reset-modules

```

#### 3.2 Enhanced Plugin Registration

Plugins will be extended to provide metadata for the module system:

```python
# In each plugin (e.g., ContentType.py)
def get_module_metadata():
    """Return module metadata for the module manager."""
    return {
        "name": "ContentType",
        "version": "1.0.0",
        "dependencies": [],
        "conflicts": [],
    }
```

### 4. Module Execution Engine

**Core Algorithm:**
1. Load module definitions from `.adt-modules.json`
2. Load user overrides from `~/.adt-module-state.json`
3. Resolve final module state (enabled/disabled)
4. Sort modules by execution order
5. Validate dependencies and conflicts
6. Execute enabled modules in order

### 5. Backward Compatibility

The existing CLI interface remains unchanged:
- `adt EntityReference --directory ./docs` continues to work
- `adt ContentType --file example.adoc` continues to work
- Environment variables (`ADT_ENABLE_CONTENT_TYPE`) continue to work

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1-2)
1. Create `ModuleManager` class
2. Implement configuration file loading and validation
3. Create basic CLI commands for module status
4. Extend existing `is_plugin_enabled()` function

### Phase 2: Execution Engine (Week 3)
1. Implement module ordering and execution logic
2. Add dependency resolution
3. Create workflow execution capability
4. Add user state management

### Phase 3: CLI Integration (Week 4)
1. Add new CLI commands
2. Integrate with existing plugin system
3. Add comprehensive error handling and validation
4. Create migration utilities

### Phase 4: Testing and Documentation (Week 5)
1. Create comprehensive test suite
2. Add documentation and examples
3. Create migration guide for existing users
4. Performance testing and optimization

## Configuration Schema

### Module Definition Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "version": {"type": "string"},
    "modules": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "order": {"type": "integer", "minimum": 1},
          "required": {"type": "boolean"},
          "defaultEnabled": {"type": "boolean"},
          "category": {"type": "string", "enum": ["core", "standard", "preview", "experimental"]},
          "description": {"type": "string"},
          "dependencies": {"type": "array", "items": {"type": "string"}},
          "conflicts": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["name", "order", "required", "defaultEnabled", "category"]
      }
    },
    "workflows": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "description": {"type": "string"},
          "modules": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["name", "modules"]
      }
    }
  },
  "required": ["version", "modules"]
}
```

## Security Considerations

1. **Configuration Validation:** All configuration files must be validated against schemas
2. **Path Security:** Module paths must be sanitized to prevent directory traversal
3. **Permission Checks:** User state modifications require appropriate file permissions
4. **Conflict Resolution:** Handle conflicting configurations gracefully

## Error Handling

1. **Missing Configuration:** Gracefully degrade to existing behavior
2. **Invalid JSON:** Provide clear error messages with line numbers
3. **Module Not Found:** Skip missing modules with warnings
4. **Circular Dependencies:** Detect and report dependency cycles
5. **Permission Errors:** Handle read-only configurations

## Performance Considerations

1. **Lazy Loading:** Load module configurations only when needed
2. **Caching:** Cache parsed configurations for repeated executions
3. **Parallel Execution:** Consider parallel execution for independent modules (future enhancement)

## Testing Strategy

1. **Unit Tests:** Test each component in isolation
2. **Integration Tests:** Test complete workflows
3. **Configuration Tests:** Validate all configuration scenarios
4. **Backward Compatibility Tests:** Ensure existing functionality works
5. **Error Condition Tests:** Test all error scenarios

## Migration Path

1. **Phase 1:** New system runs alongside existing system
2. **Phase 2:** Existing environment variables mapped to new configuration
3. **Phase 3:** Migration tool to convert existing setups
4. **Phase 4:** Deprecation warnings for old patterns (future release)

## Success Criteria

1. ✅ Developers can specify module execution order via configuration file
2. ✅ Developers can mark modules as required or optional
3. ✅ Users can enable/disable optional modules
4. ✅ Users can enable/disable all optional modules at once
5. ✅ Users can reset modules to default state
6. ✅ Existing CLI functionality remains unchanged
7. ✅ Configuration is validated and provides clear error messages
8. ✅ Performance impact is minimal (<10% overhead)

## Future Enhancements (Post-MVP)

1. **Parallel Execution:** Execute independent modules concurrently
2. **Conditional Execution:** Execute modules based on file type or content
3. **Module Marketplace:** Download and install community modules
4. **GUI Configuration:** Visual interface for module management
5. **Advanced Workflows:** Complex workflow definitions with branching logic
6. **Module Metrics:** Track execution time and success rates
7. **Integration APIs:** REST API for external tool integration

## References

- [Current Plugin System](./PLUGIN_DEVELOPMENT_PATTERN.md)
- [Configuration Management](./CLI_SIMPLIFICATION_DESIGN.md)
- [File Utilities Documentation](../asciidoc_dita_toolkit/asciidoc_dita/file_utils.py)
