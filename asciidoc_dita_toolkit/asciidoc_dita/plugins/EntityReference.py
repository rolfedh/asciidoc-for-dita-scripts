"""
Plugin for the AsciiDoc DITA toolkit: EntityReference

This plugin replaces unsupported HTML character entity references in .adoc files with AsciiDoc attribute references.

See: 
- https://github.com/jhradilek/asciidoctor-dita-vale/blob/main/styles/AsciiDocDITA/EntityReference.yml
- https://github.com/jhradilek/asciidoctor-dita-vale/tree/main/fixtures/EntityReference
"""

__description__ = "Replace unsupported HTML character entity references in .adoc files with AsciiDoc attribute references."

import re
import sys
from pathlib import Path
from typing import List, Dict, Any

from ..file_utils import (common_arg_parser, process_adoc_files,
                          read_text_preserve_endings,
                          write_text_preserve_endings)

# Try to import ADTModule for the new pattern
try:
    # Add the path to find the ADTModule
    package_root = Path(__file__).parent.parent.parent.parent
    if str(package_root / "src") not in sys.path:
        sys.path.insert(0, str(package_root / "src"))
    
    from adt_core.module_sequencer import ADTModule
    ADT_MODULE_AVAILABLE = True
except ImportError:
    ADT_MODULE_AVAILABLE = False
    # Create a dummy ADTModule for backward compatibility
    class ADTModule:
        pass

# Supported XML entities in DITA 1.3 (these should not be replaced)
SUPPORTED_ENTITIES = {"amp", "lt", "gt", "apos", "quot"}

# Mapping of common HTML entities to AsciiDoc attribute references
ENTITY_TO_ASCIIDOC = {
    # XML entities are supported in DITA and left unchanged
    # "amp": "{amp}",        # & (ampersand)
    # "lt": "{lt}",          # < (less-than)
    # "gt": "{gt}",          # > (greater-than)
    # "apos": "{apos}",      # ' (apostrophe)
    # "quot": "{quot}",      # " (quotation mark)
    "brvbar": "{brvbar}",  # ¦ (broken bar)
    "bull": "{bull}",  # • (bullet)
    "copy": "{copy}",  # © (copyright sign)
    "deg": "{deg}",  # ° (degree sign)
    "Dagger": "{Dagger}",  # ‡ (double dagger)
    "dagger": "{dagger}",  # † (dagger)
    "hellip": "{hellip}",  # … (ellipsis)
    "laquo": "{laquo}",  # « (left-pointing double angle quotation mark)
    "ldquo": "{ldquo}",  # " (left double quotation mark)
    "lsquo": "{lsquo}",  # ' (left single quotation mark)
    "lsaquo": "{lsaquo}",  # ‹ (single left-pointing angle quotation mark)
    "mdash": "{mdash}",  # — (em dash)
    "middot": "{middot}",  # · (middle dot)
    "ndash": "{ndash}",  # – (en dash)
    "num": "{num}",  # # (number sign)
    "para": "{para}",  # ¶ (pilcrow/paragraph sign)
    "plus": "{plus}",  # + (plus sign)
    "pound": "{pound}",  # £ (pound sign)
    "quot": "{quot}",  # " (quotation mark)
    "raquo": "{raquo}",  # » (right-pointing double angle quotation mark)
    "rdquo": "{rdquo}",  # " (right double quotation mark)
    "reg": "{reg}",  # ® (registered sign)
    "rsquo": "{rsquo}",  # ' (right single quotation mark)
    "rsaquo": "{rsaquo}",  # › (single right-pointing angle quotation mark)
    "sect": "{sect}",  # § (section sign)
    "sbquo": "{sbquo}",  # ‚ (single low-9 quotation mark)
    "bdquo": "{bdquo}",  # „ (double low-9 quotation mark)
    "trade": "{trade}",  # ™ (trademark sign)
}

ENTITY_PATTERN = re.compile(r"&([a-zA-Z0-9]+);")


