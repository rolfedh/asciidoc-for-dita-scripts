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
            content_patterns={
                "ASSEMBLY": [r'include::'],
                "PROCEDURE": [
                    r'^\s*\d+\.\s',  # numbered steps
                    r'^\.\s*Procedure\s*$',  # .Procedure section
                    r'^\.\s*Prerequisites?\s*$',  # .Prerequisites section
                    r'^\.\s*Verification\s*$',  # .Verification section
                    r'^\s*\*\s+[A-Z][^.]*\.$',  # bullet points with imperative sentences
                ],
                "REFERENCE": [
                    r'\|====',  # AsciiDoc tables
                    r'^\w+::\s*$',  # definition lists
                    r'^\[options="header"\]',  # table headers
                    r'^\|\s*\w+\s*\|\s*\w+',  # table rows
                ],
            },
        )


@dataclass
class ContentTypeAttribute:
    """Represents a content type attribute found in a file."""

    value: str
    line_index: int
    attribute_type: (
        str  # 'current', 'deprecated_content', 'deprecated_module', 'commented'
    )


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
                logger.debug(
                    "Detected content type '%s' from filename prefix", content_type
                )
                return content_type

        logger.debug("No content type detected from filename")
        return None

    def detect_existing_attribute(
        self, lines: List[Tuple[str, str]]
    ) -> Optional[ContentTypeAttribute]:
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

    def get_comprehensive_suggestion(
        self, filename: str, title: Optional[str], content: str
    ) -> DetectionResult:
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
            return DetectionResult(
                filename_type, 0.95, [f"Detected from filename prefix"]
            )

        # No suggestion found
        return DetectionResult(
            None, 0.0, ["No patterns matched in filename"]
        )


def register_subcommand(subparsers):
    """This module doesn't register as a subcommand - it's a helper module."""
    pass
