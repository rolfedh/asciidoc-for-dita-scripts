"""
Plugin for the AsciiDoc DITA toolkit: DirectoryConfig

This plugin provides directory-scoped processing capabilities for AsciiDoc files.
It allows users to configure which directories to include/exclude during processing,
with persistent configuration stored in .adtconfig.json files.

This is a preview feature that must be explicitly enabled via:
export ADT_ENABLE_DIRECTORY_CONFIG=true
"""

__description__ = "Configure directory scoping for AsciiDoc processing (preview)"

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from ..file_utils import save_config_file, load_config_file, is_plugin_enabled


class DirectoryConfigManager:
    """Manages directory configuration for AsciiDoc processing."""
    
    def __init__(self):
        self.config_filename = ".adtconfig.json"
    
    def create_default_config(self, repo_root=None):
        """Create a default configuration structure."""
        if repo_root is None:
            repo_root = os.getcwd()
        
        return {
            "version": "1.0",
            "repoRoot": os.path.abspath(repo_root),
            "includeDirs": [],
            "excludeDirs": [],
            "lastUpdated": datetime.now().isoformat()
        }
    
    def validate_directory(self, directory_path, base_path):
        """Validate that a directory exists and is within the repository root."""
        if not directory_path:
            return False, "Directory path cannot be empty"
        
        # Convert to absolute path relative to base_path
        if not os.path.isabs(directory_path):
            full_path = os.path.join(base_path, directory_path)
        else:
            full_path = directory_path
        
        if not os.path.exists(full_path):
            return False, f"Directory does not exist: {full_path}"
        
        if not os.path.isdir(full_path):
            return False, f"Path is not a directory: {full_path}"
        
        return True, full_path
    
    def prompt_for_repository_root(self):
        """Prompt user for repository root directory."""
        current_dir = os.getcwd()
        print(f"\nRepository Root Configuration")
        print(f"Current directory: {current_dir}")
        
        while True:
            repo_root = input(f"Enter repository root path [{current_dir}]: ").strip()
            if not repo_root:
                repo_root = current_dir
            
            repo_root = os.path.abspath(os.path.expanduser(repo_root))
            
            if os.path.exists(repo_root) and os.path.isdir(repo_root):
                return repo_root
            else:
                print(f"Error: Directory does not exist: {repo_root}")
    
    def prompt_for_directories(self, prompt_text, repo_root, existing_dirs=None):
        """Prompt user for directory list with validation."""
        if existing_dirs is None:
            existing_dirs = []
        
        print(f"\n{prompt_text}")
        print("Enter directory paths relative to repository root, one per line.")
        print("Press Enter on empty line to finish.")
        
        if existing_dirs:
            print(f"Current directories: {', '.join(existing_dirs)}")
        
        directories = []
        while True:
            dir_input = input("Directory: ").strip()
            if not dir_input:
                break
            
            # Validate directory
            is_valid, result = self.validate_directory(dir_input, repo_root)
            if is_valid:
                # Convert to relative path for storage
                rel_path = os.path.relpath(result, repo_root)
                if rel_path not in directories:
                    directories.append(rel_path)
                    print(f"  ✓ Added: {rel_path}")
                else:
                    print(f"  ! Already added: {rel_path}")
            else:
                print(f"  ✗ {result}")
        
        return directories
    
    def display_configuration(self, config, config_path=None):
        """Display current configuration in a user-friendly format."""
        print("\n" + "="*50)
        print("Directory Configuration")
        print("="*50)
        
        if config_path:
            print(f"Configuration file: {config_path}")
        
        print(f"Repository root: {config['repoRoot']}")
        print(f"Last updated: {config['lastUpdated']}")
        
        if config['includeDirs']:
            print(f"\nInclude directories ({len(config['includeDirs'])}):")
            for dir_name in config['includeDirs']:
                print(f"  + {dir_name}")
        else:
            print(f"\nInclude directories: All directories (no restrictions)")
        
        if config['excludeDirs']:
            print(f"\nExclude directories ({len(config['excludeDirs'])}):")
            for dir_name in config['excludeDirs']:
                print(f"  - {dir_name}")
        else:
            print(f"\nExclude directories: None")
        
        print("="*50)
    
    def interactive_setup(self):
        """Run interactive setup wizard for directory configuration."""
        print("ADT Directory Configuration Setup")
        print("=" * 40)
        
        # Step 1: Repository root
        repo_root = self.prompt_for_repository_root()
        
        # Step 2: Include directories
        include_dirs = self.prompt_for_directories(
            "Include Directories (leave empty to include all)", 
            repo_root
        )
        
        # Step 3: Exclude directories  
        exclude_dirs = self.prompt_for_directories(
            "Exclude Directories (leave empty to exclude none)", 
            repo_root
        )
        
        # Step 4: Create configuration
        config = self.create_default_config(repo_root)
        config['includeDirs'] = include_dirs
        config['excludeDirs'] = exclude_dirs
        
        # Step 5: Choose where to save
        print("\nWhere would you like to save the configuration?")
        print("[1] Current directory (./.adtconfig.json) - Project-specific")
        print("[2] Home directory (~/.adtconfig.json) - Global default")
        
        while True:
            choice = input("Select location [1]: ").strip()
            if not choice:
                choice = "1"
            
            if choice == "1":
                config_path = "./.adtconfig.json"
                break
            elif choice == "2":
                config_path = "~/.adtconfig.json"
                break
            else:
                print("Please enter 1 or 2")
        
        # Step 6: Save configuration
        if save_config_file(config_path, config):
            print(f"\n✓ Configuration saved to {config_path}")
            self.display_configuration(config, config_path)
            return True
        else:
            print(f"\n✗ Failed to save configuration to {config_path}")
            return False
    
    def show_current_config(self):
        """Display the current active configuration."""
        # Check for local config first
        local_config = load_config_file("./.adtconfig.json")
        home_config = load_config_file("~/.adtconfig.json")
        
        if local_config and home_config:
            print("Multiple configuration files found:")
            print("\nLocal configuration (./.adtconfig.json):")
            self.display_configuration(local_config, "./.adtconfig.json")
            print("\nHome configuration (~/.adtconfig.json):")
            self.display_configuration(home_config, "~/.adtconfig.json")
            print("\nNote: Local configuration takes precedence when both exist.")
        elif local_config:
            self.display_configuration(local_config, "./.adtconfig.json")
        elif home_config:
            self.display_configuration(home_config, "~/.adtconfig.json")
        else:
            print("No directory configuration found.")
            print("Run 'adt DirectoryConfig' to create a configuration.")


def run_directory_config(args):
    """Main entry point for directory-config command."""
    if not is_plugin_enabled("DirectoryConfig"):
        print("Directory configuration is currently disabled.")
        print("To enable this preview feature, run:")
        print("  export ADT_ENABLE_DIRECTORY_CONFIG=true")
        print("Then run the command again.")
        sys.exit(1)
    
    manager = DirectoryConfigManager()
    
    if args.show:
        manager.show_current_config()
    else:
        # Run interactive setup
        if manager.interactive_setup():
            print("\nDirectory configuration setup completed successfully!")
            print("All ADT plugins will now use this directory configuration.")
        else:
            print("\nDirectory configuration setup failed.")
            sys.exit(1)


def register_subcommand(subparsers):
    """Register the DirectoryConfig subcommand."""
    parser = subparsers.add_parser(
        "DirectoryConfig",
        help="Configure directory scoping for AsciiDoc processing",
        description="Set up directory inclusion/exclusion rules for AsciiDoc file processing. "
                   "This allows you to configure which directories ADT should process, "
                   "providing consistent scoping across all plugins."
    )
    
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display current directory configuration"
    )
    
    parser.set_defaults(func=run_directory_config)