class EntityReferenceModule(ADTModule):
    """
    ADTModule implementation for EntityReference plugin.
    
    This module replaces unsupported HTML character entity references 
    in .adoc files with AsciiDoc attribute references.
    """
    
    @property
    def name(self) -> str:
        """Module name identifier."""
        return "EntityReference"
    
    @property
    def version(self) -> str:
        """Module version using semantic versioning."""
        return "1.2.1"
    
    @property
    def dependencies(self) -> List[str]:
        """List of required module names."""
        return []  # No dependencies
    
    @property
    def release_status(self) -> str:
        """Release status: 'GA' for stable, 'preview' for beta."""
        return "GA"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the module with configuration.
        
        Args:
            config: Configuration dictionary containing module settings
        """
        # Configuration options
        self.timeout_seconds = config.get("timeout_seconds", 30)
        self.cache_size = config.get("cache_size", 1000)
        self.verbose = config.get("verbose", False)
        self.skip_comments = config.get("skip_comments", True)
        
        # Initialize statistics
        self.files_processed = 0
        self.entities_replaced = 0
        self.warnings_generated = 0
        
        if self.verbose:
            print(f"Initialized EntityReference v{self.version}")
            print(f"  Timeout: {self.timeout_seconds}s")
            print(f"  Cache size: {self.cache_size}")
            print(f"  Skip comments: {self.skip_comments}")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the entity reference replacement.
        
        Args:
            context: Execution context containing parameters and results from dependencies
        
        Returns:
            Dictionary with execution results
        """
        try:
            # Extract parameters from context
            file_path = context.get("file")
            recursive = context.get("recursive", False)
            directory = context.get("directory", ".")
            
            # Create args object for compatibility with legacy code
            class Args:
                def __init__(self, file=None, recursive=False, directory="."):
                    self.file = file
                    self.recursive = recursive
                    self.directory = directory
            
            args = Args(file_path, recursive, directory)
            
            # Reset statistics
            self.files_processed = 0
            self.entities_replaced = 0
            self.warnings_generated = 0
            
            # Process files using the existing logic
            process_adoc_files(args, self._process_file_wrapper)
            
            return {
                "module_name": self.name,
                "version": self.version,
                "files_processed": self.files_processed,
                "entities_replaced": self.entities_replaced,
                "warnings_generated": self.warnings_generated,
                "success": True,
                "supported_entities": list(SUPPORTED_ENTITIES),
                "entity_mappings": len(ENTITY_TO_ASCIIDOC)
            }
            
        except Exception as e:
            error_msg = f"Error in EntityReference module: {e}"
            if self.verbose:
                print(error_msg)
            return {
                "module_name": self.name,
                "version": self.version,
                "error": str(e),
                "success": False,
                "files_processed": self.files_processed,
                "entities_replaced": self.entities_replaced
            }
    
    def _process_file_wrapper(self, filepath: str) -> None:
        """
        Wrapper around the process_file function to track statistics.
        
        Args:
            filepath: Path to the file to process
        """
        if self.verbose:
            print(f"Processing file: {filepath}")
        
        original_entities = self.entities_replaced
        original_warnings = self.warnings_generated
        
        # Process the file
        process_file(filepath, self._entity_replacement_callback)
        
        # Update statistics
        self.files_processed += 1
        
        if self.verbose:
            entities_in_file = self.entities_replaced - original_entities
            warnings_in_file = self.warnings_generated - original_warnings
            print(f"  Entities replaced: {entities_in_file}")
            print(f"  Warnings generated: {warnings_in_file}")
    
    def _entity_replacement_callback(self, entity: str, replaced: bool) -> None:
        """
        Callback function for entity replacement tracking.
        
        Args:
            entity: The entity name that was processed
            replaced: Whether the entity was replaced
        """
        if replaced:
            self.entities_replaced += 1
        else:
            self.warnings_generated += 1
    
    def cleanup(self) -> None:
        """Clean up module resources."""
        if self.verbose:
            print(f"EntityReference cleanup complete")
            print(f"  Total files processed: {self.files_processed}")
            print(f"  Total entities replaced: {self.entities_replaced}")
            print(f"  Total warnings generated: {self.warnings_generated}")


def replace_entities(line, callback=None):
    """
    Replace HTML entity references with AsciiDoc attribute references.

    Args:
        line: Input line to process
        callback: Optional callback function for tracking replacements

    Returns:
        Line with entity references replaced
    """

    def repl(match):
        entity = match.group(1)
        if entity in SUPPORTED_ENTITIES:
            if callback:
                callback(entity, False)
            return match.group(0)
        elif entity in ENTITY_TO_ASCIIDOC:
            if callback:
                callback(entity, True)
            return ENTITY_TO_ASCIIDOC[entity]
        else:
            print(f"Warning: No AsciiDoc attribute for &{entity};")
            if callback:
                callback(entity, False)
            return match.group(0)

    return ENTITY_PATTERN.sub(repl, line)


def process_file(filepath, callback=None):
    """
    Process a single .adoc file, replacing entity references.
    Skip entities within comments (single-line // and block comments ////).

    Args:
        filepath: Path to the file to process
        callback: Optional callback function for tracking replacements
    """
    try:
        lines = read_text_preserve_endings(filepath)
        new_lines = []
        in_block_comment = False

        for text, ending in lines:
            stripped = text.strip()

            # Check for block comment delimiters
            if stripped == "////":
                in_block_comment = not in_block_comment
                new_lines.append((text, ending))
                continue

            # Skip processing if we're in a block comment or it's a single-line comment
            if in_block_comment or stripped.startswith("//"):
                new_lines.append((text, ending))
            else:
                new_lines.append((replace_entities(text, callback), ending))

        write_text_preserve_endings(filepath, new_lines)
        print(f"Processed {filepath} (preserved per-line endings)")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")


def main(args):
    """Legacy main function for backward compatibility."""
    if ADT_MODULE_AVAILABLE:
        # Use the new ADTModule implementation
        module = EntityReferenceModule()
        
        # Initialize with basic configuration
        config = {
            "verbose": getattr(args, "verbose", False),
            "timeout_seconds": 30,
            "cache_size": 1000,
            "skip_comments": True
        }
        module.initialize(config)
        
        # Execute with context
        context = {
            "file": getattr(args, "file", None),
            "recursive": getattr(args, "recursive", False),
            "directory": getattr(args, "directory", "."),
            "verbose": getattr(args, "verbose", False)
        }
        
        result = module.execute(context)
        
        # Cleanup
        module.cleanup()
        
        return result
    else:
        # Fallback to legacy implementation
        process_adoc_files(args, process_file)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser("EntityReference", help=__description__)
    common_arg_parser(parser)
    parser.set_defaults(func=main)
