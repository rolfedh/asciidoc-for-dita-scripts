"""
Plugin for the AsciiDoc DITA toolkit: ContextAnalyzer

This plugin analyzes AsciiDoc documentation to report on context usage
and potential migration complexity. It provides detailed reports on IDs
with _{context} suffixes, xref usage, and potential collision scenarios.

This is Phase 1 of the context migration strategy - analysis only, no changes.
"""

__description__ = "Analyze AsciiDoc documentation for context usage and migration complexity"

import json
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional, Set, Any
import logging

from ..cli_utils import common_arg_parser
from ..file_utils import find_adoc_files, read_text_preserve_endings
from ..workflow_utils import process_adoc_files
from ..regex_patterns import CompiledPatterns

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

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class IDWithContext:
    """Represents an ID with context suffix found in documentation."""
    id_value: str           # Full ID (e.g., "topic_banana")
    base_id: str           # Base without context (e.g., "topic")
    context_value: str     # Context part (e.g., "banana")
    filepath: str
    line_number: int


@dataclass
class XrefUsage:
    """Represents a cross-reference usage found in documentation."""
    target_id: str
    target_file: str       # Empty if same-file reference
    filepath: str          # File containing the xref
    line_number: int
    full_match: str        # Complete xref text


@dataclass
class CollisionReport:
    """Represents a potential ID collision scenario."""
    base_id: str
    conflicting_files: List[str]
    suggested_resolution: str


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""
    filepath: str
    context_attributes: List[str]
    ids_with_context: List[IDWithContext]
    xref_usages: List[XrefUsage]
    link_usages: List[XrefUsage]


@dataclass
class AnalysisReport:
    """Complete analysis report for the documentation set."""
    total_files_scanned: int
    files_with_context_ids: int
    total_context_ids: int
    total_xrefs: int
    total_links: int
    potential_collisions: List[CollisionReport]
    file_analyses: List[FileAnalysis]


