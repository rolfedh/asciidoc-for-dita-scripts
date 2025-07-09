"""
Plugin for the AsciiDoc DITA toolkit: DirectoryConfig

This plugin provides directory-scoped processing capabilities for AsciiDoc files.
It allows users to configure which directories to include/exclude during processing,
with persistent configuration stored in .adtconfig.json files.

This is a preview feature that must be explicitly enabled via:
export ADT_ENABLE_DIRECTORY_CONFIG=true
"""

__description__ = "Configure directory scoping for AsciiDoc processing (preview)"

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

from ..config_utils import save_json_config as save_config_file, load_json_config as load_config_file
from ..plugin_manager import is_plugin_enabled
from ..security_utils import validate_directory_path

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

# Constants
CONFIG_VERSION = "1.0"
LOCAL_CHOICE = "1"
HOME_CHOICE = "2"

# Set up logging
logger = logging.getLogger(__name__)


class DirectoryConfigModule(ADTModule):
    """
    ADTModule implementation for DirectoryConfig plugin.
    
    This module provides directory-scoped processing capabilities for AsciiDoc files,
    allowing users to configure which directories to include/exclude during processing.
    Supports both interactive setup and automated configuration management.
    """
    
    @property
    def name(self) -> str:
        """Module name identifier."""
        return "DirectoryConfig"
    
    @property
    def version(self) -> str:
        """Module version using semantic versioning."""
        return "1.3.0"
    
    @property
    def dependencies(self) -> List[str]:
        """List of required module names."""
        return []  # No dependencies - this is a foundational module
    
    @property
    def release_status(self) -> str:
        """Release status: 'preview' for beta features."""
        return "preview"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the module with configuration.
        
        Args:
            config: Configuration dictionary containing module settings
        """
        # Operation mode configuration
        self.show_config = config.get("show_config", False)
        self.interactive_setup = config.get("interactive_setup", True)
        self.verbose = config.get("verbose", False)
        self.auto_create_config = config.get("auto_create_config", False)
        
        # Directory configuration parameters
        self.repo_root = config.get("repo_root")
        self.include_dirs = config.get("include_dirs", [])
        self.exclude_dirs = config.get("exclude_dirs", [])
        self.config_location = config.get("config_location", "local")  # "local" or "home"
        
        # Feature enablement
        self.enable_preview = config.get("enable_preview", os.getenv("ADT_ENABLE_DIRECTORY_CONFIG", "false").lower() == "true")
        
        # Initialize statistics
        self.directories_processed = 0
        self.files_filtered = 0
        self.configs_created = 0
        self.configs_updated = 0
        self.warnings_generated = 0
        
        # Initialize manager
        self.manager = DirectoryConfigManager()
        
        if self.verbose:
            print(f"Initialized DirectoryConfig v{self.version}")
            print(f"  Show config: {self.show_config}")
            print(f"  Interactive setup: {self.interactive_setup}")
            print(f"  Auto create config: {self.auto_create_config}")
            print(f"  Preview enabled: {self.enable_preview}")
            print(f"  Repo root: {self.repo_root}")
            print(f"  Include dirs: {len(self.include_dirs)}")
            print(f"  Exclude dirs: {len(self.exclude_dirs)}")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the directory configuration processing.
        
        Args:
            context: Execution context containing parameters and results from dependencies
        
        Returns:
            Dictionary with execution results
        """
        try:
            # Check if preview feature is enabled
            if not self.enable_preview:
                error_msg = "Directory configuration is disabled. Enable with ADT_ENABLE_DIRECTORY_CONFIG=true"
                if self.verbose:
                    print(error_msg)
                return {
                    "module_name": self.name,
                    "version": self.version,
                    "error": error_msg,
                    "success": False,
                    "feature_enabled": False
                }
            
            # Reset statistics
            self.directories_processed = 0
            self.files_filtered = 0
            self.configs_created = 0
            self.configs_updated = 0
            self.warnings_generated = 0
            
            result = {
                "module_name": self.name,
                "version": self.version,
                "success": True,
                "feature_enabled": True
            }
            
            if self.show_config:
                # Show current configuration
                result.update(self._show_configuration())
            elif self.auto_create_config:
                # Automatically create configuration without user interaction
                result.update(self._auto_create_configuration())
            elif self.interactive_setup:
                # Run interactive setup
                result.update(self._run_interactive_setup())
            else:
                # Load and apply existing configuration
                result.update(self._load_and_apply_configuration(context))
            
            # Add statistics to result
            result.update({
                "directories_processed": self.directories_processed,
                "files_filtered": self.files_filtered,
                "configs_created": self.configs_created,
                "configs_updated": self.configs_updated,
                "warnings_generated": self.warnings_generated
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Error in DirectoryConfig module: {e}"
            if self.verbose:
                print(error_msg)
            return {
                "module_name": self.name,
                "version": self.version,
                "error": str(e),
                "success": False,
                "directories_processed": self.directories_processed,
                "files_filtered": self.files_filtered,
                "configs_created": self.configs_created,
                "configs_updated": self.configs_updated,
                "warnings_generated": self.warnings_generated
            }
    
    def _show_configuration(self) -> Dict[str, Any]:
        """Show current directory configuration."""
        try:
            self.manager.show_current_config()
            return {
                "operation": "show_config",
                "config_displayed": True
            }
        except Exception as e:
            self.warnings_generated += 1
            return {
                "operation": "show_config",
                "config_displayed": False,
                "error": str(e)
            }
    
    def _auto_create_configuration(self) -> Dict[str, Any]:
        """Automatically create configuration without user interaction."""
        try:
            # Use provided parameters or defaults
            repo_root = self.repo_root or os.getcwd()
            
            # Create configuration
            config = self.manager.create_default_config(repo_root)
            config = self.manager.core.update_config_paths(config, self.include_dirs, self.exclude_dirs)
            
            # Determine config path
            config_path = "./.adtconfig.json" if self.config_location == "local" else "~/.adtconfig.json"
            
            # Save configuration
            if save_config_file(config_path, config):
                self.configs_created += 1
                if self.verbose:
                    print(f"✓ Configuration created at {config_path}")
                return {
                    "operation": "auto_create_config",
                    "config_created": True,
                    "config_path": config_path,
                    "repo_root": repo_root,
                    "include_dirs": len(self.include_dirs),
                    "exclude_dirs": len(self.exclude_dirs)
                }
            else:
                self.warnings_generated += 1
                return {
                    "operation": "auto_create_config",
                    "config_created": False,
                    "error": "Failed to save configuration"
                }
                
        except Exception as e:
            self.warnings_generated += 1
            return {
                "operation": "auto_create_config",
                "config_created": False,
                "error": str(e)
            }
    
    def _run_interactive_setup(self) -> Dict[str, Any]:
        """Run interactive setup wizard."""
        try:
            success = self.manager.interactive_setup()
            if success:
                self.configs_created += 1
                return {
                    "operation": "interactive_setup",
                    "setup_completed": True
                }
            else:
                self.warnings_generated += 1
                return {
                    "operation": "interactive_setup",
                    "setup_completed": False,
                    "error": "Interactive setup failed or was cancelled"
                }
        except Exception as e:
            self.warnings_generated += 1
            return {
                "operation": "interactive_setup",
                "setup_completed": False,
                "error": str(e)
            }
    
    def _load_and_apply_configuration(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Load and apply existing configuration to context."""
        try:
            config = load_directory_config()
            
            if config:
                # Apply directory filters to context
                directory = context.get("directory", ".")
                filtered_dirs = apply_directory_filters(directory, config)
                
                self.directories_processed = len(filtered_dirs)
                
                # If recursive processing is enabled, get filtered files
                if context.get("recursive", False):
                    filtered_files = get_filtered_adoc_files(directory, config)
                    self.files_filtered = len(filtered_files)
                
                if self.verbose:
                    print(f"Applied directory configuration:")
                    print(f"  Directories processed: {self.directories_processed}")
                    print(f"  Files filtered: {self.files_filtered}")
                    print(f"  Include dirs: {len(config.get('includeDirs', []))}")
                    print(f"  Exclude dirs: {len(config.get('excludeDirs', []))}")
                
                return {
                    "operation": "apply_config",
                    "config_applied": True,
                    "config_found": True,
                    "filtered_directories": filtered_dirs,
                    "repo_root": config.get("repoRoot"),
                    "include_dirs": len(config.get("includeDirs", [])),
                    "exclude_dirs": len(config.get("excludeDirs", []))
                }
            else:
                if self.verbose:
                    print("No directory configuration found")
                return {
                    "operation": "apply_config",
                    "config_applied": False,
                    "config_found": False,
                    "message": "No directory configuration found"
                }
                
        except Exception as e:
            self.warnings_generated += 1
            return {
                "operation": "apply_config",
                "config_applied": False,
                "error": str(e)
            }
    
    def cleanup(self) -> None:
        """Clean up module resources."""
        if self.verbose:
            print(f"DirectoryConfig cleanup complete")
            print(f"  Total directories processed: {self.directories_processed}")
            print(f"  Total files filtered: {self.files_filtered}")
            print(f"  Total configs created: {self.configs_created}")
            print(f"  Total configs updated: {self.configs_updated}")
            print(f"  Total warnings generated: {self.warnings_generated}")
            print(f"  Preview feature enabled: {self.enable_preview}")


# Helper functions for path handling
def _normalize_path(path: str, base_path: Optional[str] = None) -> str:
    """
    Normalize and resolve a path relative to base_path.

    Args:
        path: The path to normalize
        base_path: Optional base path to resolve relative paths against

    Returns:
        Normalized absolute path
    """
    if not path:
        raise ValueError("Path cannot be empty")

    # Expand user home directory
    expanded_path = os.path.expanduser(path)

    # If base_path is provided and path is relative, join them
    if base_path and not os.path.isabs(expanded_path):
        expanded_path = os.path.join(base_path, expanded_path)

    # Return normalized absolute path
    return os.path.abspath(expanded_path)


def _is_path_under_directory(file_path: str, dir_path: str) -> bool:
    """
    Check if file_path is under dir_path.

    Args:
        file_path: Path to check
        dir_path: Directory path to check against

    Returns:
        True if file_path is under dir_path, False otherwise
    """
    try:
        # Normalize both paths
        normalized_file = _normalize_path(file_path)
        normalized_dir = _normalize_path(dir_path)

        # Check if they share a common path and the directory is the parent
        common_path = os.path.commonpath([normalized_file, normalized_dir])
        return common_path == normalized_dir
    except (ValueError, OSError) as e:
        logger.debug(f"Error checking path relationship between {file_path} and {dir_path}: {e}")
        return False


def _validate_path_list(paths: List[str], base_path: str, description: str) -> List[str]:
    """
    Validate and normalize a list of paths.

    Args:
        paths: List of paths to validate
        base_path: Base path for relative path resolution
        description: Description for logging purposes

    Returns:
        List of validated and normalized paths
    """
    validated_paths = []

    for path in paths:
        try:
            normalized = _normalize_path(path, base_path)
            validated_paths.append(os.path.relpath(normalized, base_path))
            logger.debug(f"Validated {description} path: {path} -> {validated_paths[-1]}")
        except (ValueError, OSError) as e:
            logger.warning(f"Invalid {description} path '{path}': {e}")
            continue

    return validated_paths


def _detect_path_conflicts(include_dirs: List[str], exclude_dirs: List[str],
                           repo_root: str) -> List[str]:
    """
    Detect conflicts between include and exclude directories.

    Args:
        include_dirs: List of include directory paths
        exclude_dirs: List of exclude directory paths
        repo_root: Repository root path

    Returns:
        List of conflict messages
    """
    conflicts = []

    # Check for overlapping include/exclude directories
    for include_dir in include_dirs:
        include_path = _normalize_path(include_dir, repo_root)

        for exclude_dir in exclude_dirs:
            exclude_path = _normalize_path(exclude_dir, repo_root)

            # Check if include directory is under exclude directory
            if _is_path_under_directory(include_path, exclude_path):
                conflicts.append(f"Include directory '{include_dir}' is under exclude directory '{exclude_dir}'")

            # Check if exclude directory is under include directory
            elif _is_path_under_directory(exclude_path, include_path):
                conflicts.append(f"Exclude directory '{exclude_dir}' is under include directory '{include_dir}'")

    # Check for duplicate paths in same list
    include_set = set(include_dirs)
    if len(include_set) != len(include_dirs):
        conflicts.append("Duplicate paths found in include directories")

    exclude_set = set(exclude_dirs)
    if len(exclude_set) != len(exclude_dirs):
        conflicts.append("Duplicate paths found in exclude directories")

    return conflicts


class DirectoryConfigCore:
    """Core business logic for directory configuration (separated from user interaction)."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def create_default_config(self, repo_root: Optional[str] = None) -> dict:
        """Create a default configuration structure."""
        if repo_root is None:
            repo_root = os.getcwd()

        normalized_repo_root = _normalize_path(repo_root)

        config = {
            "version": CONFIG_VERSION,
            "repoRoot": normalized_repo_root,
            "includeDirs": [],
            "excludeDirs": [],
            "lastUpdated": datetime.now().isoformat()
        }

        self.logger.debug(f"Created default config with repo root: {normalized_repo_root}")

        # Validate schema
        if not self._validate_config_schema(config):
            raise ValueError("Invalid configuration schema")

        return config

    def _validate_config_schema(self, config: dict) -> bool:
        """Validate configuration schema structure."""
        required_fields = ["version", "repoRoot", "includeDirs", "excludeDirs", "lastUpdated"]

        if not isinstance(config, dict):
            self.logger.error("Configuration must be a dictionary")
            return False

        for field in required_fields:
            if field not in config:
                self.logger.error(f"Missing required field: {field}")
                return False

        # Type validation
        if not isinstance(config["includeDirs"], list):
            self.logger.error("includeDirs must be a list")
            return False
        if not isinstance(config["excludeDirs"], list):
            self.logger.error("excludeDirs must be a list")
            return False

        # Check for conflicts
        conflicts = _detect_path_conflicts(
            config["includeDirs"],
            config["excludeDirs"],
            config["repoRoot"]
        )

        if conflicts:
            self.logger.warning(f"Configuration conflicts detected: {'; '.join(conflicts)}")
            # Don't fail validation, just warn

        self.logger.debug("Configuration schema validation passed")
        return True

    def validate_directory(self, directory_path: str, base_path: str) -> Tuple[bool, str]:
        """Validate that a directory exists and is within the repository root."""
        try:
            normalized_path = _normalize_path(directory_path, base_path)
            self.logger.debug(f"Validating directory: {directory_path} -> {normalized_path}")

            result = validate_directory_path(normalized_path, base_path, require_exists=True)

            if result[0]:
                self.logger.debug(f"Directory validation successful: {directory_path}")
            else:
                self.logger.debug(f"Directory validation failed: {directory_path} - {result[1]}")

            return result
        except Exception as e:
            error_msg = f"Error validating directory '{directory_path}': {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def update_config_paths(self, config: dict, include_dirs: List[str],
                            exclude_dirs: List[str]) -> dict:
        """Update configuration with validated paths."""
        repo_root = config["repoRoot"]

        # Validate and normalize paths
        validated_includes = _validate_path_list(include_dirs, repo_root, "include")
        validated_excludes = _validate_path_list(exclude_dirs, repo_root, "exclude")

        # Update configuration
        config["includeDirs"] = validated_includes
        config["excludeDirs"] = validated_excludes
        config["lastUpdated"] = datetime.now().isoformat()

        # Check for conflicts
        conflicts = _detect_path_conflicts(validated_includes, validated_excludes, repo_root)
        if conflicts:
            self.logger.warning(f"Configuration conflicts: {'; '.join(conflicts)}")

        self.logger.info(f"Updated configuration with {len(validated_includes)} include dirs, "
                         f"{len(validated_excludes)} exclude dirs")

        return config


class DirectoryConfigUI:
    """User interface layer for directory configuration."""

    def __init__(self, core: DirectoryConfigCore):
        self.core = core
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def prompt_for_repository_root(self) -> str:
        """Prompt user for repository root directory."""
        current_dir = os.getcwd()
        print("\nRepository Root Configuration")
        print(f"Current directory: {current_dir}")

        try:
            while True:
                repo_root = input(f"Enter repository root path [{current_dir}]: ").strip()
                if not repo_root:
                    repo_root = current_dir

                if repo_root.lower() in ['quit', 'exit', 'q']:
                    print("Setup cancelled by user.")
                    sys.exit(0)

                try:
                    normalized_root = _normalize_path(repo_root)

                    if os.path.exists(normalized_root) and os.path.isdir(normalized_root):
                        self.logger.debug(f"Repository root selected: {normalized_root}")
                        return normalized_root
                    else:
                        print(f"Error: Directory does not exist: {normalized_root}")
                        self.logger.debug(f"Invalid repository root: {normalized_root}")
                except Exception as e:
                    print(f"Error: Invalid path: {e}")
                    self.logger.debug(f"Path normalization error: {e}")
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user (Ctrl+C).")
            sys.exit(0)

    def prompt_for_directories(self, prompt_text: str, repo_root: str,
                               existing_dirs: Optional[List[str]] = None) -> List[str]:
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
                is_valid, result = self.core.validate_directory(dir_input, repo_root)
                if is_valid:
                    # Convert to relative path for storage
                    rel_path = os.path.relpath(result, repo_root)
                    if rel_path not in directories:
                        directories.append(rel_path)
                        print(f"  ✓ Added: {rel_path}")
                        self.logger.debug(f"Added directory: {rel_path}")
                    else:
                        print(f"  ! Already added: {rel_path}")
                        self.logger.debug(f"Duplicate directory ignored: {rel_path}")
                else:
                    print(f"  ✗ {result}")
                    self.logger.debug(f"Invalid directory rejected: {dir_input} - {result}")
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user (Ctrl+C).")
            sys.exit(0)

        return directories

    def display_configuration(self, config: dict, config_path: Optional[str] = None) -> None:
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
            print("\nInclude directories: All directories (no restrictions)")

        if config['excludeDirs']:
            print(f"\nExclude directories ({len(config['excludeDirs'])}):")
            for dir_name in config['excludeDirs']:
                print(f"  - {dir_name}")
        else:
            print("\nExclude directories: None")

        print("="*50)

    def _prompt_for_save_location(self) -> str:
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

    def _save_config_with_retry(self, config_path: str, config: dict,
                                max_retries: int = 3) -> bool:
        """Save configuration with retry logic."""
        for attempt in range(max_retries):
            try:
                if save_config_file(config_path, config):
                    print(f"\n✓ Configuration saved to {config_path}")
                    self.display_configuration(config, config_path)
                    self.logger.info(f"Configuration saved successfully to {config_path}")
                    return True
                else:
                    if attempt < max_retries - 1:
                        print(f"\n✗ Failed to save configuration to {config_path}")
                        self.logger.warning(f"Failed to save configuration to {config_path}, attempt {attempt + 1}")
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
                        self.logger.error(f"Failed to save configuration after {max_retries} attempts")
            except Exception as e:
                self.logger.error(f"Error saving configuration: {e}")
                if attempt == max_retries - 1:
                    print(f"\n✗ Error saving configuration: {e}")
                    return False

        return False


class DirectoryConfigManager:
    """Manages directory configuration for AsciiDoc processing."""

    def __init__(self):
        self.core = DirectoryConfigCore()
        self.ui = DirectoryConfigUI(self.core)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def create_default_config(self, repo_root: Optional[str] = None) -> dict:
        """Create a default configuration structure."""
        return self.core.create_default_config(repo_root)

    def validate_directory(self, directory_path: str, base_path: str) -> Tuple[bool, str]:
        """Validate that a directory exists and is within the repository root."""
        return self.core.validate_directory(directory_path, base_path)

    def interactive_setup(self) -> bool:
        """Run interactive setup wizard for directory configuration."""
        try:
            print("ADT Directory Configuration Setup")
            print("=" * 40)

            # Step 1: Repository root
            repo_root = self.ui.prompt_for_repository_root()

            # Step 2: Include directories
            include_dirs = self.ui.prompt_for_directories(
                "Include Directories (leave empty to include all)",
                repo_root
            )

            # Step 3: Exclude directories
            exclude_dirs = self.ui.prompt_for_directories(
                "Exclude Directories (leave empty to exclude none)",
                repo_root
            )

            # Step 4: Create and update configuration
            config = self.core.create_default_config(repo_root)
            config = self.core.update_config_paths(config, include_dirs, exclude_dirs)

            # Step 5: Choose where to save
            config_path = self.ui._prompt_for_save_location()

            # Step 6: Save configuration with retry
            success = self.ui._save_config_with_retry(config_path, config)

            if success:
                self.logger.info("Interactive setup completed successfully")
            else:
                self.logger.error("Interactive setup failed")

            return success

        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user (Ctrl+C).")
            self.logger.info("Setup cancelled by user")
            return False
        except Exception as e:
            print(f"\nUnexpected error during setup: {e}")
            self.logger.error(f"Unexpected error during setup: {e}")
            return False

    def show_current_config(self) -> None:
        """Display the current active configuration."""
        self.logger.debug("Showing current configuration")

        # Check for local config first
        local_config = load_config_file("./.adtconfig.json")
        home_config = load_config_file("~/.adtconfig.json")

        if local_config and home_config:
            print("Multiple configuration files found:")
            print("\nLocal configuration (./.adtconfig.json):")
            self.ui.display_configuration(local_config, "./.adtconfig.json")
            print("\nHome configuration (~/.adtconfig.json):")
            self.ui.display_configuration(home_config, "~/.adtconfig.json")
            print("\nNote: Local configuration takes precedence when both exist.")
            self.logger.debug("Displayed multiple configurations")
        elif local_config:
            self.ui.display_configuration(local_config, "./.adtconfig.json")
            self.logger.debug("Displayed local configuration")
        elif home_config:
            self.ui.display_configuration(home_config, "~/.adtconfig.json")
            self.logger.debug("Displayed home configuration")
        else:
            print("No directory configuration found.")
            print("Run 'adt DirectoryConfig' to create a configuration.")
            self.logger.debug("No configuration found")


# Modular compatibility functions for the new architecture

def load_directory_config() -> Optional[dict]:
    """
    Load directory configuration from the local or home config file.

    Returns:
        dict or None: Configuration dictionary if found, None otherwise.
    """
    logger.debug("Loading directory configuration")

    # Check for local config first
    local_config = load_config_file("./.adtconfig.json")
    if local_config:
        logger.debug("Loaded local configuration")
        return local_config

    # Fallback to home config
    home_config = load_config_file("~/.adtconfig.json")
    if home_config:
        logger.debug("Loaded home configuration")
        return home_config

    logger.debug("No configuration found")
    return None


def apply_directory_filters(base_path: str, config: Optional[dict]) -> List[str]:
    """
    Apply directory filters based on configuration.

    Args:
        base_path: The base directory path to filter
        config: Directory configuration

    Returns:
        List of filtered directory paths
    """
    logger.debug(f"Applying directory filters to {base_path}")

    if not config:
        logger.debug("No configuration provided, returning base path")
        return [base_path]

    try:
        repo_root = config.get("repoRoot", os.getcwd())
        include_dirs = config.get("includeDirs", [])
        exclude_dirs = config.get("excludeDirs", [])

        # Normalize paths
        normalized_base = _normalize_path(base_path)
        normalized_repo = _normalize_path(repo_root)

        logger.debug(f"Filtering: base={normalized_base}, repo={normalized_repo}, "
                     f"includes={len(include_dirs)}, excludes={len(exclude_dirs)}")

        # Check if base_path is excluded
        for exclude_dir in exclude_dirs:
            exclude_path = _normalize_path(exclude_dir, normalized_repo)

            if _is_path_under_directory(normalized_base, exclude_path):
                logger.warning(f"Directory {normalized_base} is excluded by configuration")
                # Still return the path since there's no alternative
                return [normalized_base]

        # If include dirs are specified, filter based on them
        if include_dirs:
            filtered_dirs = []
            for include_dir in include_dirs:
                include_path = _normalize_path(include_dir, normalized_repo)

                # Check if base_path is in or under an included directory
                if (_is_path_under_directory(normalized_base, include_path) or
                        _is_path_under_directory(include_path, normalized_base)):
                    filtered_dirs.append(include_path)
                    logger.debug(f"Directory {include_path} matches include filter")

            result = filtered_dirs if filtered_dirs else [normalized_base]
            logger.debug(f"Include filtering resulted in {len(result)} directories")
            return result

        # No include filters, just return the base path (exclude filters already checked)
        logger.debug("No include filters, returning base path")
        return [normalized_base]

    except Exception as e:
        logger.error(f"Error applying directory filters: {e}")
        # Fallback to normalized base path
        return [_normalize_path(base_path)]


def get_filtered_adoc_files(directory_path: str, config: Optional[dict],
                            find_adoc_files_func: Optional[callable] = None) -> List[str]:
    """
    Get filtered AsciiDoc files based on directory configuration.

    Args:
        directory_path: The directory to search
        config: Directory configuration
        find_adoc_files_func: Function to find adoc files (optional)

    Returns:
        List of filtered .adoc file paths
    """
    logger.debug(f"Getting filtered adoc files from {directory_path}")

    if find_adoc_files_func is None:
        from ..file_utils import find_adoc_files
        find_adoc_files_func = find_adoc_files

    if not config:
        logger.debug("No configuration provided, finding all adoc files")
        return find_adoc_files_func(directory_path, recursive=True)

    try:
        repo_root = config.get("repoRoot", os.getcwd())
        include_dirs = config.get("includeDirs", [])
        exclude_dirs = config.get("excludeDirs", [])

        normalized_repo = _normalize_path(repo_root)

        logger.debug(f"Filtering files: repo={normalized_repo}, "
                     f"includes={len(include_dirs)}, excludes={len(exclude_dirs)}")

        all_files = []

        # If include dirs are specified, only process those
        if include_dirs:
            for include_dir in include_dirs:
                include_path = _normalize_path(include_dir, normalized_repo)

                if os.path.exists(include_path) and os.path.isdir(include_path):
                    files = find_adoc_files_func(include_path, recursive=True)
                    all_files.extend(files)
                    logger.debug(f"Found {len(files)} files in include directory {include_path}")
        else:
            # Process all files in the directory path
            all_files = find_adoc_files_func(directory_path, recursive=True)
            logger.debug(f"Found {len(all_files)} files in directory {directory_path}")

        # Filter out excluded directories
        if exclude_dirs:
            filtered_files = []
            for file_path in all_files:
                excluded = False
                normalized_file = _normalize_path(file_path)

                for exclude_dir in exclude_dirs:
                    exclude_path = _normalize_path(exclude_dir, normalized_repo)

                    if _is_path_under_directory(normalized_file, exclude_path):
                        excluded = True
                        logger.debug(f"File {file_path} excluded by directory {exclude_dir}")
                        break

                if not excluded:
                    filtered_files.append(file_path)

            logger.debug(f"Exclusion filtering resulted in {len(filtered_files)} files")
            return filtered_files

        logger.debug(f"No exclusion filtering, returning {len(all_files)} files")
        return all_files

    except Exception as e:
        logger.error(f"Error filtering adoc files: {e}")
        # Fallback to basic file finding
        return find_adoc_files_func(directory_path, recursive=True)


def run_directory_config(args):
    """Legacy main function for backward compatibility."""
    if ADT_MODULE_AVAILABLE:
        # Use the new ADTModule implementation
        module = DirectoryConfigModule()
        
        # Initialize with configuration from args
        config = {
            "show_config": getattr(args, "show", False),
            "interactive_setup": not getattr(args, "show", False),
            "verbose": getattr(args, "verbose", False),
            "auto_create_config": False,
            "enable_preview": os.getenv("ADT_ENABLE_DIRECTORY_CONFIG", "false").lower() == "true"
        }
        
        module.initialize(config)
        
        # Execute with context
        context = {
            "directory": ".",
            "recursive": False
        }
        
        result = module.execute(context)
        
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

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.set_defaults(func=run_directory_config)
