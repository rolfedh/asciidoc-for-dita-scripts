"""
ModuleSequencer implementation for ADT module system.

Main class responsible for sequencing, configuring, and managing ADT modules.
Handles module discovery, dependency resolution, configuration management,
and proper initialization sequencing.
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Set, Tuple, Optional, Any
from importlib.metadata import entry_points

from .exceptions import (
    ADTModuleError, ConfigurationError, ModuleNotFoundError,
    CircularDependencyError, MissingDependencyError, VersionConflictError
)

# Known legacy plugins that should not show warnings during transition
LEGACY_PLUGINS = set()  # All plugins have been migrated to ADTModule


class ModuleState(Enum):
    """Possible states for a module."""
    ENABLED = "enabled"
    DISABLED = "disabled" 
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class ModuleResolution:
    """Result of module resolution process."""
    name: str
    state: ModuleState
    version: str
    dependencies: List[str]
    init_order: int
    config: Dict[str, Any]
    error_message: Optional[str] = None


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
        self.suppress_legacy_warnings = True  # Default to suppress warnings
    
    def set_suppress_legacy_warnings(self, suppress: bool = True) -> None:
        """
        Control whether to suppress warnings for legacy plugins.
        
        Args:
            suppress: If True, suppress warnings for known legacy plugins
        """
        self.suppress_legacy_warnings = suppress
    
    def load_configurations(self, dev_config_path: str, user_config_path: str = None) -> None:
        """Load developer and user configurations."""
        try:
            # Load developer configuration (required)
            if not os.path.exists(dev_config_path):
                raise ConfigurationError(f"Developer config file not found: {dev_config_path}")
            
            with open(dev_config_path, 'r') as f:
                self.dev_config = json.load(f)
            
            self.logger.info(f"Loaded developer config from {dev_config_path}")
            
            # Load user configuration (optional)
            if user_config_path and os.path.exists(user_config_path):
                with open(user_config_path, 'r') as f:
                    self.user_config = json.load(f)
                self.logger.info(f"Loaded user config from {user_config_path}")
            else:
                self.user_config = {}
                self.logger.info("No user config found, using defaults")
                
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration: {e}")
    
    def discover_modules(self) -> None:
        """Discover available modules via entry points."""
        self.available_modules = {}
        
        try:
            # Discover modules via entry points
            eps = entry_points()
            adt_eps = eps.select(group="adt.modules") if hasattr(eps, 'select') else eps.get("adt.modules", [])
            
            for entry_point in adt_eps:
                try:
                    module_class = entry_point.load()
                    module_instance = module_class()
                    
                    if not isinstance(module_instance, ADTModule):
                        # Check if this is a known legacy plugin
                        if self.suppress_legacy_warnings and entry_point.name in LEGACY_PLUGINS:
                            self.logger.debug(f"Legacy plugin {entry_point.name} does not inherit from ADTModule (transition mode)")
                        else:
                            self.logger.warning(f"Module {entry_point.name} does not inherit from ADTModule")
                        continue
                    
                    self.available_modules[module_instance.name] = module_instance
                    self.logger.info(f"Discovered module: {module_instance.name} v{module_instance.version}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to load module {entry_point.name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error during module discovery: {e}")
        
        self.logger.info(f"Discovered {len(self.available_modules)} modules")
    
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
        """Build directed dependency graph (adjacency list)."""
        # Initialize graph with all modules
        graph = {}
        all_modules = set()
        
        for module_config in self.dev_config.get("modules", []):
            module_name = module_config["name"]
            all_modules.add(module_name)
            
            # Combine module's own dependencies with developer-specified additional dependencies
            module_deps = set()
            if module_name in self.available_modules:
                module_deps.update(self.available_modules[module_name].dependencies)
            
            additional_deps = set(module_config.get("dependencies", []))
            all_dependencies = module_deps.union(additional_deps)
            
            # Validate dependencies exist
            for dep in all_dependencies:
                if dep not in self.available_modules:
                    raise MissingDependencyError(f"Module '{module_name}' depends on missing module '{dep}'")
        
        # Initialize all nodes in graph
        for module in all_modules:
            graph[module] = set()
        
        # Build adjacency list: if A depends on B, then B -> A
        for module_config in self.dev_config.get("modules", []):
            module_name = module_config["name"]
            
            module_deps = set()
            if module_name in self.available_modules:
                module_deps.update(self.available_modules[module_name].dependencies)
            
            additional_deps = set(module_config.get("dependencies", []))
            all_dependencies = module_deps.union(additional_deps)
            
            # For each dependency, add an edge from dependency to this module
            for dep in all_dependencies:
                graph[dep].add(module_name)
        
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
            
            # Get module-specific config from developer config
            module_config = {}
            for config in self.dev_config.get("modules", []):
                if config["name"] == module_name:
                    module_config = config.get("config", {})
                    break
            
            # Apply user overrides
            user_overrides = self.user_config.get("moduleOverrides", {}).get(module_name, {})
            module_config.update(user_overrides)
            
            # Apply global config
            global_config = self.dev_config.get("global_config", {})
            final_config = {**global_config, **module_config}
            
            resolutions.append(ModuleResolution(
                name=module_name,
                state=ModuleState.ENABLED,
                version=module.version,
                dependencies=module.dependencies,
                init_order=i,
                config=final_config
            ))
        
        return resolutions
    
    def get_module_status(self) -> Dict[str, Any]:
        """Get current status of all modules."""
        resolutions, errors = self.sequence_modules()
        
        status = {
            "modules": [],
            "total_enabled": 0,
            "total_disabled": 0,
            "total_failed": 0,
            "errors": errors
        }
        
        # Get all configured modules from dev config
        configured_modules = set()
        for module_config in self.dev_config.get("modules", []):
            configured_modules.add(module_config["name"])
        
        # Add enabled/failed modules from resolutions
        enabled_modules = set()
        for resolution in resolutions:
            enabled_modules.add(resolution.name)
            status["modules"].append({
                "name": resolution.name,
                "state": resolution.state.value,
                "version": resolution.version,
                "dependencies": resolution.dependencies,
                "init_order": resolution.init_order,
                "error_message": resolution.error_message
            })
            
            if resolution.state == ModuleState.ENABLED:
                status["total_enabled"] += 1
            elif resolution.state == ModuleState.DISABLED:
                status["total_disabled"] += 1
            elif resolution.state == ModuleState.FAILED:
                status["total_failed"] += 1
        
        # Add disabled modules (configured but not in resolutions)
        for module_name in configured_modules:
            if module_name not in enabled_modules and module_name in self.available_modules:
                module = self.available_modules[module_name]
                status["modules"].append({
                    "name": module_name,
                    "state": "disabled",
                    "version": module.version,
                    "dependencies": module.dependencies,
                    "init_order": -1,
                    "error_message": None
                })
                status["total_disabled"] += 1
        
        # Add unconfigured available modules
        for name, module in self.available_modules.items():
            if name not in configured_modules:
                status["modules"].append({
                    "name": name,
                    "state": "unconfigured",
                    "version": module.version,
                    "dependencies": module.dependencies,
                    "init_order": -1,
                    "error_message": None
                })
        
        return status
    
    def validate_configuration(self) -> List[str]:
        """Validate current configuration and return any errors."""
        errors = []
        
        try:
            # Validate developer config structure
            if "version" not in self.dev_config:
                errors.append("Developer config missing 'version' field")
            
            if "modules" not in self.dev_config:
                errors.append("Developer config missing 'modules' field")
            
            # Validate each module config
            for i, module_config in enumerate(self.dev_config.get("modules", [])):
                if "name" not in module_config:
                    errors.append(f"Module config {i} missing 'name' field")
                
                if "required" not in module_config:
                    errors.append(f"Module config {i} missing 'required' field")
            
            # Try to sequence modules to catch dependency issues
            _, sequence_errors = self.sequence_modules()
            errors.extend(sequence_errors)
            
        except Exception as e:
            errors.append(f"Configuration validation error: {e}")
        
        return errors


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