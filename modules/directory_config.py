"""DirectoryConfig module for ADT system."""

from typing import List, Dict, Any
from src.adt_core.module_sequencer import ADTModule


class DirectoryConfigModule(ADTModule):
    """Directory configuration processing module."""
    
    @property
    def name(self) -> str:
        return "DirectoryConfig"
    
    @property
    def version(self) -> str:
        return "1.0.3"
    
    @property
    def dependencies(self) -> List[str]:
        return ["ContentType", "EntityReference"]  # Depends on both
    
    @property
    def release_status(self) -> str:
        return "preview"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the module with configuration."""
        self.scan_depth = config.get("scan_depth", 5)
        self.exclude_patterns = config.get("exclude_patterns", ["*.tmp", "*.log"])
        print(f"Initialized DirectoryConfig v{self.version}")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module logic."""
        print(f"Executing DirectoryConfig")
        return {
            "module_name": self.name,
            "directories_scanned": 10,
            "scan_depth": self.scan_depth,
            "excluded_patterns": len(self.exclude_patterns),
            "success": True
        }
    
    def cleanup(self) -> None:
        """Clean up module resources."""
        print(f"Cleaning up DirectoryConfig")