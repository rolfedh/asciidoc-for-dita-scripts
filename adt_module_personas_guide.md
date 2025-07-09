# ADT Module Configuration System - Personas Guide

This guide explains how to work with the ADT module configuration system from three different perspectives: Plugin Developer, Developer, and End User.

---

## 🔧 Plugin Developer

### Concept Overview

As a **Plugin Developer**, you create reusable modules that extend ADT functionality. Your modules must follow specific interfaces and provide metadata that allows the system to discover, load, and manage them properly. You're responsible for defining dependencies, implementing proper initialization/cleanup, and providing clear documentation.

**Key Responsibilities:**
- Implement the `ADTModule` interface
- Define module metadata (name, actual version, dependencies)
- Handle initialization and cleanup properly
- Provide configuration schema
- Ensure proper error handling

### Procedures

#### 1. Setting Up Your Module Project

**File Structure:**
```
my_adt_module/
├── pyproject.toml              # Package configuration
├── src/
│   └── my_adt_module/
│       ├── __init__.py
│       ├── module.py           # Your module implementation
│       └── config_schema.json  # Configuration schema
├── tests/
│   └── test_module.py
└── README.md
```

#### 2. Implementing the Module Interface

**Step 1: Create your module class**
```python
# src/my_adt_module/module.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

class MyCustomModule(ADTModule):
    """Custom module for processing data."""
    
    @property
    def name(self) -> str:
        return "MyCustomModule"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def dependencies(self) -> List[str]:
        return ["EntityReference", "ContentType"]  # Required dependencies
    
    @property
    def release_status(self) -> str:
        return "GA"  # or "preview"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the module with configuration."""
        self.timeout = config.get("timeout_seconds", 30)
        self.cache_enabled = config.get("cache_enabled", True)
        self.logger = logging.getLogger(f"adt.{self.name}")
        
        # Validate configuration
        if self.timeout <= 0:
            raise ValueError("timeout_seconds must be positive")
        
        self.logger.info(f"Initialized {self.name} v{self.version}")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module logic."""
        self.logger.info(f"Executing {self.name}")
        
        # Your module logic here
        input_data = context.get("input_data", {})
        
        # Process data
        result = self._process_data(input_data)
        
        return {
            "processed_data": result,
            "module_name": self.name,
            "success": True
        }
    
    def cleanup(self) -> None:
        """Clean up module resources."""
        self.logger.info(f"Cleaning up {self.name}")
        # Close connections, clear caches, etc.
    
    def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Your custom processing logic."""
        # Implementation details
        return {"processed": True, "data": data}
```

#### 3. Configuring Package Distribution

**Step 2: Setup entry points in pyproject.toml**
```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-adt-module"
version = "1.0.0"
description = "Custom ADT module for processing data"
requires-python = ">=3.8"
dependencies = [
    "adt-core>=1.0.0",
    # Your dependencies
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"

[project.entry-points."adt.modules"]
MyCustomModule = "my_adt_module.module:MyCustomModule"
```

#### 4. Providing Configuration Schema

**Step 3: Define configuration schema**
```json
// src/my_adt_module/config_schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MyCustomModule Configuration",
  "type": "object",
  "properties": {
    "timeout_seconds": {
      "type": "integer",
      "minimum": 1,
      "maximum": 300,
      "default": 30,
      "description": "Request timeout in seconds"
    },
    "cache_enabled": {
      "type": "boolean",
      "default": true,
      "description": "Enable result caching"
    },
    "max_retries": {
      "type": "integer",
      "minimum": 0,
      "maximum": 10,
      "default": 3
    }
  },
  "required": ["timeout_seconds"]
}
```

### Examples

#### Example 1: Simple Processing Module
```python
class DataValidatorModule(ADTModule):
    @property
    def name(self) -> str:
        return "DataValidator"
    
    @property
    def version(self) -> str:
        return "2.1.0"
    
    @property
    def dependencies(self) -> List[str]:
        return []  # No dependencies
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.strict_mode = config.get("strict_mode", False)
        self.validation_rules = config.get("rules", [])
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        data = context.get("input_data", {})
        
        validation_result = self._validate_data(data)
        
        return {
            "validation_passed": validation_result.is_valid,
            "errors": validation_result.errors,
            "validated_data": data if validation_result.is_valid else None
        }
```

