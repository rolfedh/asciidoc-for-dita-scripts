#!/usr/bin/env python3
"""
ADT Journey - UserJourney Workflow Orchestration CLI

Simple wrapper script to run the UserJourney CLI interface.
This can be used directly or integrated into the main ADT CLI system.
"""

import sys
from pathlib import Path

# Add the project root to Python path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import and run the CLI
try:
    from asciidoc_dita_toolkit.asciidoc_dita.plugins.userjourney_cli import main
    sys.exit(main())
except ImportError as e:
    print(f"❌ Failed to import UserJourney CLI: {e}")
    print("Make sure you're running from the ADT project directory.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
