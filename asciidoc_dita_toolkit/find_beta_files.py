#!/usr/bin/env python3
"""
Helper script to locate beta testing files for asciidoc-dita-toolkit
"""
import os
import sys
import argparse

def find_beta_test_files():
    """Find the beta testing files in the installed package."""
    try:
        # Look in the package's beta_testing_files directory
        import asciidoc_dita_toolkit.beta_testing_files
        beta_testing_path = os.path.dirname(asciidoc_dita_toolkit.beta_testing_files.__file__)
        
        if os.path.exists(beta_testing_path) and os.listdir(beta_testing_path):
            return beta_testing_path
            
        # Fallback: look in the package directory
        import asciidoc_dita_toolkit
        package_dir = os.path.dirname(asciidoc_dita_toolkit.__file__)
        beta_testing_path = os.path.join(package_dir, 'beta_testing_files')
        
        if os.path.exists(beta_testing_path) and os.listdir(beta_testing_path):
            return beta_testing_path
            
        return None
        
    except Exception as e:
        if not hasattr(sys, '_called_from_test'):
            print(f"Error finding beta test files: {e}")
        return None

def main():
    """Main function to find and display beta test files location."""
    parser = argparse.ArgumentParser(description="Find beta testing files location")
    parser.add_argument(
        "--path-only", 
        action="store_true", 
        help="Output only the path, suitable for use in scripts"
    )
    args = parser.parse_args()
    
    beta_path = find_beta_test_files()
    
    if not beta_path:
        if args.path_only:
            sys.exit(1)
        else:
            print("Beta testing files not found.")
            print("You can download them from:")
            print("https://github.com/rolfedh/asciidoc-dita-toolkit/tree/main/beta-testing")
            sys.exit(1)
    
    if args.path_only:
        print(beta_path)
    else:
        print(f"Beta testing files found at: {beta_path}")
        print("\nAvailable test files:")
        for file in os.listdir(beta_path):
            if file.endswith('.adoc'):
                print(f"  - {file}")
        print(f"\nTo use these files, copy them to your working directory:")
        print(f"cp {beta_path}/*.adoc .")

if __name__ == "__main__":
    main()