#### Example 2: Module with Dependencies
```python
class ReportGeneratorModule(ADTModule):
    @property
    def name(self) -> str:
        return "ReportGenerator"
    
    @property
    def dependencies(self) -> List[str]:
        return ["DataValidator", "ContentType"]  # Depends on other modules
    
    def initialize(self, config: Dict[str, Any]) -> None:
        # This module will only initialize after its dependencies
        self.output_format = config.get("format", "pdf")
        self.template_path = config.get("template_path", "templates/default.html")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Can access results from dependency modules
        validated_data = context.get("DataValidator", {}).get("validated_data")
        content_type = context.get("ContentType", {}).get("content_type")
        
        if not validated_data:
            return {"error": "No validated data available"}
        
        report = self._generate_report(validated_data, content_type)
        return {"report": report, "format": self.output_format}
```

---

## 📋 Developer

### Concept Overview

As a **Developer**, you configure the ADT system by defining which modules are available, their execution order, requirements, and default settings. You manage the `.adt-modules.json` configuration file that serves as the blueprint for your ADT application.

**Key Responsibilities:**
- Define module execution sequence
- Set module requirements (required vs optional)
- Configure module dependencies and version constraints
- Set up global configuration parameters
- Ensure proper module compatibility

**Note**: The ADT system uses a `ModuleSequencer` component that reads your configuration and handles the complex task of module discovery, dependency resolution, and proper initialization ordering. You specify version constraints (e.g., ">=1.2.0") while plugin developers set the actual version numbers (e.g., "1.2.1") in their modules.

### Procedures

#### 1. Creating Developer Configuration

**Step 1: Initialize configuration file**
```bash
# Create the developer configuration file
touch .adt-modules.json
```

**Step 2: Define basic structure**
```json
{
  "version": "1.0",
  "modules": [],
  "global_config": {}
}
```

#### 2. Adding Modules to Configuration

**Step 3: Add modules with full specifications**
```json
{
  "version": "1.0",
  "modules": [
    {
      "name": "EntityReference",                    // REFERENCE: Must match module's actual name
      "required": true,                            // CONSTRAINT: Developer decides if required
      "version": ">=1.2.0",                       // CONSTRAINT: Version requirement (actual version comes from module)
      "dependencies": ["Authentication"],          // CONSTRAINT: Additional dependencies (module's dependencies auto-detected)
      "init_order": 1,                            // CONSTRAINT: Developer-controlled initialization order
      "config": {                                 // CONFIGURATION: Values passed to module.initialize()
        "timeout_seconds": 30,
        "cache_size": 1000
      }
    },
    {
      "name": "ContentType",                       // REFERENCE: Must match module's actual name
      "required": false,                           // CONSTRAINT: Developer decides if required
      "version": ">=2.0.0",                       // CONSTRAINT: Version requirement
      "dependencies": ["EntityReference"],         // CONSTRAINT: Additional dependencies
      "init_order": 2,                            // CONSTRAINT: Developer-controlled initialization order
      "config": {                                 // CONFIGURATION: Values passed to module.initialize()
        "cache_enabled": true,
        "supported_types": ["text", "image", "video"]
      }
    },
    {
      "name": "DirectoryConfig",                   // REFERENCE: Must match module's actual name
      "required": false,                           // CONSTRAINT: Developer decides if required
      "version": "~1.0.0",                        // CONSTRAINT: Version requirement
      "dependencies": ["ContentType", "EntityReference"], // CONSTRAINT: Additional dependencies
      "init_order": 3,                            // CONSTRAINT: Developer-controlled initialization order
      "config": {                                 // CONFIGURATION: Values passed to module.initialize()
        "scan_depth": 5,
        "exclude_patterns": ["*.tmp", "*.log"]
      }
    }
  ],
  "global_config": {                              // CONFIGURATION: Global settings for all modules
    "max_retries": 3,
    "log_level": "INFO",
    "timeout_seconds": 60
  }
}
```

