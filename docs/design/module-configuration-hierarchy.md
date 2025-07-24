# Module Configuration Hierarchy Design

## Executive Summary

The current ADT module system has **inconsistent configuration patterns** across different stakeholders. This document proposes a unified configuration hierarchy that balances developer control, plugin flexibility, and user choice while maintaining system stability through proper dependency management.

**Implementation Goal**: Create a standardized, AI-implementable module configuration system in 4 discrete chunks that can be developed independently by GitHub Copilot and Claude Sonnet.

## Document Structure for AI Implementation

This document is organized into **4 implementation chunks** that can be executed independently:

- **[CHUNK 1]**: Core Infrastructure & Base Classes
- **[CHUNK 2]**: Configuration Resolution Engine
- **[CHUNK 3]**: Module Migration & Standardization
- **[CHUNK 4]**: CLI Tools & User Experience

Each chunk includes specific implementation requirements, test criteria, and integration points.

## Current State Analysis

### Configuration Inconsistencies

**DirectoryConfig Module:**
- Full layered config: `env var → module config → runtime`
- Environment variable: `ADT_ENABLE_DIRECTORY_CONFIG`
- Preview feature flag system

**Other Modules:**
- Basic module config only
- No environment variable support
- Inconsistent default behaviors

**UserJourney Module:**
- Custom workflow state configuration
- Different patterns from other modules

### Stakeholder Roles

| Stakeholder | Current Capabilities | Current Issues |
|-------------|---------------------|----------------|
| **ADT Developer** | Define module dependencies in code | No way to mark modules as "required" |
| **Plugin Developer** | Set module metadata, version | Limited control over enablement rules |
| **End User** | Basic config overrides | Inconsistent env var support, no dependency awareness |

## Problem Statement

1. **Inconsistent Configuration**: Modules use different patterns for enablement
2. **No Required Module Concept**: Users can disable critical system modules
3. **Poor Dependency Handling**: No automatic resolution or clear error messages
4. **Limited User Control**: Inconsistent environment variable support
5. **Developer Constraints**: No way to enforce business rules about module combinations

## Proposed Solution: Three-Tier Configuration Hierarchy

### Tier 1: Developer Constraints (Highest Priority)

**Purpose**: ADT developers define non-negotiable system requirements

```python
@property
def required(self) -> bool:
    """Whether this module is required for system operation."""
    return True  # Cannot be disabled by users

@property
def user_configurable(self) -> bool:
    """Whether end users can disable this module."""
    return False  # For required modules

@property
def dependencies(self) -> List[str]:
    """Required dependencies that must be enabled."""
    return ["EntityReference", "DirectoryConfig"]
```

**Examples:**
- `DirectoryConfig`: Required=True (foundational)
- `EntityReference`: Required=True (core functionality)
- `ExampleBlock`: Required=False (enhancement)

### Tier 2: Plugin Developer Defaults (Medium Priority)

**Purpose**: Plugin developers set sensible defaults and constraints

```python
@property
def default_enabled(self) -> bool:
    """Default enablement state."""
    return True

@property
def preview_feature(self) -> bool:
    """Whether this is a preview feature."""
    return False

def validate_configuration(self, config: Dict[str, Any]) -> List[str]:
    """Validate plugin-specific configuration rules."""
    errors = []
    # Plugin-specific validation logic
    return errors
```

### Tier 3: End User Preferences (Lowest Priority)

**Purpose**: Users customize their experience within constraints

**Environment Variables:**
```bash
# Global control
export ADT_ENABLE_ALL_MODULES=false
export ADT_DISABLE_PREVIEW_FEATURES=true

# Per-module control
export ADT_ENABLE_EXAMPLE_BLOCK=false
export ADT_ENABLE_CONTENT_TYPE=true
```

**Configuration Files:**
```json
{
  "modules": {
    "ExampleBlock": {"enabled": false},
    "ContentType": {"enabled": true, "strict_mode": true}
  },
  "global": {
    "enable_preview_features": false
  }
}
```

## Configuration Resolution Algorithm

### Resolution Order

1. **Check Developer Constraints**
   - If `required=True`, module is enabled regardless of user preferences
   - Log warning if user tried to disable required module

2. **Apply Plugin Defaults**
   - Use `default_enabled` if no user preference specified
   - Respect `preview_feature` flag with global preview settings

3. **Apply User Preferences**
   - Environment variables override config files
   - Config files override plugin defaults
   - Validate against plugin constraints

4. **Resolve Dependencies**
   - Auto-enable required dependencies with warnings
   - Cascade disable dependent modules with warnings
   - Fail only on unresolvable conflicts

### Dependency Resolution Logic

