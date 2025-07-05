# ADT Directory Configuration Toggle-ability Design

## Overview
This document outlines the architectural design for making the directory-config feature completely optional and toggle-able as part of ADT's two-stage plugin rollout strategy: preview → generally available.

## Design Goals
- **Zero Breaking Changes**: Existing workflows continue unchanged when disabled
- **Graceful Degradation**: Core functionality works with or without configuration
- **Clean Feature Boundaries**: Configuration logic contained within plugin boundaries
- **Staged Rollout Support**: Perfect for progressive feature enablement

## Implementation Difficulty: **LOW** ⭐

The directory-config feature is naturally toggle-able due to the plugin-based architecture approach.

## Toggle-ability Strategy

### 1. Plugin-Based Architecture
Implement `DirectoryConfig` as a standard plugin with stage metadata:

```python
# In plugin registry
AVAILABLE_PLUGINS = {
    "ContentType": {"stage": "generally-available", "enabled": True},
    "EntityReference": {"stage": "generally-available", "enabled": True}, 
    "DirectoryConfig": {"stage": "preview", "enabled": False}
}
```

### 2. Graceful Degradation Pattern
Modify `process_adoc_files` in file_utils.py to work with or without configuration:

```python
def process_adoc_files(directory_path):
    """Process AsciiDoc files with optional directory configuration."""
    # Try to load config, fall back to legacy behavior
    config = load_directory_config() if is_plugin_enabled("DirectoryConfig") else None
    
    if config:
        # New: Apply directory filtering
        files = get_filtered_adoc_files(directory_path, config)
    else:
        # Legacy: Process all files in directory
        files = get_all_adoc_files(directory_path)
    
    return files

def get_directory_scope(base_path):
    """Returns directories to process based on configuration."""
    if not is_plugin_enabled("DirectoryConfig"):
        return [base_path]  # Legacy behavior: just the specified directory
    
    config = load_directory_config()
    if not config:
        return [base_path]  # No config found, use legacy behavior
    
    return apply_directory_filters(base_path, config)
```

### 3. Plugin Configurator Integration
The directory-config integrates seamlessly with the planned plugin configurator:

```bash
$ adt configure-plugins
> [1] ContentType (generally-available) ✓ enabled
> [2] EntityReference (generally-available) ✓ enabled  
> [3] DirectoryConfig (preview) ✗ disabled
> [4] Toggle plugin states
```

## Implementation Benefits

### ✅ Zero Breaking Changes
- Existing `adt ContentType ./path` workflows continue unchanged
- All current plugins work exactly as before
- No migration required for existing users
- No learning curve for users who don't enable the feature

### ✅ Clean Feature Boundaries
- Configuration logic contained within the DirectoryConfig plugin
- Core toolkit (`file_utils.py`, `toolkit.py`) remains unaware of configuration details
- Easy to remove or modify without affecting other features
- Clear separation of concerns

### ✅ Staged Rollout Support
- Perfect for preview → generally available progression
- Can be enabled per-user, per-team, or per-environment
- Feedback collection without affecting stable workflows
- A/B testing capabilities during preview stage

### ✅ Backward Compatibility
- When disabled: 100% identical to current behavior
- When enabled: Additive functionality only
- No configuration files required for basic operation
- Existing scripts and automation continue working

## Rollout Strategy

### Stage 1: Preview
```python
"DirectoryConfig": {"stage": "preview", "enabled": False}
```
- Disabled by default
- Users can manually enable for testing
- Feedback collection on UX and functionality

### Stage 2: Generally Available
```python
"DirectoryConfig": {"stage": "generally-available", "enabled": True}
```
- Enabled by default for new installations
- Full documentation and support
- Existing users can opt-in via plugin configurator

## CLI Behavior by Stage

### When Disabled (Stage 1)
```bash
$ adt ContentType ./docs
# Works exactly as today - processes all .adoc files in ./docs

$ adt DirectoryConfig
# Plugin not available or shows "Enable in plugin configurator"
```

### When Enabled (Stage 2)
```bash
$ adt ContentType ./docs
# Uses directory configuration if available, falls back to legacy behavior

$ adt DirectoryConfig
# Interactive setup wizard available
```

## Configuration Discovery Logic
```python
def load_directory_config():
    """Load configuration with proper fallback chain."""
    if not is_plugin_enabled("DirectoryConfig"):
        return None
    
    # Check current directory first
    local_config = load_config_file("./.adtconfig.json")
    home_config = load_config_file("~/.adtconfig.json")
    
    if local_config and home_config:
        return prompt_user_to_choose_config(local_config, home_config)
    
    return local_config or home_config or None
```

## Testing Strategy
- **Unit Tests**: Verify behavior with plugin enabled/disabled
- **Integration Tests**: Ensure existing workflows remain unchanged
- **User Acceptance**: Test with disabled state first, then enable
- **Performance**: Verify no impact when disabled

## Migration Path
1. **Phase 1**: Implement with plugin disabled by default
2. **Phase 2**: Enable for user testing and feedback
3. **Phase 3**: Full enablement with opt-out capability

## Conclusion
The plugin-based architecture makes directory-config inherently toggle-able with minimal complexity. This design supports the two-stage rollout strategy while maintaining 100% backward compatibility and providing a smooth migration path for users.

The key insight is that **optional features implemented as plugins are naturally toggle-able**, making this approach ideal for progressive feature rollouts in enterprise environments.
