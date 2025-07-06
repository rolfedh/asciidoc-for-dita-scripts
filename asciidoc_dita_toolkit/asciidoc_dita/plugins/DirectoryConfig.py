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

from ..config_utils import save_json_config as save_config_file, load_json_config as load_config_file
from ..plugin_manager import is_plugin_enabled
from ..security_utils import validate_directory_path

# Constants
CONFIG_VERSION = "1.0"
LOCAL_CHOICE = "1"
HOME_CHOICE = "2"


class DirectoryConfigManager:
    """Manages directory configuration for AsciiDoc processing."""
    
    def create_default_config(self, repo_root=None):
        """Create a default configuration structure."""
        if repo_root is None:
            repo_root = os.getcwd()
        
        config = {
            "version": CONFIG_VERSION,
            "repoRoot": os.path.abspath(repo_root),
            "includeDirs": [],
            "excludeDirs": [],
            "lastUpdated": datetime.now().isoformat()
        }
        
        # Validate schema
        if not self._validate_config_schema(config):
            raise ValueError("Invalid configuration schema")
        
        return config
    
    def _validate_config_schema(self, config):
        """Validate configuration schema structure."""
        required_fields = ["version", "repoRoot", "includeDirs", "excludeDirs", "lastUpdated"]
        
        if not isinstance(config, dict):
            return False
        
        for field in required_fields:
            if field not in config:
                return False
        
        # Type validation
        if not isinstance(config["includeDirs"], list):
            return False
        if not isinstance(config["excludeDirs"], list):
            return False
        
        return True
    
    def validate_directory(self, directory_path, base_path):
        """Validate that a directory exists and is within the repository root."""
        return validate_directory_path(directory_path, base_path, require_exists=True)
    
    def prompt_for_repository_root(self):
        """Prompt user for repository root directory."""
        current_dir = os.getcwd()
        print(f"\nRepository Root Configuration")
        print(f"Current directory: {current_dir}")
        
        try:
            while True:
                repo_root = input(f"Enter repository root path [{current_dir}]: ").strip()
                if not repo_root:
                    repo_root = current_dir
                
                if repo_root.lower() in ['quit', 'exit', 'q']:
                    print("Setup cancelled by user.")
                    sys.exit(0)
                
                repo_root = os.path.abspath(os.path.expanduser(repo_root))
                
                if os.path.exists(repo_root) and os.path.isdir(repo_root):
                    return repo_root
                else:
                    print(f"Error: Directory does not exist: {repo_root}")
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user (Ctrl+C).")
            sys.exit(0)
    
    def prompt_for_directories(self, prompt_text, repo_root, existing_dirs=None):
        """Prompt user for directory list with validation."""
        if existing_dirs is None:
            existing_dirs = []
        
        print(f"\n{prompt_text}")
        print("Enter directory paths relative to repository root, one per line.")
        print("Press Enter on empty line to finish, or 'quit' to exit.")
        
        if existing_dirs:
            print(f"Current directories: {', '.join(existing_dirs)}")
        
        directories = []
        try:
            while True:
                dir_input = input("Directory: ").strip()
                if not dir_input:
                    break
                
                if dir_input.lower() in ['quit', 'exit', 'q']:
                    print("Setup cancelled by user.")
                    sys.exit(0)
                
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
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user (Ctrl+C).")
            sys.exit(0)
        
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
        try:
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
            config_path = self._prompt_for_save_location()
            
            # Step 6: Save configuration with retry
            return self._save_config_with_retry(config_path, config)
            
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user (Ctrl+C).")
            return False
        except Exception as e:
            print(f"\nUnexpected error during setup: {e}")
            return False
    
    def _prompt_for_save_location(self):
        """Prompt user for configuration save location."""
        print("\nWhere would you like to save the configuration?")
        print(f"[{LOCAL_CHOICE}] Current directory (./.adtconfig.json) - Project-specific")
        print(f"[{HOME_CHOICE}] Home directory (~/.adtconfig.json) - Global default")
        
        try:
            while True:
                choice = input(f"Select location [{LOCAL_CHOICE}]: ").strip()
                if not choice:
                    choice = LOCAL_CHOICE
                
                if choice == LOCAL_CHOICE:
                    return "./.adtconfig.json"
                elif choice == HOME_CHOICE:
                    return "~/.adtconfig.json"
                else:
                    print(f"Please enter {LOCAL_CHOICE} or {HOME_CHOICE}")
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user (Ctrl+C).")
            sys.exit(0)
    
    def _save_config_with_retry(self, config_path, config, max_retries=3):
        """Save configuration with retry logic."""
        for attempt in range(max_retries):
            if save_config_file(config_path, config):
                print(f"\n✓ Configuration saved to {config_path}")
                self.display_configuration(config, config_path)
                return True
            else:
                if attempt < max_retries - 1:
                    print(f"\n✗ Failed to save configuration to {config_path}")
                    retry = input("Would you like to try again? (y/n): ").strip().lower()
                    if retry != 'y':
                        # Offer alternative location
                        alt_path = "~/.adtconfig.json" if config_path.startswith("./") else "./.adtconfig.json"
                        try_alt = input(f"Try saving to {alt_path} instead? (y/n): ").strip().lower()
                        if try_alt == 'y':
                            config_path = alt_path
                            continue
                        else:
                            break
                else:
                    print(f"\n✗ Failed to save configuration after {max_retries} attempts")
        
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


