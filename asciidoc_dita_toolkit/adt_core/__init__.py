"""
ADT Core Module

Provides module sequencing, dependency resolution, and configuration management
for ADT-based Python projects.
"""

from .module_sequencer import ModuleSequencer, ModuleState, ModuleResolution, ADTModule
from .exceptions import (
    ADTModuleError,
    ConfigurationError,
    ModuleNotFoundError,
    ModuleInitializationError,
    DependencyError,
    CircularDependencyError,
    MissingDependencyError,
    VersionConflictError,
)

__version__ = "2.0.8"

__all__ = [
    "ModuleSequencer",
    "ModuleState",
    "ModuleResolution",
    "ADTModule",
    "ADTModuleError",
    "ConfigurationError",
    "ModuleNotFoundError",
    "ModuleInitializationError",
    "DependencyError",
    "CircularDependencyError",
    "MissingDependencyError",
    "VersionConflictError",
]
