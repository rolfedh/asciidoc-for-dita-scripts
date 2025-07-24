#!/usr/bin/env python3
"""
UserJourney CLI Interface

Command-line interface for the UserJourney workflow orchestration system.
This module provides the main entry point and argument parsing for all
UserJourney commands.

Usage:
    adt journey start --name=<workflow> --directory=<path>
    adt journey resume --name=<workflow>  
    adt journey continue --name=<workflow>
    adt journey status [--name=<workflow>]
    adt journey list
    adt journey cleanup [--name=<workflow>] [--completed] [--all]

Examples:
    adt journey start --name=my_docs --directory=/path/to/docs
    adt journey continue --name=my_docs
    adt journey status --name=my_docs
    adt journey cleanup --completed
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional

# Setup path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from asciidoc_dita_toolkit.asciidoc_dita.plugins.UserJourney import (
        UserJourneyProcessor, WorkflowManager, UserJourneyError
    )
except ImportError as e:
    print(f"❌ Failed to import UserJourney components: {e}")
    print("Make sure you're running from the correct directory.")
    sys.exit(1)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with all subcommands."""
    
    parser = argparse.ArgumentParser(
        prog='adt journey',
        description='UserJourney - Workflow orchestration for ADT',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s start --name=my_docs --directory=/path/to/docs
      Start a new workflow processing all .adoc files in the directory
      
  %(prog)s continue --name=my_docs  
      Continue executing the next module in the workflow
      
  %(prog)s status --name=my_docs
      Show detailed status of a specific workflow
      
  %(prog)s list
      List all available workflows with their status
      
  %(prog)s cleanup --completed
      Remove all completed workflows to save disk space

For more information, visit: https://github.com/rolfedh/asciidoc-dita-toolkit
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging output'
    )
    
    parser.add_argument(
        '--quiet', '-q', 
        action='store_true',
        help='Suppress all but error messages'
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='COMMAND'
    )
    
    # Start command
    start_parser = subparsers.add_parser(
        'start',
        help='Start a new workflow',
        description='Create and start a new UserJourney workflow'
    )
    start_parser.add_argument(
        '--name',
        required=True,
        help='Unique name for the workflow'
    )
    start_parser.add_argument(
        '--directory',
        required=True,
        help='Directory containing .adoc files to process'
    )
    
    # Resume command
    resume_parser = subparsers.add_parser(
        'resume',
        help='Resume an existing workflow',
        description='Load and display status of an existing workflow'
    )
    resume_parser.add_argument(
        '--name',
        required=True,
        help='Name of the workflow to resume'
    )
    
    # Continue command
    continue_parser = subparsers.add_parser(
        'continue',
        help='Continue workflow execution',
        description='Execute the next pending module in a workflow'
    )
    continue_parser.add_argument(
        '--name',
        required=True,
        help='Name of the workflow to continue'
    )
    
    # Status command
    status_parser = subparsers.add_parser(
        'status',
        help='Show workflow status',
        description='Display detailed status information for workflows'
    )
    status_parser.add_argument(
        '--name',
        help='Name of specific workflow to show (if omitted, shows all)'
    )
    
    # List command
    list_parser = subparsers.add_parser(
        'list',
        help='List all workflows',
        description='Display summary of all available workflows'
    )
    
    # Cleanup command  
    cleanup_parser = subparsers.add_parser(
        'cleanup',
        help='Clean up workflows',
        description='Remove workflow files to free up disk space'
    )
    cleanup_group = cleanup_parser.add_mutually_exclusive_group(required=True)
    cleanup_group.add_argument(
        '--name',
        help='Name of specific workflow to delete'
    )
    cleanup_group.add_argument(
        '--completed',
        action='store_true',
        help='Delete all completed workflows'
    )
    cleanup_group.add_argument(
        '--all',
        action='store_true', 
        help='Delete ALL workflows (use with extreme caution!)'
    )
    
    return parser


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure logging based on verbosity settings."""
    
    if quiet:
        log_level = logging.ERROR
    elif verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Reduce noise from other libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the UserJourney CLI.
    
    Args:
        argv: Command line arguments (defaults to sys.argv)
        
    Returns:
        int: Exit code (0 for success, 1+ for error)
    """
    
    parser = create_argument_parser()
    
    # Handle case where no arguments provided
    if not argv and len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    try:
        args = parser.parse_args(argv)
        
        # Setup logging
        setup_logging(
            verbose=getattr(args, 'verbose', False),
            quiet=getattr(args, 'quiet', False)
        )
        
        # Handle case where no subcommand provided
        if not hasattr(args, 'command') or not args.command:
            parser.print_help()
            return 0
        
        # Initialize processor
        try:
            processor = UserJourneyProcessor()
        except Exception as e:
            print(f"❌ Failed to initialize UserJourney: {e}")
            logging.exception("Initialization failed")
            return 1
        
        # Route to appropriate command handler
        command_handlers = {
            'start': processor.process_start_command,
            'resume': processor.process_resume_command,
            'continue': processor.process_continue_command,
            'status': processor.process_status_command,
            'list': processor.process_list_command,
            'cleanup': processor.process_cleanup_command
        }
        
        handler = command_handlers.get(args.command)
        if not handler:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
            return 1
        
        # Execute command
        return handler(args)
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return 130  # Standard exit code for SIGINT
        
    except UserJourneyError as e:
        print(f"❌ UserJourney error: {e}")
        return 1
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logging.exception("Unexpected error in main")
        return 1


def cli_entry_point() -> None:
    """Entry point for the CLI when installed as a package."""
    sys.exit(main())


if __name__ == '__main__':
    # Direct execution entry point
    sys.exit(main())