class ContextAnalyzerModule(ADTModule):
    """
    ADTModule implementation for ContextAnalyzer plugin.
    
    This module analyzes AsciiDoc documentation to report on context usage
    and potential migration complexity. It provides detailed reports on IDs
    with _{context} suffixes, xref usage, and potential collision scenarios.
    """
    
    @property
    def name(self) -> str:
        """Module name identifier."""
        return "ContextAnalyzer"
    
    @property
    def version(self) -> str:
        """Module version using semantic versioning."""
        return "1.2.0"
    
    @property
    def dependencies(self) -> List[str]:
        """List of required module names."""
        return ["EntityReference", "ContentType"]  # Depends on EntityReference and ContentType
    
    @property
    def release_status(self) -> str:
        """Release status: 'GA' for stable."""
        return "GA"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the module with configuration.
        
        Args:
            config: Configuration dictionary containing module settings
        """
        # Analysis configuration
        self.output_format = config.get("output_format", "text")
        self.detailed = config.get("detailed", False)
        self.collisions_only = config.get("collisions_only", False)
        self.output_file = config.get("output_file")
        self.verbose = config.get("verbose", False)
        
        # Initialize statistics
        self.files_analyzed = 0
        self.context_ids_found = 0
        self.xrefs_found = 0
        self.links_found = 0
        self.collisions_detected = 0
        
        # Initialize analyzer
        self.analyzer = ContextAnalyzer()
        
        if self.verbose:
            print(f"Initialized ContextAnalyzer v{self.version}")
            print(f"  Output format: {self.output_format}")
            print(f"  Detailed: {self.detailed}")
            print(f"  Collisions only: {self.collisions_only}")
            print(f"  Output file: {self.output_file}")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the context analysis.
        
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
            self.files_analyzed = 0
            self.context_ids_found = 0
            self.xrefs_found = 0
            self.links_found = 0
            self.collisions_detected = 0
            
            # Process files using the existing logic
            process_adoc_files(args, self._process_file_wrapper)
            
            # Generate report
            report = self.analyzer.generate_report()
            
            # Update statistics
            self.files_analyzed = report.total_files_scanned
            self.context_ids_found = report.total_context_ids
            self.xrefs_found = report.total_xrefs
            self.links_found = report.total_links
            self.collisions_detected = len(report.potential_collisions)
            
            # Generate output content
            output_content = self._generate_output_content(report)
            
            # Save to file if specified
            if self.output_file:
                self._save_output_to_file(output_content)
            
            return {
                "module_name": self.name,
                "version": self.version,
                "success": True,
                "files_analyzed": self.files_analyzed,
                "context_ids_found": self.context_ids_found,
                "xrefs_found": self.xrefs_found,
                "links_found": self.links_found,
                "collisions_detected": self.collisions_detected,
                "output_format": self.output_format,
                "output_file": self.output_file,
                "output_content": output_content if not self.output_file else None,
                "report": asdict(report) if self.output_format == "json" else None
            }
            
        except Exception as e:
            error_msg = f"Error in ContextAnalyzer module: {e}"
            if self.verbose:
                print(error_msg)
            return {
                "module_name": self.name,
                "version": self.version,
                "error": str(e),
                "success": False,
                "files_analyzed": self.files_analyzed,
                "context_ids_found": self.context_ids_found,
                "xrefs_found": self.xrefs_found,
                "links_found": self.links_found,
                "collisions_detected": self.collisions_detected
            }
    
    def _process_file_wrapper(self, filepath: str) -> bool:
        """
        Wrapper around the process_context_analyzer_file function.
        
        Args:
            filepath: Path to the file to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        if self.verbose:
            print(f"Analyzing file: {filepath}")
        
        try:
            process_context_analyzer_file(filepath, self.analyzer)
            return True
            
        except Exception as e:
            logger.error("Error processing file %s: %s", filepath, e)
            return False
    
    def _generate_output_content(self, report: AnalysisReport) -> str:
        """
        Generate output content based on configuration.
        
        Args:
            report: Analysis report to format
            
        Returns:
            Formatted output content
        """
        if self.output_format == 'json':
            # Convert to JSON-serializable format
            report_dict = asdict(report)
            return json.dumps(report_dict, indent=2)
        else:
            return format_text_report(report, self.detailed, self.collisions_only)
    
    def _save_output_to_file(self, content: str) -> None:
        """
        Save output content to file.
        
        Args:
            content: Content to save
        """
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            if self.verbose:
                print(f"Analysis report saved to {self.output_file}")
        except Exception as e:
            logger.error(f"Error saving output to {self.output_file}: {e}")
            raise
    
    def cleanup(self) -> None:
        """Clean up module resources."""
        if self.verbose:
            print(f"ContextAnalyzer cleanup complete")
            print(f"  Total files analyzed: {self.files_analyzed}")
            print(f"  Total context IDs found: {self.context_ids_found}")
            print(f"  Total xrefs found: {self.xrefs_found}")
            print(f"  Total links found: {self.links_found}")
            print(f"  Total collisions detected: {self.collisions_detected}")
            print(f"  Output format: {self.output_format}")


