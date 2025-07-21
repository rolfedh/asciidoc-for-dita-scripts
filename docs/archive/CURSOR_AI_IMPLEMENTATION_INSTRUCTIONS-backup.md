# Cursor AI Implementation Instructions: ADTModule Architecture Migration

## Overview

Migrate the legacy plugin architecture to the standardized ADTModule pattern to enable better external plugin development and integration. This implements the recommendations from `architecture-recommendation-adopt-adtmodule-pattern.md`.

## Phase 1: Immediate Actions (Current Session)

### 1. Suppress Legacy Plugin Warnings

**File**: `/asciidoc_dita_toolkit/asciidoc_dita/plugin_loader.py` (or equivalent)

**Task**: Modify the plugin discovery mechanism to suppress the warning messages:
```
Module ContentType does not inherit from ADTModule
Module DirectoryConfig does not inherit from ADTModule
Module EntityReference does not inherit from ADTModule
```

**Implementation**:
- Add a `--quiet` or `--suppress-warnings` flag
- Or convert warnings to debug-level logging
- Keep warnings for development mode but hide in production

### 2. Create Plugin Development Guide

**File**: `/docs/PLUGIN_DEVELOPMENT_GUIDE.md`

**Content Structure**:
```markdown
# Plugin Development Guide

## Quick Start
- 5-minute tutorial for creating a basic plugin
- Template repository link
- Hello World example

## ADTModule Interface
- Required methods and properties
- Configuration handling
- Error handling best practices

## Testing Your Plugin
- Unit testing framework
- Integration testing
- Validation tools

## Distribution
- PyPI publishing
- Entry points configuration
- Version management

## Examples
- Simple processing plugin
- Plugin with dependencies
- Configuration-heavy plugin
```

## Phase 2: Legacy Plugin Migration

### 3. Migrate EntityReference Plugin

**File**: `/asciidoc_dita_toolkit/asciidoc_dita/plugins/EntityReference.py`

**Current Pattern**:
```python
def main(args):
    """Main function for the EntityReference plugin."""
    process_adoc_files(args, process_file)

def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser("EntityReference", help=__description__)
    common_arg_parser(parser)
    parser.set_defaults(func=main)
```

**Target Pattern**:
```python
class EntityReferenceModule(ADTModule):
    @property
    def name(self) -> str:
        return "EntityReference"

    @property
    def version(self) -> str:
        return "1.2.1"  # Use semantic versioning

    @property
    def dependencies(self) -> List[str]:
        return []  # No dependencies

    @property
    def release_status(self) -> str:
        return "GA"

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize with configuration."""
        self.timeout_seconds = config.get("timeout_seconds", 30)
        self.cache_size = config.get("cache_size", 1000)

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the entity reference replacement."""
        # Move main() logic here
        # Return results dict
        return {"files_processed": count, "entities_replaced": total}

    def cleanup(self) -> None:
        """Clean up resources."""
        pass

# Keep legacy function for backward compatibility during transition
def main(args):
    """Legacy main function - delegates to ADTModule."""
    module = EntityReferenceModule()
    module.initialize({})
    # Adapt args to context format
    result = module.execute({"args": args})
    return result
```

### 4. Migrate ContentType Plugin

**File**: `/asciidoc_dita_toolkit/asciidoc_dita/plugins/ContentType.py`

Apply the same migration pattern as EntityReference:
- Create `ContentTypeModule(ADTModule)` class
- Move logic from `main()` to `execute()`
- Add proper metadata (name, version, dependencies)
- Keep legacy `main()` for compatibility

### 5. Migrate DirectoryConfig Plugin

**File**: `/asciidoc_dita_toolkit/asciidoc_dita/plugins/DirectoryConfig.py`

Apply the same migration pattern with attention to:
- Dependencies on other modules
- Configuration requirements
- File system operations

## Phase 3: Framework Enhancements

### 6. Update Plugin Loader

**File**: `/asciidoc_dita_toolkit/asciidoc_dita/plugin_loader.py`

**Requirements**:
- Support both legacy and ADTModule plugins during transition
- Automatic discovery via entry points
- Dependency resolution for ADTModule plugins
- Configuration passing
- Error handling and reporting

**Implementation**:
```python
class PluginLoader:
    def __init__(self):
        self.legacy_plugins = {}
        self.adt_modules = {}
        self.module_sequencer = ModuleSequencer()

    def discover_plugins(self):
        """Discover both legacy and ADTModule plugins."""
        # Legacy plugin discovery (existing logic)
        self._discover_legacy_plugins()

        # ADTModule discovery via entry points
        self._discover_adt_modules()

    def load_plugin(self, name: str, config: Dict[str, Any] = None):
        """Load plugin with automatic type detection."""
        if name in self.adt_modules:
            return self._load_adt_module(name, config)
        elif name in self.legacy_plugins:
            return self._load_legacy_plugin(name, config)
        else:
            raise PluginNotFoundError(f"Plugin '{name}' not found")
```

### 7. Create Plugin Template Repository Structure

**Directory**: `/templates/plugin-template/`

**Structure**:
```
plugin-template/
├── pyproject.toml              # Package configuration
├── README.md                   # Plugin documentation
├── src/
│   └── my_adt_plugin/
│       ├── __init__.py
│       ├── plugin.py           # Main plugin implementation
│       └── config_schema.json  # Configuration schema
├── tests/
│   ├── test_plugin.py         # Unit tests
│   └── test_integration.py    # Integration tests
└── docs/
    └── usage.md               # Usage documentation
```

