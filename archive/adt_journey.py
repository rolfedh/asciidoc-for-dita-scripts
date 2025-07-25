#!/usr/bin/env python3
"""
ADT Journey - UserJourney Workflow Orchestration CLI [ARCHIVED]

DEPRECATED: This standalone wrapper script is no longer needed.
UserJourney is now fully integrated into the main ADT CLI.

Use instead:
    adt journey start --name=<workflow> --directory=<path>
    adt journey continue --name=<workflow>
    adt journey status --name=<workflow>
    adt journey list
    adt journey cleanup --name=<workflow>

This file is archived for historical reference only.
"""

import sys
from pathlib import Path

# Add the project root to Python path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Import and run the CLI
try:
    from asciidoc_dita_toolkit.modules.user_journey.userjourney_cli import main

    sys.exit(main())
except ImportError as e:
    print(f"❌ Failed to import UserJourney CLI: {e}")
    print("Make sure you're running from the ADT project directory.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