class ContextAnalyzer:
    """
    Analyzes AsciiDoc documentation to report on context usage
    and potential migration complexity.
    """
    
    def __init__(self):
        # Use shared regex patterns
        self.id_with_context_regex = CompiledPatterns.ID_WITH_CONTEXT_REGEX
        self.xref_regex = CompiledPatterns.XREF_BASIC_REGEX
        self.link_regex = CompiledPatterns.LINK_REGEX
        self.context_attr_regex = CompiledPatterns.CONTEXT_ATTR_REGEX
        
        # Analysis state
        self.all_ids: Dict[str, List[IDWithContext]] = {}  # base_id -> list of IDWithContext
        self.all_xrefs: List[XrefUsage] = []
        self.all_links: List[XrefUsage] = []
        self.file_analyses: List[FileAnalysis] = []
        
    def analyze_file(self, filepath: str) -> FileAnalysis:
        """
        Analyze a single AsciiDoc file for context usage.
        
        Args:
            filepath: Path to the file to analyze
            
        Returns:
            FileAnalysis object with results
        """
        try:
            lines = read_text_preserve_endings(filepath)
            content = ''.join(text + ending for text, ending in lines)
            
            # Find context attributes
            context_attributes = []
            for match in self.context_attr_regex.finditer(content):
                context_attributes.append(match.group(1).strip())
            
            # Find IDs with context
            ids_with_context = []
            for line_num, (text, _) in enumerate(lines, 1):
                for match in self.id_with_context_regex.finditer(text):
                    full_id = match.group(1) + '_' + match.group(2)
                    base_id = match.group(1)
                    context_value = match.group(2)
                    
                    id_with_context = IDWithContext(
                        id_value=full_id,
                        base_id=base_id,
                        context_value=context_value,
                        filepath=filepath,
                        line_number=line_num
                    )
                    ids_with_context.append(id_with_context)
                    
                    # Track for collision detection
                    if base_id not in self.all_ids:
                        self.all_ids[base_id] = []
                    self.all_ids[base_id].append(id_with_context)
            
            # Find xref usage
            xref_usages = []
            for line_num, (text, _) in enumerate(lines, 1):
                for match in self.xref_regex.finditer(text):
                    # XREF_BASIC_PATTERN captures: ([^#\[]+)(?:#([^#\[]+))?(\[.*?\])
                    # Group 1: file_or_id (before # or [)
                    # Group 2: optional_id (after #)
                    # Group 3: link_text (in brackets)
                    
                    first_part = match.group(1) if match.group(1) else ""
                    second_part = match.group(2) if match.group(2) else ""
                    full_match = match.group(0)
                    
                    if second_part:
                        # Format: xref:file.adoc#target_id[text]
                        target_file = first_part
                        target_id = second_part
                    else:
                        # Format: xref:target_id[text]
                        target_file = ""
                        target_id = first_part
                    
                    xref_usage = XrefUsage(
                        target_id=target_id,
                        target_file=target_file,
                        filepath=filepath,
                        line_number=line_num,
                        full_match=full_match
                    )
                    xref_usages.append(xref_usage)
                    self.all_xrefs.append(xref_usage)
            
            # Find link usage
            link_usages = []
            for line_num, (text, _) in enumerate(lines, 1):
                for match in self.link_regex.finditer(text):
                    # LINK_PATTERN captures: ([^#\[]+)(?:#([^#\[]+))?(\[.*?\])
                    # Group 1: url_or_file (before # or [)
                    # Group 2: optional_anchor (after #)
                    # Group 3: link_text (in brackets)
                    
                    first_part = match.group(1) if match.group(1) else ""
                    second_part = match.group(2) if match.group(2) else ""
                    full_match = match.group(0)
                    
                    if second_part:
                        # Format: link:url#anchor[text]
                        target_file = first_part
                        target_id = second_part
                    else:
                        # Format: link:url[text]
                        target_file = first_part
                        target_id = ""
                    
                    link_usage = XrefUsage(
                        target_id=target_id,
                        target_file=target_file,
                        filepath=filepath,
                        line_number=line_num,
                        full_match=full_match
                    )
                    link_usages.append(link_usage)
                    self.all_links.append(link_usage)
            
            file_analysis = FileAnalysis(
                filepath=filepath,
                context_attributes=context_attributes,
                ids_with_context=ids_with_context,
                xref_usages=xref_usages,
                link_usages=link_usages
            )
            
            self.file_analyses.append(file_analysis)
            return file_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing file {filepath}: {e}")
            return FileAnalysis(
                filepath=filepath,
                context_attributes=[],
                ids_with_context=[],
                xref_usages=[],
                link_usages=[]
            )
    
    def detect_id_collisions(self) -> List[CollisionReport]:
        """
        Detect potential ID collisions that would occur after context removal.
        
        Returns:
            List of CollisionReport objects
        """
        collisions = []
        
        for base_id, id_list in self.all_ids.items():
            if len(id_list) > 1:
                # Multiple IDs would become the same after context removal
                conflicting_files = [id_obj.filepath for id_obj in id_list]
                unique_files = list(set(conflicting_files))
                
                if len(unique_files) > 1:
                    # Collision across multiple files
                    suggested_resolution = f"Consider renaming to {base_id}-1, {base_id}-2, etc."
                else:
                    # Multiple contexts in same file
                    suggested_resolution = f"Multiple contexts in same file - automatic numbering will be applied"
                
                collision = CollisionReport(
                    base_id=base_id,
                    conflicting_files=unique_files,
                    suggested_resolution=suggested_resolution
                )
                collisions.append(collision)
        
        return collisions
    
    def generate_report(self) -> AnalysisReport:
        """
        Generate a comprehensive analysis report.
        
        Returns:
            AnalysisReport object
        """
        collisions = self.detect_id_collisions()
        
        total_files_scanned = len(self.file_analyses)
        files_with_context_ids = len([f for f in self.file_analyses if f.ids_with_context])
        total_context_ids = sum(len(f.ids_with_context) for f in self.file_analyses)
        total_xrefs = len(self.all_xrefs)
        total_links = len(self.all_links)
        
        return AnalysisReport(
            total_files_scanned=total_files_scanned,
            files_with_context_ids=files_with_context_ids,
            total_context_ids=total_context_ids,
            total_xrefs=total_xrefs,
            total_links=total_links,
            potential_collisions=collisions,
            file_analyses=self.file_analyses
        )
    
    def analyze_directory(self, root_dir: str) -> AnalysisReport:
        """
        Analyze all AsciiDoc files in a directory.
        
        Args:
            root_dir: Directory to analyze
            
        Returns:
            AnalysisReport object
        """
        try:
            adoc_files = find_adoc_files(root_dir, recursive=True)
            
            for filepath in adoc_files:
                self.analyze_file(filepath)
            
            return self.generate_report()
            
        except Exception as e:
            logger.error(f"Error analyzing directory {root_dir}: {e}")
            return AnalysisReport(
                total_files_scanned=0,
                files_with_context_ids=0,
                total_context_ids=0,
                total_xrefs=0,
                total_links=0,
                potential_collisions=[],
                file_analyses=[]
            )


