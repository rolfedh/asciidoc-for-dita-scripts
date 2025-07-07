"""
Content type detection logic for the ContentType plugin.

This module contains the core detection algorithms separated from UI and I/O concerns.
"""

import re
import logging
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class ContentTypeConfig:
    """Configuration for content type detection patterns."""
    
    filename_prefixes: Dict[Tuple[str, ...], str]
    title_patterns: Dict[str, List[str]]
    content_patterns: Dict[str, List[str]]
    
    @classmethod
    def get_default(cls) -> 'ContentTypeConfig':
        """Get default configuration for content type detection."""
        return cls(
            filename_prefixes={
                ("assembly_", "assembly-"): "ASSEMBLY",
                ("con_", "con-"): "CONCEPT",
                ("proc_", "proc-"): "PROCEDURE",
                ("ref_", "ref-"): "REFERENCE",
                ("snip_", "snip-"): "SNIPPET",
            },
            title_patterns={
                "PROCEDURE": [
                    r'^(Creating|Installing|Configuring|Setting up|Building|Deploying|Managing|Updating|Upgrading)',
                    r'^(Adding|Removing|Deleting|Enabling|Disabling|Starting|Stopping|Restarting)',
                    r'^(Implementing|Establishing|Defining|Developing|Generating|Publishing)'
                ],
                "REFERENCE": [
                    r'(reference|commands?|options?|parameters?|settings?|configuration)',
                    r'(syntax|examples?|list of|table of|glossary)',
                    r'(api|cli|command.?line)'
                ],
                "ASSEMBLY": [
                    r'(guide|tutorial|walkthrough|workflow)',
                    r'(getting started|quick start|step.?by.?step)'
                ]
            },
            content_patterns={
                "ASSEMBLY": [
                    r'include::'
                ],
                "PROCEDURE": [
                    r'^\s*\d+\.\s',  # numbered steps
                    r'^\.\s*Procedure\s*$',  # .Procedure section
                    r'^\.\s*Prerequisites?\s*$',  # .Prerequisites section
                    r'^\.\s*Verification\s*$',  # .Verification section
                    r'^\s*\*\s+[A-Z][^.]*\.$'  # bullet points with imperative sentences
                ],
                "REFERENCE": [
                    r'\|====',  # AsciiDoc tables
                    r'^\w+::\s*$',  # definition lists
                    r'^\[options="header"\]',  # table headers
                    r'^\|\s*\w+\s*\|\s*\w+',  # table rows
                ]
            }
        )


@dataclass
class ContentTypeAttribute:
    """Represents a content type attribute found in a file."""
    
    value: str
    line_index: int
    attribute_type: str  # 'current', 'deprecated_content', 'deprecated_module', 'commented'


@dataclass
class DetectionResult:
    """Result of content type detection."""
    
    suggested_type: Optional[str]
    confidence: float
    reasoning: List[str]