#### 3. Managing Module Dependencies

**Step 4: Define dependency relationships**
```json
{
  "modules": [
    {
      "name": "BaseModule",                        // REFERENCE: Must match module's actual name
      "required": true,                            // CONSTRAINT: Developer decides if required
      "dependencies": [],                          // CONSTRAINT: Additional dependencies (module's dependencies auto-detected)
      "init_order": 1                             // CONSTRAINT: Developer-controlled initialization order
    },
    {
      "name": "ProcessingModule",                  // REFERENCE: Must match module's actual name
      "required": false,                           // CONSTRAINT: Developer decides if required
      "dependencies": ["BaseModule"],              // CONSTRAINT: Additional dependencies
      "init_order": 2                             // CONSTRAINT: Developer-controlled initialization order
    },
    {
      "name": "OutputModule",                      // REFERENCE: Must match module's actual name
      "required": false,                           // CONSTRAINT: Developer decides if required
      "dependencies": ["ProcessingModule", "BaseModule"], // CONSTRAINT: Additional dependencies
      "init_order": 3                             // CONSTRAINT: Developer-controlled initialization order
    }
  ]
}
```

#### 4. Version Management

**Step 5: Specify version constraints**
```json
{
  "modules": [
    {
      "name": "StableModule",                      // REFERENCE: Must match module's actual name
      "version": ">=2.0.0",                       // CONSTRAINT: At least version 2.0.0 (actual version comes from module)
      "required": true                             // CONSTRAINT: Developer decides if required
    },
    {
      "name": "BetaModule",                        // REFERENCE: Must match module's actual name
      "version": "~1.5.0",                        // CONSTRAINT: Compatible with 1.5.x (actual version comes from module)
      "required": false                            // CONSTRAINT: Developer decides if required
    },
    {
      "name": "ExactModule",                       // REFERENCE: Must match module's actual name
      "version": "1.0.0",                         // CONSTRAINT: Exact version required (actual version comes from module)
      "required": true                             // CONSTRAINT: Developer decides if required
    }
  ]
}
```

### Examples

#### Example 1: Basic Web Application Configuration
```json
{
  "version": "1.0",
  "modules": [
    {
      "name": "Authentication",                     // REFERENCE: Must match module's actual name
      "required": true,                            // CONSTRAINT: Developer decides if required
      "version": ">=3.0.0",                       // CONSTRAINT: Version requirement (actual version comes from module)
      "dependencies": [],                          // CONSTRAINT: Additional dependencies (module's dependencies auto-detected)
      "init_order": 1,                            // CONSTRAINT: Developer-controlled initialization order
      "config": {                                 // CONFIGURATION: Values passed to module.initialize()
        "session_timeout": 3600,
        "max_login_attempts": 5
      }
    },
    {
      "name": "Database",                          // REFERENCE: Must match module's actual name
      "required": true,                            // CONSTRAINT: Developer decides if required
      "version": ">=2.1.0",                       // CONSTRAINT: Version requirement
      "dependencies": [],                          // CONSTRAINT: Additional dependencies
      "init_order": 2,                            // CONSTRAINT: Developer-controlled initialization order
      "config": {                                 // CONFIGURATION: Values passed to module.initialize()
        "pool_size": 10,
        "connection_timeout": 30
      }
    },
    {
      "name": "UserManagement",                    // REFERENCE: Must match module's actual name
      "required": true,                            // CONSTRAINT: Developer decides if required
      "version": ">=1.0.0",                       // CONSTRAINT: Version requirement
      "dependencies": ["Authentication", "Database"], // CONSTRAINT: Additional dependencies
      "init_order": 3                             // CONSTRAINT: Developer-controlled initialization order
    },
    {
      "name": "Analytics",                         // REFERENCE: Must match module's actual name
      "required": false,                           // CONSTRAINT: Developer decides if required
      "version": ">=1.2.0",                       // CONSTRAINT: Version requirement
      "dependencies": ["UserManagement"],         // CONSTRAINT: Additional dependencies
      "init_order": 4,                            // CONSTRAINT: Developer-controlled initialization order
      "config": {                                 // CONFIGURATION: Values passed to module.initialize()
        "tracking_enabled": true,
        "retention_days": 90
      }
    }
  ],
  "global_config": {                              // CONFIGURATION: Global settings for all modules
    "max_retries": 3,
    "log_level": "INFO",
    "debug_mode": false
  }
}
```

