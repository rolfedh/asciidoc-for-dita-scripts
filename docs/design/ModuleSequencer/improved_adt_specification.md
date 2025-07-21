# Complete ADT Module Configuration Design (Python Implementation)

This document defines a complete, GenAI-friendly specification for managing modular components (modules) in ADT-based Python projects.

---

## 1. Key Concepts

- **Plugin Metadata**: Defines each module's name, actual version, release status (GA/preview), and dependencies
- **Developer Config** (`.adt-modules.json`): Specifies module execution order, requirements, dependencies, and version constraints
- **User Config** (`adt-user-config.json`): Enables or disables optional modules only
- **CLI Flags**: Temporary command-line overrides for testing or one-off runs
- **Module Dependencies**: Explicit dependency relationships between modules with version constraints
- **Module Discovery**: Automatic detection via Python entry points and filesystem scanning
- **Module Lifecycle**: Initialization, execution, and cleanup phases with proper error handling
- **ModuleSequencer**: Main class that sequences, configures, and manages all modules including discovery, dependency resolution, and proper initialization ordering

---

## 2. Module Discovery Mechanism

### Python Entry Points Integration
```python
# pyproject.toml integration
[project.entry-points."adt.modules"]
entity_reference = "adt_modules.entity_reference:EntityReferenceModule"
content_type = "adt_modules.content_type:ContentTypeModule"
directory_config = "adt_modules.directory_config:DirectoryConfigModule"
```

### Module Base Class
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

class ADTModule(ABC):
    """Base class for all ADT modules."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Module name identifier."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Module version (semantic versioning)."""
        pass
    
    @property
    def dependencies(self) -> List[str]:
        """List of required module names."""
        return []
    
    @property
    def release_status(self) -> str:
        """Release status: 'GA' or 'preview'."""
        return "GA"
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the module with configuration."""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module logic."""
        pass
    
    def cleanup(self) -> None:
        """Clean up module resources."""
        pass
```

---

## 3. Configuration Format

### Developer Config (`.adt-modules.json`)
```json
{
  "version": "1.0",
  "modules": [
    {
      "name": "EntityReference",                   // REFERENCE: Must match module's actual name
      "required": true,                            // CONSTRAINT: Developer decides if required
      "version": ">=1.2.0",                       // CONSTRAINT: Version requirement (actual version comes from module)
      "dependencies": [],                          // CONSTRAINT: Additional dependencies (module's dependencies auto-detected)
      "init_order": 1,                            // CONSTRAINT: Developer-controlled initialization order
      "config": {                                 // CONFIGURATION: Values passed to module.initialize()
        "timeout_seconds": 30
      }
    },
    {
      "name": "ContentType",                       // REFERENCE: Must match module's actual name
      "required": false,                           // CONSTRAINT: Developer decides if required
      "version": ">=2.0.0",                       // CONSTRAINT: Version requirement
      "dependencies": ["EntityReference"],         // CONSTRAINT: Additional dependencies
      "init_order": 2,                            // CONSTRAINT: Developer-controlled initialization order
      "config": {                                 // CONFIGURATION: Values passed to module.initialize()
        "cache_enabled": true
      }
    },
    {
      "name": "DirectoryConfig",                   // REFERENCE: Must match module's actual name
      "required": false,                           // CONSTRAINT: Developer decides if required
      "version": "~1.0.0",                        // CONSTRAINT: Version requirement
      "dependencies": ["ContentType", "EntityReference"], // CONSTRAINT: Additional dependencies
      "init_order": 3                             // CONSTRAINT: Developer-controlled initialization order
    }
  ],
  "global_config": {                              // CONFIGURATION: Global settings for all modules
    "max_retries": 3,
    "log_level": "INFO"
  }
}
```

### User Config (`adt-user-config.json`)
```json
{
  "version": "1.0",
  "enabledModules": ["ContentType"],
  "disabledModules": ["DirectoryConfig"],
  "moduleOverrides": {
    "ContentType": {
      "cache_enabled": false
    }
  }
}
```

---

## 4. Dependency Resolution Algorithm

### Core Resolution Logic
```python
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

