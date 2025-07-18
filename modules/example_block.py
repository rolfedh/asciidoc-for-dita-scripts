"""ExampleBlock module for ADT system."""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Try to import ADTModule for the new pattern
try:
    # Add the path to find the ADTModule
    package_root = Path(__file__).parent.parent
    if str(package_root / "src") not in sys.path:
        sys.path.insert(0, str(package_root / "src"))
    
    from adt_core.module_sequencer import ADTModule
    ADT_MODULE_AVAILABLE = True
except ImportError:
    ADT_MODULE_AVAILABLE = False
    # Create a dummy ADTModule for backward compatibility
    class ADTModule:
        pass


class ExampleBlockModule(ADTModule):
    """Example block processing module."""
    
    @property
    def name(self) -> str:
        return "ExampleBlock"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Flag or fix example blocks in problematic locations."
    
    @property
    def dependencies(self) -> List[str]:
        return []  # No dependencies
    
    @property
    def release_status(self) -> str:
        return "GA"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the module with configuration."""
        self.batch_mode = config.get("batch_mode", False)
        self.quiet_mode = config.get("quiet_mode", False)
        self.verbose = config.get("verbose", False)
        
        # Set up access to legacy plugin functionality
        package_root = Path(__file__).parent.parent
        if str(package_root) not in sys.path:
            sys.path.insert(0, str(package_root))
        
        if self.verbose:
            print(f"Initialized ExampleBlock v{self.version}")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module logic."""
        try:
            # Import and use the legacy plugin functionality
            from asciidoc_dita_toolkit.asciidoc_dita.plugins.ExampleBlock import (
                process_example_block_file, create_processor
            )
            from asciidoc_dita_toolkit.asciidoc_dita.workflow_utils import process_adoc_files
            
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
            example_blocks_processed = 0
            files_processed = 0
            
            # Create a processor instance for batch mode
            processor = create_processor(batch_mode=self.batch_mode, quiet_mode=self.quiet_mode)
            
            # Create a wrapper to track processing
            def example_block_wrapper(filepath):
                nonlocal files_processed, example_blocks_processed
                # Always show the filename being processed
                print(f"Processing file: {filepath}")
                
                # Use the legacy plugin function
                success = process_example_block_file(filepath, processor)
                files_processed += 1
                if success:
                    example_blocks_processed += 1
            
            # Process files using the workflow
            process_adoc_files(args, example_block_wrapper)
            
            return {
                "module_name": self.name,
                "files_processed": files_processed,
                "example_blocks_processed": example_blocks_processed,
                "batch_mode": self.batch_mode,
                "success": True
            }
            
        except Exception as e:
            if self.verbose:
                print(f"Error in ExampleBlock module: {e}")
            return {
                "module_name": self.name,
                "error": str(e),
                "success": False
            }
    
    def cleanup(self) -> None:
        """Clean up module resources."""
        if self.verbose:
            print(f"Cleaning up ExampleBlock")
