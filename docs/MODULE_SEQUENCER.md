# ModuleSequencer Documentation

## Overview

The `ModuleSequencer` is the core architectural component of the asciidoc-dita-toolkit's plugin system. It provides enterprise-grade plugin management with automatic dependency resolution, hierarchical configuration management, and robust error handling.

## Architecture

### Core Components

```python
# Base class for all plugins
class ADTModule(ABC)

# Plugin state management  
class ModuleState(Enum)

# Resolution results
class ModuleResolution

# Main orchestrator
class ModuleSequencer
```

### Plugin Discovery

The ModuleSequencer automatically discovers plugins via Python entry points:

```toml
# pyproject.toml
[project.entry-points."adt.modules"]
EntityReference = "asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference:EntityReferenceModule"
CrossReference = "asciidoc_dita_toolkit.asciidoc_dita.plugins.CrossReference:CrossReferenceModule"
```

## Configuration Hierarchy

The system uses a 3-tier configuration model with clear precedence:

```
CLI Arguments > User Config > Developer Config
```

### Developer Configuration (Required)
```json
{
  "version": "1.0",
  "modules": [
    {
      "name": "EntityReference",
      "required": true,
      "dependencies": [],
      "config": {
        "strict_mode": false
      }
    },
    {
      "name": "CrossReference", 
      "required": false,
      "dependencies": ["EntityReference"],
      "config": {
        "validate_refs": true
      }
    }
  ],
  "global_config": {
    "debug": false,
    "output_format": "dita"
  }
}
```

### User Configuration (Optional)
```json
{
  "enabledModules": ["EntityReference", "CrossReference"],
  "disabledModules": ["ExampleBlock"],
  "moduleOverrides": {
    "CrossReference": {
      "strict_mode": true
    }
  }
}
```

### CLI Overrides (Temporary)
```bash
adt --enable-module=CrossReference --disable-module=ExampleBlock
```

## Dependency Management

### Automatic Resolution

The ModuleSequencer automatically:
1. **Discovers dependencies** from module declarations and config
2. **Validates existence** of all required dependencies  
3. **Detects circular dependencies** using DFS algorithms
4. **Orders initialization** via topological sorting

### Example Dependency Chain

**ModuleSequencer Orchestration Only** (not used by CLI commands):

```
EntityReference (no dependencies)
    ↓
CrossReference (depends on EntityReference)
    ↓  
ContextAnalyzer (depends on CrossReference)
    ↓
ContextMigrator (depends on ContextAnalyzer)
```

**Important**: CLI commands like `adt ContextAnalyzer` bypass this dependency chain entirely and execute plugins directly without dependency resolution.

### Circular Dependency Detection
```python
# This would be detected and prevented:
ModuleA → ModuleB → ModuleC → ModuleA

# Error: "Circular dependency detected: ModuleA -> ModuleB -> ModuleC -> ModuleA"
```

## Module States

```python
class ModuleState(Enum):
    ENABLED = "enabled"     # Active and functioning
    DISABLED = "disabled"   # Intentionally disabled
    FAILED = "failed"       # Error during loading/init
    PENDING = "pending"     # Waiting for dependencies
```

## API Reference

### Basic Usage

```python
from adt_core.module_sequencer import ModuleSequencer

# Initialize sequencer
sequencer = ModuleSequencer()

# Load configurations  
sequencer.load_configurations(
    dev_config_path="config/developer.json",
    user_config_path="~/.adt/config.json"
)

# Discover available modules
sequencer.discover_modules()

# Sequence modules with CLI overrides
resolutions, errors = sequencer.sequence_modules(
    cli_overrides={"CrossReference": True, "ExampleBlock": False}
)

# Check system status
status = sequencer.get_module_status()
```

### Creating Custom Modules

```python
from adt_core.module_sequencer import ADTModule

class MyCustomModule(ADTModule):
    @property
    def name(self) -> str:
        return "MyCustomModule"
    
    @property  
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def dependencies(self) -> List[str]:
        return ["EntityReference"]  # Depends on EntityReference
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
        # Initialize module with config
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Process the context and return results
        return {"processed": True}
    
    def cleanup(self) -> None:
        # Clean up resources
        pass
```

### Error Handling

```python
from adt_core.exceptions import (
    CircularDependencyError,
    MissingDependencyError, 
    ConfigurationError
)

try:
    sequencer.load_configurations(dev_config, user_config)
    sequencer.discover_modules()
    resolutions, errors = sequencer.sequence_modules()
    
    if errors:
        for error in errors:
            logger.error(f"Sequencing error: {error}")
            
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
except MissingDependencyError as e:
    logger.error(f"Missing dependency: {e}")
except CircularDependencyError as e:
    logger.error(f"Circular dependency: {e}")
```

## Advanced Features

### Dual Plugin Architecture

The asciidoc-dita-toolkit uses a dual plugin architecture that maintains backward compatibility while providing modern orchestration capabilities:

#### CLI Plugin System (Legacy Interface)
- **Direct execution**: Commands like `adt ContextAnalyzer` bypass ModuleSequencer
- **Original plugin code**: Uses plugins in `asciidoc_dita_toolkit/asciidoc_dita/plugins/`
- **No dependency resolution**: Each plugin runs independently
- **Immediate execution**: No configuration or sequencing overhead

```bash
# These commands use the legacy interface directly:
adt ContextAnalyzer --recursive --directory=./docs
adt EntityReference --file=example.adoc
adt CrossReference --validate-refs
```

