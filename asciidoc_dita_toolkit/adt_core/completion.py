#!/usr/bin/env python3
"""
Completion helper for adt CLI.

This module provides functions to generate completion data for bash/zsh shells.
It's designed to be called by shell completion scripts to provide dynamic
module names and other completion data.
"""

import sys
import json
from typing import List, Dict, Any

from .cli import get_new_modules_for_help


def get_available_modules() -> List[str]:
    """Get list of available module names for completion."""
    try:
        modules = get_new_modules_for_help()
        return sorted(modules.keys())
    except Exception:
        # Fallback module list if dynamic discovery fails
        return [
            "ArchiveUnusedFiles",
            "ContentType", 
            "ContextAnalyzer",
            "ContextMigrator",
            "CrossReference",
            "DirectoryConfig",
            "EntityReference",
            "ExampleBlock",
            "UserJourney",
            "ValeFlagger"
        ]


def get_journey_commands() -> List[str]:
    """Get UserJourney subcommands."""
    return ["start", "resume", "continue", "status", "list", "cleanup"]


def get_base_options() -> List[str]:
    """Get base adt command options."""
    return ["--help", "--version", "--list-modules", "--suppress-warnings", "--show-warnings"]


def get_module_options() -> List[str]:
    """Get common module options."""
    return ["-f", "--file", "-r", "--recursive", "-d", "--directory", "-v", "--verbose", "-h", "--help"]


def get_valeflag_options() -> List[str]:
    """Get ValeFlagger-specific options."""
    return ["--enable-rules", "--disable-rules", "--config", "--execute-changes"]


def get_journey_options() -> List[str]:
    """Get UserJourney-specific options."""
    return ["-n", "--name", "--completed", "--all"]


def main():
    """Main entry point for completion helper."""
    if len(sys.argv) < 2:
        print("Usage: python -m asciidoc_dita_toolkit.adt_core.completion <completion_type>", file=sys.stderr)
        sys.exit(1)
    
    completion_type = sys.argv[1]
    
    try:
        if completion_type == "modules":
            modules = get_available_modules()
            print(" ".join(modules))
        elif completion_type == "journey-commands":
            commands = get_journey_commands()
            print(" ".join(commands))
        elif completion_type == "base-options":
            options = get_base_options()
            print(" ".join(options))
        elif completion_type == "module-options":
            options = get_module_options()
            print(" ".join(options))
        elif completion_type == "valeflag-options":
            options = get_valeflag_options()
            print(" ".join(options))
        elif completion_type == "journey-options":
            options = get_journey_options()
            print(" ".join(options))
        elif completion_type == "all":
            # Return JSON with all completion data
            data = {
                "modules": get_available_modules(),
                "journey_commands": get_journey_commands(),
                "base_options": get_base_options(),
                "module_options": get_module_options(),
                "valeflag_options": get_valeflag_options(),
                "journey_options": get_journey_options()
            }
            print(json.dumps(data))
        else:
            print(f"Unknown completion type: {completion_type}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        # Silently fail for completion - don't show errors during tab completion
        pass


if __name__ == "__main__":
    main()