def format_text_report(report: AnalysisReport, detailed: bool = False, collisions_only: bool = False) -> str:
    """
    Format the analysis report as human-readable text.
    
    Args:
        report: AnalysisReport to format
        detailed: Whether to include detailed per-file information
        collisions_only: Whether to show only collision information
        
    Returns:
        Formatted text report
    """
    if collisions_only:
        lines = ["=== Context Migration Collision Analysis ===", ""]
        
        if report.potential_collisions:
            lines.append("=== Potential ID Collisions ===")
            for collision in report.potential_collisions:
                lines.append(f"Base ID '{collision.base_id}'")
                for filepath in collision.conflicting_files:
                    lines.append(f"  - {filepath}")
                lines.append(f"  Suggested: {collision.suggested_resolution}")
                lines.append("")
        else:
            lines.append("No potential ID collisions detected.")
            
        return "\n".join(lines)
    
    lines = ["=== Context Migration Analysis Report ===", ""]
    
    # Summary
    lines.extend([
        f"Files Scanned: {report.total_files_scanned}",
        f"Files with Context IDs: {report.files_with_context_ids}",
        f"Total IDs with _{{context}}: {report.total_context_ids}",
        f"Total xrefs found: {report.total_xrefs}",
        f"Total links found: {report.total_links}",
        ""
    ])
    
    # Collision analysis
    if report.potential_collisions:
        lines.append("=== Potential ID Collisions ===")
        for collision in report.potential_collisions:
            lines.append(f"Base ID '{collision.base_id}'")
            for filepath in collision.conflicting_files:
                lines.append(f"  - {filepath}")
            lines.append(f"  Suggested: {collision.suggested_resolution}")
            lines.append("")
    else:
        lines.extend(["=== Potential ID Collisions ===", "None detected.", ""])
    
    # Detailed file analysis
    if detailed:
        lines.append("=== Files Requiring Migration ===")
        for file_analysis in report.file_analyses:
            if file_analysis.ids_with_context:
                lines.append(f"{file_analysis.filepath}:")
                for id_with_context in file_analysis.ids_with_context:
                    lines.append(f"  - [id=\"{id_with_context.id_value}\"] → [id=\"{id_with_context.base_id}\"] (line {id_with_context.line_number})")
                lines.append("")
    
    # Risk assessment
    lines.append("=== Summary ===")
    low_risk = sum(1 for f in report.file_analyses if f.ids_with_context and not any(
        collision.base_id in [id_obj.base_id for id_obj in f.ids_with_context]
        for collision in report.potential_collisions
    ))
    medium_risk = len(report.potential_collisions)
    high_risk = sum(1 for f in report.file_analyses if len(f.context_attributes) > 1)
    
    lines.extend([
        f"- Low Risk: {low_risk} files (simple context removal)",
        f"- Medium Risk: {medium_risk} files (potential collisions)",
        f"- High Risk: {high_risk} files (complex multi-context scenarios)",
        "",
        "Recommended approach: Batch migration by risk level"
    ])
    
    return "\n".join(lines)