#### Example 2: Data Processing Pipeline
```json
{
  "version": "1.0",
  "modules": [
    {
      "name": "DataIngestion",                     // REFERENCE: Must match module's actual name
      "required": true,                            // CONSTRAINT: Developer decides if required
      "version": ">=1.0.0",                       // CONSTRAINT: Version requirement (actual version comes from module)
      "dependencies": [],                          // CONSTRAINT: Additional dependencies (module's dependencies auto-detected)
      "init_order": 1,                            // CONSTRAINT: Developer-controlled initialization order
      "config": {                                 // CONFIGURATION: Values passed to module.initialize()
        "batch_size": 1000,
        "input_format": "json"
      }
    },
    {
      "name": "DataValidation",                    // REFERENCE: Must match module's actual name
      "required": true,                            // CONSTRAINT: Developer decides if required
      "version": ">=2.0.0",                       // CONSTRAINT: Version requirement
      "dependencies": ["DataIngestion"],          // CONSTRAINT: Additional dependencies
      "init_order": 2,                            // CONSTRAINT: Developer-controlled initialization order
      "config": {                                 // CONFIGURATION: Values passed to module.initialize()
        "strict_mode": true,
        "validation_rules": "rules/data_validation.json"
      }
    },
    {
      "name": "DataTransformation",                // REFERENCE: Must match module's actual name
      "required": false,                           // CONSTRAINT: Developer decides if required
      "version": ">=1.5.0",                       // CONSTRAINT: Version requirement
      "dependencies": ["DataValidation"],         // CONSTRAINT: Additional dependencies
      "init_order": 3                             // CONSTRAINT: Developer-controlled initialization order
    },
    {
      "name": "DataExport",                        // REFERENCE: Must match module's actual name
      "required": true,                            // CONSTRAINT: Developer decides if required
      "version": ">=1.0.0",                       // CONSTRAINT: Version requirement
      "dependencies": ["DataTransformation"],     // CONSTRAINT: Additional dependencies
      "init_order": 4,                            // CONSTRAINT: Developer-controlled initialization order
      "config": {                                 // CONFIGURATION: Values passed to module.initialize()
        "output_format": "parquet",
        "compression": "snappy"
      }
    }
  ],
  "global_config": {                              // CONFIGURATION: Global settings for all modules
    "max_retries": 5,
    "log_level": "DEBUG",
    "parallel_processing": true
  }
}
```

---

## 👤 End User

### Concept Overview

As an **End User**, you control which optional modules are enabled or disabled in your ADT installation. You can customize module behavior through the `adt-user-config.json` file and use CLI commands for quick adjustments. You cannot disable required modules, but you have full control over optional ones.

**Key Responsibilities:**
- Enable/disable optional modules
- Override module-specific settings
- Use CLI commands for quick module management
- Monitor module status and performance

### Procedures

#### 1. Viewing Current Module Status

**Step 1: Check module status**
```bash
# View all modules and their current status
adt modules status

# View specific module details
adt modules status --module ContentType

# List all available modules
adt modules list
```

**Expected Output:**
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
```

#### 2. Creating User Configuration

**Step 2: Initialize user configuration**
```bash
# Create user config file (if it doesn't exist)
touch adt-user-config.json
```

**Step 3: Configure enabled/disabled modules**
```json
{
  "version": "1.0",
  "enabledModules": [
    "ContentType",
    "Analytics"
  ],
  "disabledModules": [
    "DirectoryConfig",
    "AdvancedReporting"
  ],
  "moduleOverrides": {
    "ContentType": {
      "cache_enabled": false,
      "supported_types": ["text", "image"]
    },
    "Analytics": {
      "tracking_enabled": true,
      "retention_days": 30
    }
  }
}
```

#### 3. Managing Modules via CLI

**Step 4: Enable/disable modules**
```bash
# Enable a specific module
adt modules enable DirectoryConfig