```python
def resolve_module_configuration(modules: Dict[str, Module]) -> Dict[str, bool]:
    enabled_modules = {}

    # Phase 1: Apply developer constraints
    for name, module in modules.items():
        if module.required:
            enabled_modules[name] = True
            if user_tried_to_disable(name):
                log.warning(f"Cannot disable required module: {name}")

    # Phase 2: Apply user preferences for optional modules
    for name, module in modules.items():
        if not module.required:
            enabled_modules[name] = resolve_user_preference(name, module)

    # Phase 3: Resolve dependencies
    changed = True
    while changed:
        changed = False
        for name, enabled in enabled_modules.items():
            if enabled:
                for dep in modules[name].dependencies:
                    if not enabled_modules.get(dep, False):
                        if modules[dep].user_configurable:
                            log.warning(f"Auto-enabling {dep} (required by {name})")
                            enabled_modules[dep] = True
                            changed = True
                        else:
                            raise ConfigError(f"Cannot enable {dep} (required by {name})")

    return enabled_modules
```

## Module Categories

### Required Modules (Developer-Controlled)
- **DirectoryConfig**: File discovery foundation
- **EntityReference**: Core content processing
- Cannot be disabled by users
- Auto-enabled regardless of configuration

### Core Optional Modules (Default Enabled)
- **ContentType**: Content classification
- **CrossReference**: Link validation
- Enabled by default, user-configurable
- May have dependencies on required modules

### Enhancement Modules (Default Enabled)
- **ExampleBlock**: Content structure enhancement
- **ContextAnalyzer**: Advanced analysis
- Enabled by default, fully user-configurable

### Preview Modules (Default Disabled)
- **Experimental features**
- Disabled by default unless preview mode enabled
- May become core modules in future releases

### Orchestration Modules (Special Case)
- **UserJourney**: Workflow orchestration
- Different configuration patterns due to state management
- May need special handling in configuration system

## Implementation Strategy

### Phase 1: Foundation (Week 1-2)
1. **Define base interfaces** for module configuration
2. **Implement resolution algorithm** in ModuleSequencer
3. **Add required/optional distinction** to existing modules
4. **Create configuration validation framework**

### Phase 2: Standardization (Week 3-4)
1. **Migrate all modules** to new configuration pattern
2. **Add environment variable support** consistently
3. **Implement dependency auto-resolution**
4. **Add comprehensive logging/warnings**

### Phase 3: Enhancement (Week 5-6)
1. **Add configuration validation CLI tools**
2. **Implement cascade disable warnings**
3. **Add configuration export/import**
4. **Performance optimization**

## Environment Variable Specification

### Global Controls
```bash
ADT_ENABLE_ALL_MODULES=true|false      # Override all module defaults
ADT_DISABLE_PREVIEW_FEATURES=true|false # Disable all preview features
ADT_CONFIG_VALIDATION=strict|warn|off   # Configuration validation level
```

### Per-Module Controls
```bash
ADT_ENABLE_<MODULE_NAME>=true|false     # Per-module enablement
ADT_<MODULE_NAME>_<SETTING>=value       # Per-module configuration
```

Examples:
```bash
ADT_ENABLE_EXAMPLE_BLOCK=false
ADT_CONTENT_TYPE_STRICT_MODE=true
ADT_CROSS_REFERENCE_VALIDATE_REFS=false
```

## Benefits

### For ADT Developers
- **System stability**: Required modules cannot be disabled
- **Clear contracts**: Explicit dependency declarations
- **Flexible deployment**: Different configurations for different use cases

### For Plugin Developers
- **Predictable behavior**: Consistent configuration patterns
- **User feedback**: Clear warnings about configuration conflicts
- **Easy integration**: Standard interfaces for all configuration

### For End Users
- **Simple control**: Environment variables for quick overrides
- **Clear feedback**: Warnings explain auto-enabled dependencies
- **Flexible configuration**: Multiple ways to customize behavior

## Migration Strategy

### Backward Compatibility
- **Existing configurations continue working** during transition
- **Gradual migration** of modules to new pattern
- **Clear deprecation warnings** for old patterns

### Configuration Migration
```python
# Old pattern (deprecated)
self.enable_preview = config.get("enable_preview",
    os.getenv("ADT_ENABLE_DIRECTORY_CONFIG", "true").lower() == "true")

# New pattern
self.enabled = self.resolve_enablement(config)
```

## Future Considerations

### Advanced Features
- **Profile-based configuration**: Development vs. production profiles
- **Remote configuration**: Centralized configuration management
- **A/B testing**: Gradual feature rollouts
- **Performance monitoring**: Track module execution times

### Integration Points
- **CI/CD pipelines**: Automated configuration validation
- **IDE integration**: Configuration editor with dependency visualization
- **Monitoring systems**: Track module usage patterns

## Conclusion

This three-tier configuration hierarchy provides:
1. **Developer control** over system stability
2. **Plugin flexibility** for feature management
3. **User choice** within safe boundaries
4. **Automatic dependency resolution** with clear feedback

The proposed system balances the needs of all stakeholders while maintaining backward compatibility and providing a clear migration path forward.