def process_context_analyzer_file(filepath: str, analyzer: ContextAnalyzer):
    """
    Process a single file with the context analyzer.
    
    Args:
        filepath: Path to the file to process
        analyzer: ContextAnalyzer instance
    """
    analyzer.analyze_file(filepath)


def main(args):
    """Legacy main function for backward compatibility."""
    if ADT_MODULE_AVAILABLE:
        # Use the new ADTModule implementation
        module = ContextAnalyzerModule()
        
        # Initialize with configuration from args
        config = {
            "output_format": getattr(args, "format", "text"),
            "detailed": getattr(args, "detailed", False),
            "collisions_only": getattr(args, "collisions_only", False),
            "output_file": getattr(args, "output", None),
            "verbose": getattr(args, "verbose", False)
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
        
        # Display output if not saved to file
        if not result.get("output_file") and result.get("output_content"):
            print(result["output_content"])
        
        # Check if module execution was successful
        if not result.get("success", False):
            if result.get("error"):
                print(f"Error: {result['error']}")
            sys.exit(1)
        
        # Cleanup
        module.cleanup()
        
        return result
    else:
        # Fallback to legacy implementation
        # Setup logging
        if hasattr(args, 'verbose') and args.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        
        analyzer = ContextAnalyzer()
        
        # Process files
        def process_file_wrapper(filepath):
            return process_context_analyzer_file(filepath, analyzer)
        
        try:
            process_adoc_files(args, process_file_wrapper)
            report = analyzer.generate_report()
            
            # Generate output
            output_format = getattr(args, 'format', 'text')
            detailed = getattr(args, 'detailed', False)
            collisions_only = getattr(args, 'collisions_only', False)
            output_file = getattr(args, 'output', None)
            
            if output_format == 'json':
                # Convert to JSON-serializable format
                report_dict = asdict(report)
                output_content = json.dumps(report_dict, indent=2)
            else:
                output_content = format_text_report(report, detailed, collisions_only)
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                print(f"Analysis report saved to {output_file}")
            else:
                print(output_content)
                
        except KeyboardInterrupt:
            logger.info("Analysis interrupted by user")
            print("\nAnalysis interrupted by user.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {e}")
            print(f"Error during analysis: {e}")
            sys.exit(1)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser(
        "ContextAnalyzer",
        help=__description__,
        description=__description__
    )
    
    # Add common arguments
    common_arg_parser(parser)
    
    # Add plugin-specific arguments
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Include detailed per-file analysis in the report"
    )
    
    parser.add_argument(
        "--collisions-only",
        action="store_true",
        help="Show only potential ID collision information"
    )
    
    parser.add_argument(
        "--format",
        choices=['text', 'json'],
        default='text',
        help="Output format for the report (default: text)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Save report to specified file instead of printing to console"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output"
    )
    
    parser.set_defaults(func=main)