class ModuleState(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    FAILED = "failed"
    PENDING = "pending"

class ADTModuleError(Exception):
    """Base exception for ADT module errors."""
    pass

class CircularDependencyError(ADTModuleError):
    """Raised when circular dependencies are detected."""
    pass

class MissingDependencyError(ADTModuleError):
    """Raised when required dependencies are missing."""
    pass

class VersionConflictError(ADTModuleError):
    """Raised when version constraints cannot be satisfied."""
    pass

@dataclass
class ModuleResolution:
    name: str
    state: ModuleState
    version: str
    dependencies: List[str]
    init_order: int
    config: Dict[str, Any]
    error_message: Optional[str] = None

class ModuleSequencer:
    """
    Main class responsible for sequencing, configuring, and managing ADT modules.
    
    Handles module discovery, dependency resolution, configuration management,
    and proper initialization sequencing.
    """
    
    def __init__(self):
        self.available_modules: Dict[str, ADTModule] = {}
        self.dev_config: Dict[str, Any] = {}
        self.user_config: Dict[str, Any] = {}
        self.logger = logging.getLogger("adt.sequencer")
    
    def load_configurations(self, dev_config_path: str, user_config_path: str) -> None:
        """Load developer and user configurations."""
        # Implementation for loading JSON configurations
        pass
    
    def discover_modules(self) -> None:
        """Discover available modules via entry points."""
        # Implementation for module discovery
        pass
    
    def sequence_modules(
        self,
        cli_overrides: Optional[Dict[str, bool]] = None
    ) -> Tuple[List[ModuleResolution], List[str]]:
        """
        Sequence modules with comprehensive dependency handling.
        
        Returns:
            Tuple of (resolved_modules, error_messages)
        """
        errors = []
        resolutions = []
        
        try:
            # Step 1: Build dependency graph
            dep_graph = self._build_dependency_graph()
            
            # Step 2: Detect circular dependencies
            self._detect_circular_dependencies(dep_graph)
            
            # Step 3: Topological sort for initialization order
            sorted_modules = self._topological_sort(dep_graph)
            
            # Step 4: Apply user preferences and CLI overrides
            final_modules = self._apply_user_preferences(
                sorted_modules, cli_overrides
            )
            
            # Step 5: Validate final configuration
            resolutions = self._validate_final_config(final_modules)
            
        except (CircularDependencyError, MissingDependencyError, VersionConflictError) as e:
            errors.append(str(e))
            self.logger.error(f"Module sequencing failed: {e}")
        
        return resolutions, errors

    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build directed dependency graph."""
        graph = {}
        
        for module_config in self.dev_config.get("modules", []):
            module_name = module_config["name"]
            dependencies = set(module_config.get("dependencies", []))
            
            # Validate dependencies exist
            for dep in dependencies:
                if dep not in self.available_modules:
                    raise MissingDependencyError(f"Module '{module_name}' depends on missing module '{dep}'")
            
            graph[module_name] = dependencies
        
        return graph

    def _detect_circular_dependencies(self, graph: Dict[str, Set[str]]) -> None:
        """Detect circular dependencies using DFS."""
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {node: WHITE for node in graph}
        
        def dfs(node: str, path: List[str]) -> None:
            if colors[node] == GRAY:
                cycle = path[path.index(node):] + [node]
                raise CircularDependencyError(f"Circular dependency detected: {' -> '.join(cycle)}")
            
            if colors[node] == BLACK:
                return
            
            colors[node] = GRAY
            path.append(node)
            
            for neighbor in graph.get(node, set()):
                dfs(neighbor, path.copy())
            
            colors[node] = BLACK
        
        for node in graph:
            if colors[node] == WHITE:
                dfs(node, [])

    def _topological_sort(self, graph: Dict[str, Set[str]]) -> List[str]:
        """Return topologically sorted list of modules."""
        in_degree = {node: 0 for node in graph}
        
        # Calculate in-degrees
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] = in_degree.get(neighbor, 0) + 1
        
        # Kahn's algorithm
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph.get(current, set()):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result

    def _apply_user_preferences(
        self,
        sorted_modules: List[str],
        cli_overrides: Optional[Dict[str, bool]]
    ) -> List[str]:
        """Apply user preferences while respecting requirements."""
        enabled_modules = []
        user_enabled = set(self.user_config.get("enabledModules", []))
        user_disabled = set(self.user_config.get("disabledModules", []))
        cli_overrides = cli_overrides or {}
        
        # Build module requirements map
        module_requirements = {}
        for module_config in self.dev_config.get("modules", []):
            module_requirements[module_config["name"]] = module_config.get("required", False)
        
        for module_name in sorted_modules:
            is_required = module_requirements.get(module_name, False)
            cli_override = cli_overrides.get(module_name)
            
            # Priority: CLI > User Config > Developer Config
            if cli_override is not None:
                if cli_override or is_required:
                    enabled_modules.append(module_name)
            elif is_required:
                enabled_modules.append(module_name)
                if module_name in user_disabled:
                    self.logger.warning(f"Ignoring user disable for required module: {module_name}")
            elif module_name in user_enabled:
                enabled_modules.append(module_name)
            elif module_name not in user_disabled:
                enabled_modules.append(module_name)  # Default: enabled
        
        return enabled_modules

    def _validate_final_config(
        self,
        enabled_modules: List[str]
    ) -> List[ModuleResolution]:
        """Validate and create final module resolutions."""
        resolutions = []
        
        for i, module_name in enumerate(enabled_modules):
            if module_name not in self.available_modules:
                resolutions.append(ModuleResolution(
                    name=module_name,
                    state=ModuleState.FAILED,
                    version="unknown",
                    dependencies=[],
                    init_order=i,
                    config={},
                    error_message=f"Module '{module_name}' not found"
                ))
                continue
            
            module = self.available_modules[module_name]
            resolutions.append(ModuleResolution(
                name=module_name,
                state=ModuleState.ENABLED,
                version=module.version,
                dependencies=module.dependencies,
                init_order=i,
                config={}
            ))
        
        return resolutions

# Example Usage
sequencer = ModuleSequencer()
sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')
sequencer.discover_modules()

# Sequence modules with optional CLI overrides
resolutions, errors = sequencer.sequence_modules(
    cli_overrides={"Analytics": False, "DebugModule": True}
)

# Initialize and run modules in the resolved order
for resolution in resolutions:
    if resolution.state == ModuleState.ENABLED:
        module = sequencer.available_modules[resolution.name]
        module.initialize(resolution.config)
        result = module.execute({})
        print(f"Module {resolution.name} executed successfully")
```

---

## 5. Enhanced Rules for Module State

```python
def determine_module_state(
    module_name: str,
    is_required: bool,
    user_enabled: List[str],
    user_disabled: List[str],
    cli_overrides: Optional[Dict[str, bool]] = None
) -> ModuleState:
    """
    Determine final module state based on configuration hierarchy.
    
    Priority (High → Low):
    1. CLI flags (temporary override)
    2. Required status (cannot be disabled)
    3. User explicit enable/disable
    4. Default: enabled
    """
    cli_overrides = cli_overrides or {}
    
    # CLI override has highest priority
    if module_name in cli_overrides:
        return ModuleState.ENABLED if cli_overrides[module_name] else ModuleState.DISABLED
    
    # Required modules cannot be disabled
    if is_required:
        return ModuleState.ENABLED
    
    # User explicit disable
    if module_name in user_disabled:
        return ModuleState.DISABLED
    
    # User explicit enable or default enabled
    return ModuleState.ENABLED
```

---

## 6. Comprehensive Error Handling

### Custom Exception Hierarchy
```python
class ADTModuleError(Exception):
    """Base exception for all ADT module errors."""
    pass

class ConfigurationError(ADTModuleError):
    """Configuration file errors."""
    pass

class ModuleNotFoundError(ADTModuleError):
    """Module discovery errors."""
    pass

class ModuleInitializationError(ADTModuleError):
    """Module initialization failures."""
    pass

class DependencyError(ADTModuleError):
    """Dependency resolution errors."""
    pass

class CircularDependencyError(DependencyError):
    """Circular dependency detection."""
    pass

class MissingDependencyError(DependencyError):
    """Missing required dependencies."""
    pass

class VersionConflictError(DependencyError):
    """Version constraint conflicts."""
    pass

# Error handling scenarios
ERROR_SCENARIOS = {
    "circular_dependency": "Modules have circular dependencies",
    "missing_dependency": "Required dependency module not found",
    "version_conflict": "Module version constraints cannot be satisfied",
    "initialization_failure": "Module failed to initialize properly",
    "corrupted_config": "Configuration file is malformed or corrupted",
    "permission_denied": "Insufficient permissions to read configuration",
    "module_not_found": "Specified module does not exist",
    "resource_exhaustion": "Insufficient system resources for module",
    "timeout": "Module operation timed out",
    "validation_error": "Configuration validation failed"
}
```

---

## 7. Enhanced JSON Schema Definitions

### Developer Config Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.adt.com/developer-config.json",
  "title": "ADT Developer Configuration",
  "type": "object",
  "required": ["version", "modules"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$",
      "description": "Configuration schema version"
    },
    "modules": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/module"
      },
      "uniqueItems": true
    },
    "global_config": {
      "type": "object",
      "properties": {
        "max_retries": {"type": "integer", "minimum": 0},
        "log_level": {"enum": ["DEBUG", "INFO", "WARNING", "ERROR"]},
        "timeout_seconds": {"type": "integer", "minimum": 1}
      }
    }
  },
  "$defs": {
    "module": {
      "type": "object",
      "required": ["name", "required"],
      "properties": {
        "name": {
          "type": "string",
          "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
          "description": "Module identifier"
        },
        "required": {
          "type": "boolean",
          "description": "Whether module is required"
        },
        "version": {
          "type": "string",
          "pattern": "^(>=|<=|>|<|\\^|~)?\\d+\\.\\d+\\.\\d+.*$",
          "description": "Version constraint (semver)"
        },
        "dependencies": {
          "type": "array",
          "items": {"type": "string"},
          "uniqueItems": true,
          "description": "List of dependent module names"
        },
        "init_order": {
          "type": "integer",
          "minimum": 1,
          "description": "Initialization order priority"
        },
        "config": {
          "type": "object",
          "description": "Module-specific configuration"
        }
      }
    }
  }
}
```

### User Config Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.adt.com/user-config.json",
  "title": "ADT User Configuration",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$"
    },
    "enabledModules": {
      "type": "array",
      "items": {"type": "string"},
      "uniqueItems": true,
      "description": "Explicitly enabled optional modules"
    },
    "disabledModules": {
      "type": "array",
      "items": {"type": "string"},
      "uniqueItems": true,
      "description": "Explicitly disabled optional modules"
    },
    "moduleOverrides": {
      "type": "object",
      "patternProperties": {
        "^[A-Za-z][A-Za-z0-9_]*$": {
          "type": "object",
          "description": "Module-specific configuration overrides"
        }
      }
    }
  },
  "not": {
    "anyOf": [
      {
        "type": "object",
        "properties": {
          "enabledModules": {"contains": {"$ref": "#/properties/disabledModules/items"}},
          "disabledModules": {"contains": {"$ref": "#/properties/enabledModules/items"}}
        }
      }
    ]
  }
}
```

---

## 8. CLI Interface Design

### Available Commands
```bash
# Module status and information
adt modules status                      # Show all modules and their current status
adt modules status --module <name>      # Show specific module details
adt modules list                        # List all available modules

# Module management
adt modules enable <module>             # Enable a specific module
adt modules disable <module>            # Disable a specific module
adt modules enable <mod1> <mod2> <mod3> # Enable multiple modules

# Configuration and validation
adt modules validate                    # Validate current configuration
adt modules config --format json       # Output current config as JSON

# Dependency and performance analysis
adt modules deps <module>               # Show module dependencies
adt modules performance                 # Show module execution times

# Temporary overrides for testing
adt run --enable-module=<name>          # Run with temporary module override
adt run --disable-module=<name>         # Run with module temporarily disabled
```

---

## 9. CLI Output Example
```
ADT Module Status:
================
✓ EntityReference     [required, enabled, v1.2.1, GA]
  └─ Dependencies: none
✓ ContentType         [optional, enabled, v2.1.0, GA]  
  └─ Dependencies: EntityReference
⨯ DirectoryConfig     [optional, disabled, v1.0.3, preview]
  └─ Dependencies: ContentType, EntityReference

Initialization Order: EntityReference → ContentType
Total: 2 enabled, 1 disabled, 0 failed

Use 'adt modules enable DirectoryConfig' to enable disabled modules.
```

---

## 10. File Structure and Organization

```
adt_project/
├── .adt-modules.json              # Developer configuration
├── adt-user-config.json           # User configuration (optional)
├── src/
│   └── adt_core/
│       ├── __init__.py
│       ├── module_sequencer.py     # ModuleSequencer implementation
│       ├── exceptions.py           # Custom exception classes
│       └── schemas/                # JSON schema files
│           ├── developer_config.json
│           └── user_config.json
├── modules/                       # Module implementations directory
│   ├── entity_reference/
│   ├── content_type/
│   └── directory_config/
├── tests/
│   ├── test_module_sequencer.py
│   ├── test_configuration.py
│   ├── test_dependencies.py
│   └── fixtures/
│       ├── sample_dev_config.json
│       └── sample_user_config.json
└── pyproject.toml                 # Package configuration
```

---

## 11. Enhanced Test Cases

| Module          | Required | Dependencies        | User Enabled | User Disabled | CLI Override | Final State | Init Order |
|-----------------|----------|---------------------|--------------|---------------|--------------|-------------|------------|
| EntityReference | true     | []                  | —            | ✓            | —            | enabled     | 1          |
| ContentType     | false    | [EntityReference]   | ✓            | —            | —            | enabled     | 2          |
| DirectoryConfig | false    | [ContentType, ER]   | —            | ✓            | —            | disabled    | —          |
| CustomFilter    | false    | []                  | —            | —            | true         | enabled     | 3          |
| ReportGenerator | false    | [CustomFilter]      | —            | —            | —            | enabled     | 4          |

---

## 12. Configuration Priority (High → Low)

1. **CLI flags** (temporary override): `--enable-module=X --disable-module=Y`
2. **Required status** (from developer config): Cannot be overridden by user
3. **User explicit preferences** (user config): Enable/disable optional modules
4. **Default behavior**: Optional modules enabled by default
5. **Plugin metadata**: Release status only (GA/preview)

---

**Footnotes - Additional Improvements for Future Iterations:**

*Medium Priority Enhancements:*
- Enhanced JSON schemas with cross-reference validation between developer and user configs
- Performance optimizations including configuration caching strategies and lazy module loading  
- Comprehensive testing strategy with unit tests, integration tests, property-based testing, and performance benchmarks
- Security considerations including configuration validation against injection attacks and module signature verification

*Low Priority Enhancements:*
- Monitoring and observability features with structured logging and metrics collection
- Migration strategies for handling configuration format changes and backwards compatibility
- Plugin ecosystem considerations including module marketplace, automatic updates, and community modules
- Advanced CLI features like interactive configuration wizard and module recommendation engine
- Internationalization support for error messages and CLI output

This specification now provides a complete, implementation-ready foundation for Python-based ADT module management with robust dependency resolution, comprehensive error handling, and proper integration with Python packaging ecosystem.