# Disable a specific module
adt modules disable Analytics

# Enable multiple modules
adt modules enable ContentType DirectoryConfig Analytics

# Temporary override for testing
adt run --enable-module=DirectoryConfig --disable-module=Analytics

# Validate configuration
adt modules validate
```

#### 4. Monitoring Module Performance

**Step 5: Check module performance**
```bash
# Show module execution times
adt modules performance

# Show module dependencies
adt modules deps DirectoryConfig

# Export current configuration
adt modules config --format json > my-config-backup.json
```

### Examples

#### Example 1: Minimal Configuration (Most Modules Disabled)
```json
{
  "version": "1.0",
  "enabledModules": [
    "EntityReference"
  ],
  "disabledModules": [
    "ContentType",
    "DirectoryConfig",
    "Analytics",
    "AdvancedReporting",
    "EmailNotifications"
  ],
  "moduleOverrides": {
    "EntityReference": {
      "cache_size": 500,
      "timeout_seconds": 15
    }
  }
}
```

#### Example 2: Power User Configuration (Custom Overrides)
```json
{
  "version": "1.0",
  "enabledModules": [
    "ContentType",
    "DirectoryConfig",
    "Analytics",
    "AdvancedReporting",
    "EmailNotifications",
    "CustomDashboard"
  ],
  "disabledModules": [
    "LegacySupport",
    "DebugModule"
  ],
  "moduleOverrides": {
    "Analytics": {
      "tracking_enabled": true,
      "retention_days": 365,
      "detailed_logging": true
    },
    "DirectoryConfig": {
      "scan_depth": 10,
      "exclude_patterns": ["*.tmp", "*.log", "*.cache", "node_modules/*"]
    },
    "EmailNotifications": {
      "smtp_server": "smtp.company.com",
      "send_daily_reports": true,
      "alert_on_errors": true
    }
  }
}
```

#### Example 3: Development Environment Configuration
```json
{
  "version": "1.0",
  "enabledModules": [
    "ContentType",
    "DirectoryConfig",
    "DebugModule",
    "TestingUtilities"
  ],
  "disabledModules": [
    "Analytics",
    "EmailNotifications",
    "ProductionOptimizations"
  ],
  "moduleOverrides": {
    "DebugModule": {
      "verbose_logging": true,
      "save_debug_files": true,
      "debug_port": 9000
    },
    "TestingUtilities": {
      "mock_external_services": true,
      "test_data_path": "test-data/",
      "auto_cleanup": false
    }
  }
}
```

#### Example 4: CLI Usage Scenarios

**Scenario 1: Testing a new module**
```bash
# Test run with a new module enabled temporarily
adt run --enable-module=NewFeatureModule --log-level=DEBUG

# Check if the module works correctly
adt modules status NewFeatureModule

# If satisfied, permanently enable it
adt modules enable NewFeatureModule
```

**Scenario 2: Troubleshooting performance issues**
```bash
# Disable all non-essential modules
adt modules disable Analytics DirectoryConfig AdvancedReporting

# Run with minimal configuration
adt run --minimal

# Check performance improvement
adt modules performance

# Re-enable modules one by one to identify the issue
adt modules enable Analytics
adt run --test
```

**Scenario 3: Backing up and restoring configuration**
```bash
# Backup current configuration
adt modules config --format json > backup-$(date +%Y%m%d).json

# Restore from backup
cp backup-20231201.json adt-user-config.json
adt modules validate
```

---

## 🔄 Cross-Persona Workflow

### Typical Development Cycle

1. **Plugin Developer** creates a new module and publishes it
2. **Developer** adds the module to `.adt-modules.json` with appropriate configuration
3. **End User** can then enable/disable the module and customize its behavior
4. **End User** provides feedback, leading to improvements by the **Plugin Developer**

### Communication Points

- **Plugin Developer** → **Developer**: Module documentation, configuration schema, dependency requirements
- **Developer** → **End User**: Available modules, default configurations, usage guidelines  
- **End User** → **Plugin Developer**: Feature requests, bug reports, performance feedback

This guide ensures each persona understands their role and can work effectively within the ADT module configuration system.