**File**: `/templates/plugin-template/src/my_adt_plugin/plugin.py`

```python
"""
Template for creating ADT plugins.

Replace 'MyPlugin' with your plugin name and implement the required methods.
"""

from typing import Dict, List, Any
from adt_core import ADTModule

class MyPluginModule(ADTModule):
    """Template plugin - replace with your implementation."""

    @property
    def name(self) -> str:
        return "MyPlugin"  # Change this to your plugin name

    @property
    def version(self) -> str:
        return "1.0.0"  # Use semantic versioning

    @property
    def dependencies(self) -> List[str]:
        return []  # List any required dependencies

    @property
    def release_status(self) -> str:
        return "preview"  # "GA" for stable, "preview" for beta

    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize your plugin with configuration.

        Args:
            config: Configuration dictionary from JSON files
        """
        # Store configuration values
        self.debug_mode = config.get("debug_mode", False)
        self.max_files = config.get("max_files", 1000)

        # Initialize any resources
        # e.g., database connections, file handles, etc.

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute your plugin logic.

        Args:
            context: Execution context including results from dependencies

        Returns:
            Dictionary with your plugin's results
        """
        # Your plugin implementation here

        # Example: Access dependency results
        dependency_result = context.get("SomeDependency", {})

        # Example: Process files or data
        processed_count = 0

        # Return results for other plugins to use
        return {
            "files_processed": processed_count,
            "success": True,
            "data": {"key": "value"}
        }

    def cleanup(self) -> None:
        """Clean up any resources."""
        # Close files, database connections, etc.
        pass
```

### 8. Update Documentation

**File**: `/README.md`

Add section about plugin development:
```markdown
## 🔌 Plugin Development

ADT supports external plugins for extending functionality.

### Quick Start
1. Clone the plugin template: `git clone https://github.com/your-org/adt-plugin-template`
2. Implement the `ADTModule` interface
3. Publish to PyPI: `pip install your-adt-plugin`
4. Users can install and use: `adt YourPlugin -r`

### Resources
- [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT_GUIDE.md)
- [Plugin Template Repository](https://github.com/your-org/adt-plugin-template)
- [API Documentation](docs/API.md)
```

## Phase 4: Testing and Validation

### 9. Create Test Suite for Plugin Architecture

**File**: `/tests/test_plugin_architecture.py`

```python
import pytest
from adt_core import ADTModule, ModuleSequencer

class TestPluginArchitecture:
    def test_legacy_plugin_compatibility(self):
        """Ensure legacy plugins still work during transition."""
        pass

    def test_adt_module_discovery(self):
        """Test automatic discovery of ADTModule plugins."""
        pass

    def test_dependency_resolution(self):
        """Test dependency resolution for ADTModule plugins."""
        pass

    def test_configuration_passing(self):
        """Test configuration is properly passed to plugins."""
        pass

    def test_mixed_plugin_types(self):
        """Test system with both legacy and ADTModule plugins."""
        pass
```

### 10. Update Entry Points Configuration

**File**: `/pyproject.toml`

```toml
[project.entry-points."adt.modules"]
EntityReference = "asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference:EntityReferenceModule"
ContentType = "asciidoc_dita_toolkit.asciidoc_dita.plugins.ContentType:ContentTypeModule"
DirectoryConfig = "asciidoc_dita_toolkit.asciidoc_dita.plugins.DirectoryConfig:DirectoryConfigModule"
ContextAnalyzer = "asciidoc_dita_toolkit.asciidoc_dita.plugins.ContextAnalyzer:ContextAnalyzerModule"
ContextMigrator = "asciidoc_dita_toolkit.asciidoc_dita.plugins.ContextMigrator:ContextMigratorModule"
CrossReference = "asciidoc_dita_toolkit.asciidoc_dita.plugins.CrossReference:CrossReferenceModule"
```

## Implementation Priorities

### High Priority (Week 1)
1. ✅ Suppress legacy warnings (#1)
2. ✅ Migrate EntityReference plugin (#3)
3. ✅ Create basic plugin development guide (#2)

### Medium Priority (Week 2)
4. ✅ Migrate ContentType and DirectoryConfig (#4, #5)
5. ✅ Update plugin loader for dual support (#6)
6. ✅ Create plugin template (#7)

### Lower Priority (Week 3-4)
7. ✅ Comprehensive testing (#9)
8. ✅ Documentation updates (#8)
9. ✅ Entry points configuration (#10)

## Success Criteria

- ✅ All legacy plugins migrated to ADTModule
- ✅ No breaking changes for existing users
- ✅ External developers can create plugins using template
- ✅ Plugin discovery works automatically
- ✅ Dependency resolution functions correctly
- ✅ Comprehensive documentation exists
- ✅ Test suite validates both legacy and new architectures

## Notes for Cursor AI

- **Preserve existing functionality** - this is a refactoring, not a rewrite
- **Maintain backward compatibility** during transition
- **Focus on developer experience** - make plugin creation as easy as possible
- **Use existing ADTModule base class** from the codebase
- **Follow existing code style** and patterns
- **Add comprehensive docstrings** to all new code
- **Create meaningful test cases** for all new functionality

The goal is to transform the plugin ecosystem from ad-hoc to professional-grade while maintaining all existing functionality.
