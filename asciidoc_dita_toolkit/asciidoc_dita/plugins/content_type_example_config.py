"""
Example configuration for the ContentType plugin.

This file demonstrates how to extend the content type detection patterns
for custom use cases without modifying the core plugin code.
"""

from .content_type_detector import ContentTypeConfig
from .ContentType import create_processor


def create_custom_processor(batch_mode=False):
    """
    Create a ContentTypeProcessor with custom configuration.
    
    Args:
        batch_mode: If True, use batch UI mode
        
    Returns:
        Configured ContentTypeProcessor with custom patterns
    """
    
    # Define custom configuration
    custom_config = ContentTypeConfig(
        filename_prefixes={
            # Standard prefixes (keep existing)
            ("assembly_", "assembly-"): "ASSEMBLY",
            ("con_", "con-"): "CONCEPT",
            ("proc_", "proc-"): "PROCEDURE",
            ("ref_", "ref-"): "REFERENCE",
            ("snip_", "snip-"): "SNIPPET",
            
            # Custom prefixes for organization-specific patterns
            ("tut_", "tutorial-"): "TUTORIAL",
            ("guide_", "guide-"): "GUIDE",
            ("api_", "api-"): "API_REFERENCE",
            ("troubleshoot_", "troubleshooting-"): "TROUBLESHOOTING",
        },
        
        title_patterns={
            # Standard patterns (keep existing)
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
            ],
            
            # Custom patterns for new content types
            "TUTORIAL": [
                r'^(Tutorial|Learning|Step-by-step)',
                r'(how to|walkthrough|hands-on)'
            ],
            "TROUBLESHOOTING": [
                r'^(Troubleshooting|Debugging|Fixing|Resolving)',
                r'(problem|issue|error|failure)',
                r'(cannot|unable|failed|broken)'
            ],
            "API_REFERENCE": [
                r'(api|application programming interface)',
                r'(endpoint|method|function|class)',
                r'(request|response|parameter|return)'
            ]
        },
        
        content_patterns={
            # Standard patterns (keep existing)
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
            ],
            
            # Custom patterns for new content types
            "TUTORIAL": [
                r'^\s*Step\s+\d+:',  # Step 1:, Step 2:, etc.
                r'^\s*Exercise\s+\d+',  # Exercise 1, Exercise 2, etc.
                r'^\s*Lab\s+\d+',  # Lab 1, Lab 2, etc.
                r'\.Example\s*$'  # .Example sections
            ],
            "TROUBLESHOOTING": [
                r'^\s*Problem\s*$',  # Problem sections
                r'^\s*Solution\s*$',  # Solution sections
                r'^\s*Cause\s*$',  # Cause sections
                r'^\s*Resolution\s*$',  # Resolution sections
                r'Error:\s*',  # Error messages
                r'Exception:\s*'  # Exception messages
            ],
            "API_REFERENCE": [
                r'^\s*GET\s+/',  # HTTP GET endpoints
                r'^\s*POST\s+/',  # HTTP POST endpoints
                r'^\s*PUT\s+/',  # HTTP PUT endpoints
                r'^\s*DELETE\s+/',  # HTTP DELETE endpoints
                r'```\s*http',  # HTTP code blocks
                r'```\s*json',  # JSON code blocks
                r'```\s*curl'  # curl command examples
            ]
        }
    )
    
    return create_processor(batch_mode, custom_config)


def example_usage():
    """
    Example of how to use the custom configuration.
    """
    # Create processor with custom configuration
    processor = create_custom_processor(batch_mode=True)
    
    # Process a file (would normally be called by the main workflow)
    # success = processor.process_file("/path/to/file.adoc")
    
    print("Custom ContentType processor created with extended patterns")
    print("New content types supported:")
    print("- TUTORIAL (tut_*, tutorial-*)")
    print("- TROUBLESHOOTING (troubleshoot_*, troubleshooting-*)")
    print("- API_REFERENCE (api_*, api-*)")
    print("- GUIDE (guide_*, guide-*)")


def register_subcommand(subparsers):
    """This module doesn't register as a subcommand - it's an example/helper module."""
    pass


if __name__ == "__main__":
    example_usage()