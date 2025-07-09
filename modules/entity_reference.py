"""EntityReference module for ADT system."""

import sys
from pathlib import Path
from typing import List, Dict, Any
from src.adt_core.module_sequencer import ADTModule


class EntityReferenceModule(ADTModule):
    """Entity reference processing module."""
    
    @property
    def name(self) -> str:
        return "EntityReference"
    
    @property
    def version(self) -> str:
        return "1.2.1"
    
    @property
    def dependencies(self) -> List[str]:
        return []  # No dependencies
    
    @property
    def release_status(self) -> str:
        return "GA"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the module with configuration."""
        self.timeout_seconds = config.get("timeout_seconds", 30)
        self.cache_size = config.get("cache_size", 1000)
        self.verbose = config.get("verbose", False)
        
        # Set up access to legacy plugin functionality
        package_root = Path(__file__).parent.parent
        if str(package_root) not in sys.path:
            sys.path.insert(0, str(package_root))
        
        if self.verbose:
            print(f"Initialized EntityReference v{self.version}")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module logic."""
        try:
            # Import and use the legacy plugin functionality
            from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import (
                process_file, ENTITY_TO_ASCIIDOC
            )
            from asciidoc_dita_toolkit.asciidoc_dita.file_utils import (
                get_adoc_files_to_process
            )
            
            # Create args object similar to what legacy plugin expects
            class Args:
                def __init__(self, file=None, recursive=False, directory=".", verbose=False):
                    self.file = file
                    self.recursive = recursive
                    self.directory = directory
                    self.verbose = verbose
            
            args = Args(
                file=context.get("file"),
                recursive=context.get("recursive", False),
                directory=context.get("directory", "."),
                verbose=context.get("verbose", False)
            )
            
            # Get files to process
            files_to_process = get_adoc_files_to_process(args)
            
            entities_processed = 0
            files_processed = 0
            
            # Process each file
            for file_path in files_to_process:
                if self.verbose:
                    print(f"Processing file: {file_path}")
                
                process_file(file_path)
                files_processed += 1
                
                # Count entities that would be processed (approximate)
                entities_processed += len(ENTITY_TO_ASCIIDOC)
            
            return {
                "module_name": self.name,
                "files_processed": files_processed,
                "entities_processed": entities_processed,
                "success": True
            }
            
        except Exception as e:
            if self.verbose:
                print(f"Error in EntityReference module: {e}")
            return {
                "module_name": self.name,
                "error": str(e),
                "success": False
            }
    
    def cleanup(self) -> None:
        """Clean up module resources."""
        if self.verbose:
            print(f"Cleaning up EntityReference")