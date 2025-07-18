"""ContentType module for ADT system."""

import sys
from pathlib import Path
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
        self.verbose = config.get("verbose", False)

        # Set up access to legacy plugin functionality
        package_root = Path(__file__).parent.parent
        if str(package_root) not in sys.path:
            sys.path.insert(0, str(package_root))

        if self.verbose:
            print(f"Initialized ContentType v{self.version}")

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module logic."""
        try:
            # Import and use the legacy plugin functionality
            from asciidoc_dita_toolkit.asciidoc_dita.plugins.ContentType import (
                process_content_type_file,
                create_processor,
            )
            from asciidoc_dita_toolkit.asciidoc_dita.workflow_utils import (
                process_adoc_files,
            )

            # Create args object similar to what legacy plugin expects
            class Args:
                def __init__(
                    self, file=None, recursive=False, directory=".", verbose=False
                ):
                    self.file = file
                    self.recursive = recursive
                    self.directory = directory
                    self.verbose = verbose

            args = Args(
                file=context.get("file"),
                recursive=context.get("recursive", False),
                directory=context.get("directory", "."),
                verbose=context.get("verbose", False),
            )

            # Track processing results
            content_types_processed = 0
            files_processed = 0

            # Create a processor instance for batch mode
            processor = create_processor(batch_mode=True, quiet_mode=not self.verbose)

            # Create a wrapper to track processing
            def content_type_wrapper(filepath):
                nonlocal files_processed, content_types_processed
                if self.verbose:
                    print(f"Processing file: {filepath}")

                # Use the legacy plugin function
                success = process_content_type_file(filepath, processor)
                files_processed += 1
                if success:
                    content_types_processed += 1

            # Process files using the workflow
            process_adoc_files(args, content_type_wrapper)

            return {
                "module_name": self.name,
                "files_processed": files_processed,
                "content_types_processed": content_types_processed,
                "cache_enabled": self.cache_enabled,
                "success": True,
            }

        except Exception as e:
            if self.verbose:
                print(f"Error in ContentType module: {e}")
            return {"module_name": self.name, "error": str(e), "success": False}

    def cleanup(self) -> None:
        """Clean up module resources."""
        if self.verbose:
            print(f"Cleaning up ContentType")
