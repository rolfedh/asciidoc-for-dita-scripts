"""ContentType module for ADT system."""

from typing import List, Dict, Any
from src.adt_core.module_sequencer import ADTModule


class ContentTypeModule(ADTModule):
    """Content type processing module."""
    
    @property
    def name(self) -> str:
        return "ContentType"
    
    @property
    def version(self) -> str:
        return "2.1.0"
    
    @property
    def dependencies(self) -> List[str]:
        return ["EntityReference"]  # Depends on EntityReference
    
    @property
    def release_status(self) -> str:
        return "GA"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the module with configuration."""
        self.cache_enabled = config.get("cache_enabled", True)
        self.supported_types = config.get("supported_types", ["text", "image", "video"])
        print(f"Initialized ContentType v{self.version}")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module logic."""
        print(f"Executing ContentType")
        return {
            "module_name": self.name,
            "content_types_processed": len(self.supported_types),
            "cache_enabled": self.cache_enabled,
            "success": True
        }
    
    def cleanup(self) -> None:
        """Clean up module resources."""
        print(f"Cleaning up ContentType")