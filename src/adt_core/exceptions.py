"""
Custom exception classes for ADT module system.

Defines a hierarchy of exceptions for different error scenarios
that can occur during module discovery, configuration, and sequencing.
"""


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