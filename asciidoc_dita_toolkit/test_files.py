"""
Utility functions for accessing beta testing files included with the package.
"""

import os
import sys
import shutil
from pathlib import Path


def get_test_files_directory():
    """
    Get the path to the included test files directory.
    
    Returns:
        Path: Path to the test files directory
    """
    # Get the directory where this module is located
    package_dir = Path(__file__).parent
    test_files_dir = package_dir / "beta_testing_files"
    
    if not test_files_dir.exists():
        raise FileNotFoundError(
            f"Test files directory not found at {test_files_dir}. "
            "This may indicate an installation issue."
        )
    
    return test_files_dir


def copy_test_files_to_directory(destination_dir):
    """
    Copy all test files to a specified directory for testing.
    
    Args:
        destination_dir (str or Path): Directory to copy test files to
        
    Returns:
        Path: Path to the destination directory
    """
    dest_path = Path(destination_dir)
    dest_path.mkdir(parents=True, exist_ok=True)
    
    test_files_dir = get_test_files_directory()
    
    # Copy all files from test_files_dir to destination
    for file_path in test_files_dir.iterdir():
        if file_path.is_file():
            shutil.copy2(file_path, dest_path)
    
    print(f"✅ Copied {len(list(test_files_dir.glob('*')))} test files to {dest_path}")
    return dest_path


def list_test_files():
    """
    List all available test files with descriptions.
    
    Returns:
        list: List of test file names
    """
    test_files_dir = get_test_files_directory()
    
    files = []
    for file_path in test_files_dir.iterdir():
        if file_path.is_file() and file_path.suffix == '.adoc':
            files.append(file_path.name)
    
    return sorted(files)


def main():
    """
    Command-line interface for test file utilities.
    """
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m asciidoc_dita_toolkit.test_files list")
        print("  python -m asciidoc_dita_toolkit.test_files copy <destination>")
        print("  python -m asciidoc_dita_toolkit.test_files path")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        print("Available test files:")
        for file_name in list_test_files():
            print(f"  {file_name}")
    
    elif command == "copy":
        if len(sys.argv) < 3:
            print("Error: destination directory required")
            print("Usage: python -m asciidoc_dita_toolkit.test_files copy <destination>")
            sys.exit(1)
        
        destination = sys.argv[2]
        copy_test_files_to_directory(destination)
    
    elif command == "path":
        test_files_dir = get_test_files_directory()
        print(f"Test files directory: {test_files_dir}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