#### ModuleSequencer System (Modern Architecture)
- **Orchestrated execution**: Uses ADTModule wrappers in `modules/`
- **Dependency resolution**: Automatic dependency management and ordering
- **Configuration management**: 3-tier config system with validation
- **Enterprise features**: Error handling, status monitoring, cleanup

```python
# ModuleSequencer provides orchestrated execution:
sequencer = ModuleSequencer()
sequencer.sequence_modules()  # Runs plugins in dependency order
```

#### How They Work Together

The ADTModule wrappers actually **call the original plugin code**:

```python
# modules/entity_reference.py (ADTModule wrapper)
def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    # Import and use the legacy plugin functionality
    from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import process_file
    
    # Call the original plugin code
    process_file(filepath)
```

This design provides:
- **100% backward compatibility**: All CLI commands work unchanged
- **Modern orchestration**: ModuleSequencer for complex workflows
- **Code reuse**: Both systems use the same core plugin logic
- **Migration path**: Gradual transition to ModuleSequencer when needed

### Legacy Plugin Support

The ModuleSequencer includes transition support for legacy plugins:

```python
# During migration, legacy plugins were tracked
LEGACY_PLUGINS = {"OldPlugin", "AnotherLegacyPlugin"}  # Historical

# Now all plugins migrated:
LEGACY_PLUGINS = set()  # All plugins have been migrated to ADTModule
```

**Note**: `LEGACY_PLUGINS = set()` refers to ModuleSequencer tracking, not the existence of legacy plugin code. The original plugin code remains active and is used by both the CLI system and ADTModule wrappers.

### Module Status Reporting

```python
status = sequencer.get_module_status()

# Returns comprehensive status:
{
  "modules": [
    {
      "name": "EntityReference",
      "state": "enabled", 
      "version": "2.1.0",
      "dependencies": [],
      "init_order": 0,
      "error_message": None
    }
  ],
  "total_enabled": 5,
  "total_disabled": 1, 
  "total_failed": 0,
  "errors": []
}
```

### Configuration Validation

```python
# Validate configuration before processing
errors = sequencer.validate_configuration()

if errors:
    for error in errors:
        print(f"Config error: {error}")
    return False
```

## Performance Characteristics

### Initialization Time
- **Module Discovery**: O(n) where n = number of entry points
- **Dependency Resolution**: O(n + e) where e = number of dependency edges  
- **Topological Sort**: O(n + e) using Kahn's algorithm

### Memory Usage
- **Minimal overhead**: Only loaded modules kept in memory
- **Lazy loading**: Modules loaded on-demand during discovery
- **Cleanup support**: Modules can free resources via cleanup()

## Best Practices

### Module Development
1. **Keep dependencies minimal** - Only declare necessary dependencies
2. **Use semantic versioning** - Follow semver for version strings
3. **Implement cleanup()** - Free resources when module shuts down
4. **Handle config gracefully** - Provide sensible defaults
5. **Document dependencies** - Clear documentation of what each dependency provides

### Configuration Management
1. **Required vs Optional** - Mark critical modules as required
2. **Reasonable defaults** - User config should be optional
3. **Validation** - Validate config structure and values
4. **Documentation** - Document all configuration options

### Error Handling  
1. **Graceful degradation** - System continues when non-critical modules fail
2. **Clear error messages** - Specific, actionable error descriptions
3. **Dependency validation** - Check dependencies at configuration time
4. **Status monitoring** - Regular health checks via get_module_status()

## Migration Guide

### From Legacy Plugins

The ModuleSequencer successfully migrated all legacy plugins through a 5-phase process:

1. **Phase 1**: Legacy warnings suppression
2. **Phase 2-4**: Individual plugin migrations  
3. **Phase 5**: Final cleanup and completion

All plugins now inherit from `ADTModule` and benefit from:
- Automatic dependency management
- Unified configuration system
- Standardized error handling  
- Professional plugin architecture

### Backward Compatibility

Despite the architecture changes, **100% backward compatibility** is maintained:
- All original CLI commands work unchanged
- Existing configuration files supported
- No breaking changes for end users
- Legacy support infrastructure remains available

## Troubleshooting

### Common Issues

**Module not found**
```
Error: Module 'MyModule' not found
Solution: Check entry point registration in pyproject.toml
```

**Circular dependency**  
```
Error: Circular dependency detected: A -> B -> C -> A
Solution: Remove circular dependency by refactoring module interfaces
```

**Missing dependency**
```
Error: Module 'A' depends on missing module 'B' 
Solution: Install missing module or update dependencies
```

**Configuration error**
```
Error: Developer config missing 'version' field
Solution: Add required fields to developer configuration
```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.getLogger("adt.sequencer").setLevel(logging.DEBUG)

# Will show detailed sequencing information:
# - Module discovery details
# - Dependency resolution steps  
# - Configuration loading progress
# - Error details and stack traces
```

## Future Enhancements

The ModuleSequencer architecture supports future enhancements:

- **Hot reloading** - Reload modules without restart
- **Plugin marketplace** - Discover and install third-party plugins
- **Performance monitoring** - Track module execution times
- **A/B testing** - Enable/disable modules for testing
- **Module versioning** - Support multiple versions simultaneously

The robust foundation provided by the ModuleSequencer ensures the asciidoc-dita-toolkit can continue evolving while maintaining stability and compatibility.