# Modular compatibility functions for the new architecture

def load_directory_config():
    """Load directory configuration from the local or home config file.
    
    Returns:
        dict or None: Configuration dictionary if found, None otherwise.
    """
    # Check for local config first
    local_config = load_config_file("./.adtconfig.json")
    if local_config:
        return local_config
    
    # Fallback to home config
    home_config = load_config_file("~/.adtconfig.json")
    return home_config


def apply_directory_filters(base_path, config):
    """Apply directory filters based on configuration.
    
    Args:
        base_path (str): The base directory path to filter
        config (dict): Directory configuration
        
    Returns:
        list: List of filtered directory paths
    """
    import logging
    from ..file_utils import find_adoc_files
    
    logger = logging.getLogger(__name__)
    
    if not config:
        return [base_path]
    
    repo_root = config.get("repoRoot", os.getcwd())
    include_dirs = config.get("includeDirs", [])
    exclude_dirs = config.get("excludeDirs", [])
    
    # Convert to absolute paths
    base_path = os.path.abspath(base_path)
    repo_root = os.path.abspath(repo_root)
    
    # Check if base_path is excluded
    for exclude_dir in exclude_dirs:
        exclude_path = os.path.join(repo_root, exclude_dir)
        exclude_path = os.path.abspath(exclude_path)
        
        # Check if base_path is in or under an excluded directory
        try:
            os.path.commonpath([base_path, exclude_path])
            if base_path.startswith(exclude_path):
                logger.warning(f"Directory {base_path} is excluded by configuration")
                # Still return the path since there's no alternative
                return [base_path]
        except ValueError:
            # Paths are on different drives (Windows) or don't share common path
            continue
    
    # If include dirs are specified, filter based on them
    if include_dirs:
        filtered_dirs = []
        for include_dir in include_dirs:
            include_path = os.path.join(repo_root, include_dir)
            include_path = os.path.abspath(include_path)
            
            # Check if base_path is in or under an included directory
            try:
                os.path.commonpath([base_path, include_path])
                if base_path.startswith(include_path) or include_path.startswith(base_path):
                    filtered_dirs.append(include_path)
            except ValueError:
                # Paths are on different drives (Windows) or don't share common path
                continue
        
        return filtered_dirs if filtered_dirs else [base_path]
    
    # No include filters, just return the base path (exclude filters already checked)
    return [base_path]


def get_filtered_adoc_files(directory_path, config, find_adoc_files_func=None):
    """Get filtered AsciiDoc files based on directory configuration.
    
    Args:
        directory_path (str): The directory to search
        config (dict): Directory configuration
        find_adoc_files_func (callable): Function to find adoc files (optional)
        
    Returns:
        list: List of filtered .adoc file paths
    """
    if find_adoc_files_func is None:
        from ..file_utils import find_adoc_files
        find_adoc_files_func = find_adoc_files
    
    if not config:
        return find_adoc_files_func(directory_path, recursive=True)
    
    repo_root = config.get("repoRoot", os.getcwd())
    include_dirs = config.get("includeDirs", [])
    exclude_dirs = config.get("excludeDirs", [])
    
    all_files = []
    
    # If include dirs are specified, only process those
    if include_dirs:
        for include_dir in include_dirs:
            include_path = os.path.join(repo_root, include_dir)
            include_path = os.path.abspath(include_path)
            
            if os.path.exists(include_path) and os.path.isdir(include_path):
                files = find_adoc_files_func(include_path, recursive=True)
                all_files.extend(files)
    else:
        # Process all files in the directory path
        all_files = find_adoc_files_func(directory_path, recursive=True)
    
    # Filter out excluded directories
    if exclude_dirs:
        filtered_files = []
        for file_path in all_files:
            excluded = False
            abs_file_path = os.path.abspath(file_path)
            
            for exclude_dir in exclude_dirs:
                exclude_path = os.path.join(repo_root, exclude_dir)
                exclude_path = os.path.abspath(exclude_path)
                
                # Check if file is in an excluded directory
                try:
                    os.path.commonpath([abs_file_path, exclude_path])
                    if abs_file_path.startswith(exclude_path):
                        excluded = True
                        break
                except ValueError:
                    # Paths are on different drives (Windows) or don't share common path
                    continue
            
            if not excluded:
                filtered_files.append(file_path)
        
        return filtered_files
    
    return all_files


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