class ContentTypeDetector:
    """Handles content type detection logic."""
    
    def __init__(self, config: Optional[ContentTypeConfig] = None):
        self.config = config or ContentTypeConfig.get_default()
        logger.debug("ContentTypeDetector initialized with config: %s", self.config)
    
    def detect_from_filename(self, filename: str) -> Optional[str]:
        """
        Determine content type based on filename prefix.
        
        Args:
            filename: Name of the file (without path)
            
        Returns:
            Content type string or None if no pattern matches
        """
        logger.debug("Detecting content type from filename: %s", filename)
        
        for prefix_group, content_type in self.config.filename_prefixes.items():
            if any(filename.startswith(prefix) for prefix in prefix_group):
                logger.debug("Detected content type '%s' from filename prefix", content_type)
                return content_type
        
        logger.debug("No content type detected from filename")
        return None
    
    def detect_existing_attribute(self, lines: List[Tuple[str, str]]) -> Optional[ContentTypeAttribute]:
        """
        Detect existing content type attributes in file.
        
        Args:
            lines: List of (text, ending) tuples from file
            
        Returns:
            ContentTypeAttribute or None if not found
        """
        logger.debug("Detecting existing content type attributes")
        
        for i, (text, _) in enumerate(lines):
            stripped = text.strip()
            
            # Current format
            if stripped.startswith(":_mod-docs-content-type:"):
                value = stripped.split(":", 2)[-1].strip()
                logger.debug("Found current format content type: %s", value)
                return ContentTypeAttribute(value, i, 'current')
            
            # Commented-out current format
            if stripped.startswith("//:_mod-docs-content-type:"):
                value = stripped.split(":", 2)[-1].strip()
                logger.debug("Found commented content type: %s", value)
                return ContentTypeAttribute(value, i, 'commented')
            
            # Deprecated formats
            if stripped.startswith(":_content-type:"):
                value = stripped.split(":", 2)[-1].strip()
                logger.debug("Found deprecated content-type: %s", value)
                return ContentTypeAttribute(value, i, 'deprecated_content')
                
            if stripped.startswith(":_module-type:"):
                value = stripped.split(":", 2)[-1].strip()
                logger.debug("Found deprecated module-type: %s", value)
                return ContentTypeAttribute(value, i, 'deprecated_module')
        
        logger.debug("No existing content type attributes found")
        return None
    
    def detect_from_title(self, title: str) -> DetectionResult:
        """
        Analyze title style to suggest content type.
        
        Args:
            title: The document title (H1 heading)
            
        Returns:
            DetectionResult with suggestion and reasoning
        """
        logger.debug("Analyzing title: %s", title)
        
        if not title:
            return DetectionResult(None, 0.0, ["No title found"])
        
        title = title.strip()
        # Remove title prefix (= or #) and clean up
        title = re.sub(r'^[=# ]+', '', title).strip()
        
        reasoning = []
        
        for content_type, patterns in self.config.title_patterns.items():
            for pattern in patterns:
                if re.search(pattern, title, re.IGNORECASE):
                    reasoning.append(f"Title matches {content_type.lower()} pattern: {pattern}")
                    logger.debug("Title suggests content type: %s", content_type)
                    return DetectionResult(content_type, 0.8, reasoning)
        
        # Default to concept for other noun phrases
        reasoning.append("Title doesn't match specific patterns, defaulting to CONCEPT")
        logger.debug("No specific title patterns matched, suggesting CONCEPT")
        return DetectionResult("CONCEPT", 0.3, reasoning)
    
    def detect_from_content(self, content: str) -> DetectionResult:
        """
        Analyze content structure to suggest content type.
        
        Args:
            content: Full file content as string
            
        Returns:
            DetectionResult with suggestion and reasoning
        """
        logger.debug("Analyzing content patterns")
        
        reasoning = []
        
        # Check assembly indicators first (most specific)
        assembly_patterns = self.config.content_patterns.get("ASSEMBLY", [])
        for pattern in assembly_patterns:
            if re.search(pattern, content, re.MULTILINE):
                reasoning.append(f"Found assembly pattern: {pattern}")
                logger.debug("Content suggests ASSEMBLY type")
                return DetectionResult("ASSEMBLY", 0.9, reasoning)
        
        # Check procedure indicators
        procedure_patterns = self.config.content_patterns.get("PROCEDURE", [])
        procedure_matches = 0
        for pattern in procedure_patterns:
            if re.search(pattern, content, re.MULTILINE):
                procedure_matches += 1
                reasoning.append(f"Found procedure pattern: {pattern}")
        
        if procedure_matches >= 2:  # Multiple procedure indicators
            logger.debug("Content suggests PROCEDURE type")
            return DetectionResult("PROCEDURE", 0.8, reasoning)
        
        # Check reference indicators
        reference_patterns = self.config.content_patterns.get("REFERENCE", [])
        reference_matches = 0
        for pattern in reference_patterns:
            if re.search(pattern, content, re.MULTILINE):
                reference_matches += 1
                reasoning.append(f"Found reference pattern: {pattern}")
        
        # Count definition lists (::)
        definition_count = len(re.findall(r'::\s*$', content, re.MULTILINE))
        if definition_count > 3:
            reasoning.append(f"Found {definition_count} definition lists")
            reference_matches += 1
        
        if reference_matches >= 1:
            logger.debug("Content suggests REFERENCE type")
            return DetectionResult("REFERENCE", 0.7, reasoning)
        
        # No clear patterns found
        reasoning.append("No specific content patterns detected")
        logger.debug("No specific content patterns detected")
        return DetectionResult(None, 0.0, reasoning)
    
    def get_comprehensive_suggestion(self, filename: str, title: Optional[str], content: str) -> DetectionResult:
        """
        Get comprehensive content type suggestion using all available methods.
        
        Args:
            filename: Name of the file
            title: Document title
            content: Full file content
            
        Returns:
            DetectionResult with best suggestion
        """
        logger.debug("Getting comprehensive suggestion for file: %s", filename)
        
        # Try filename detection first (highest confidence)
        filename_type = self.detect_from_filename(filename)
        if filename_type:
            return DetectionResult(filename_type, 0.95, [f"Detected from filename prefix"])
        
        # Try content analysis (high confidence)
        content_result = self.detect_from_content(content)
        if content_result.suggested_type:
            return content_result
        
        # Try title analysis (medium confidence)
        title_result = self.detect_from_title(title) if title else DetectionResult(None, 0.0, ["No title"])
        if title_result.suggested_type:
            return title_result
        
        # No suggestion found
        return DetectionResult(None, 0.0, ["No patterns matched in filename, title, or content"])
    
    def extract_document_title(self, lines: List[Tuple[str, str]]) -> Optional[str]:
        """
        Extract the document title (first H1 heading) from file lines.
        
        Args:
            lines: List of (text, ending) tuples from file
            
        Returns:
            Title string or None
        """
        for text, _ in lines:
            stripped = text.strip()
            if stripped.startswith('= '):
                title = stripped[2:].strip()
                logger.debug("Found title: %s", title)
                return title
            elif stripped.startswith('# '):
                title = stripped[2:].strip()
                logger.debug("Found title: %s", title)
                return title
        
        logger.debug("No title found")
        return None


def register_subcommand(subparsers):
    """This module doesn't register as a subcommand - it's a helper module."""
    pass