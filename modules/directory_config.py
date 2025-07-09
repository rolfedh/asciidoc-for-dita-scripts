"""DirectoryConfig module for ADT system."""

import sys
from pathlib import Path
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
        return ["ContentType", "EntityReference"]
    
    @property
    def release_status(self) -> str:
        return "preview"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the module with configuration."""
        self.scan_depth = config.get("scan_depth", 5)
        self.exclude_patterns = config.get("exclude_patterns", ["*.tmp", "*.log"])
        self.verbose = config.get("verbose", False)
        
        # Set up access to legacy plugin functionality
        package_root = Path(__file__).parent.parent
        if str(package_root) not in sys.path:
            sys.path.insert(0, str(package_root))
        
        if self.verbose:
            print(f"Initialized DirectoryConfig v{self.version}")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module logic."""
        try:
            # Import and use the legacy plugin functionality
            from asciidoc_dita_toolkit.asciidoc_dita.plugins.DirectoryConfig import (
                load_directory_config, get_filtered_adoc_files, apply_directory_filters
            )
            from asciidoc_dita_toolkit.asciidoc_dita.file_utils import find_adoc_files
            
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
            
            # Track processing results
            configs_processed = 0
            files_processed = 0
            
            # Try to load directory configuration
            config = load_directory_config()
            if config:
                # Use configuration-aware file discovery
                adoc_files = get_filtered_adoc_files(args.directory, config, find_adoc_files)
                directories = apply_directory_filters(args.directory, config)
                
                for filepath in adoc_files:
                    if self.verbose:
                        print(f"Processing file: {filepath}")
                    
                    # Just count files for now since DirectoryConfig is more about file discovery
                    files_processed += 1
                
                configs_processed = len(directories)
            else:
                # Fall back to simple file discovery
                adoc_files = find_adoc_files(args.directory, args.recursive)
                files_processed = len(adoc_files)
                configs_processed = 1
            
            return {
                "module_name": self.name,
                "files_processed": files_processed,
                "configs_processed": configs_processed,
                "scan_depth": self.scan_depth,
                "success": True
            }
            
        except Exception as e:
            if self.verbose:
                print(f"Error in DirectoryConfig module: {e}")
            return {
                "module_name": self.name,
                "error": str(e),
                "success": False
            }
    
    def cleanup(self) -> None:
        """Clean up module resources."""
        if self.verbose:
            print(f"Cleaning up DirectoryConfig")