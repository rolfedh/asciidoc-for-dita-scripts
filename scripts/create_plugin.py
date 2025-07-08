#!/usr/bin/env python3
"""
Plugin Template Generator for AsciiDoc DITA Toolkit

This script generates boilerplate code for new plugins following the established pattern.
Usage: python scripts/create_plugin.py PluginName "Description"
"""

import argparse
import os
import sys
from pathlib import Path


def create_plugin_template(plugin_name, description):
    """Create a new plugin template with all necessary files."""
    
    # Validate plugin name
    if not plugin_name.isidentifier():
        raise ValueError(f"Plugin name '{plugin_name}' is not a valid Python identifier")
    
    # Define paths
    project_root = Path(__file__).parent.parent
    plugin_dir = project_root / "asciidoc_dita_toolkit" / "asciidoc_dita" / "plugins"
    test_dir = project_root / "tests"
    fixture_dir = test_dir / "fixtures" / plugin_name
    
    # Create plugin file
    plugin_file = plugin_dir / f"{plugin_name}.py"
    if plugin_file.exists():
        raise FileExistsError(f"Plugin file already exists: {plugin_file}")
    
    plugin_content = f'''"""
Plugin for the AsciiDoc DITA toolkit: {plugin_name}

{description}

See: 
- https://github.com/jhradilek/asciidoctor-dita-vale/blob/main/styles/AsciiDocDITA/{plugin_name}.yml
- https://github.com/jhradilek/asciidoctor-dita-vale/tree/main/fixtures/{plugin_name}
"""

__description__ = "{description}"

import re
from ..file_utils import (common_arg_parser, process_adoc_files,
                          read_text_preserve_endings,
                          write_text_preserve_endings)

# TODO: Define transformation patterns and constants
TRANSFORMATION_PATTERN = re.compile(r"pattern_to_match")

# TODO: Define mappings if needed
MAPPING_DICT = {{
    "example_key": "example_value",
    # Add more mappings as needed
}}


def transform_line(line):
    """
    Apply transformation to a single line.
    
    Args:
        line: Input line to process
        
    Returns:
        Transformed line
    """
    # TODO: Implement line transformation logic
    # For simple line-by-line transformations
    return line


def process_file(filepath):
    """
    Process a single .adoc file with full context.
    Use this for transformations that require state tracking across lines.
    
    Args:
        filepath: Path to the file to process
    """
    try:
        lines = read_text_preserve_endings(filepath)
        new_lines = []
        
        # TODO: Add state variables for complex transformations
        in_special_block = False
        
        for text, ending in lines:
            stripped = text.strip()
            
            # TODO: Implement state tracking logic
            # Example: tracking comments, blocks, etc.
            if stripped.startswith("//"):
                # Skip comments
                new_lines.append((text, ending))
                continue
            
            # TODO: Apply transformation logic
            # Choose between transform_line() for simple cases
            # or custom logic for complex state-dependent transformations
            transformed_text = transform_line(text)
            new_lines.append((transformed_text, ending))

        write_text_preserve_endings(filepath, new_lines)
        print(f"Processed {{filepath}} (preserved per-line endings)")
    except Exception as e:
        print(f"Error processing {{filepath}}: {{e}}")


def main(args):
    """Main function for the {plugin_name} plugin."""
    process_adoc_files(args, process_file)


def register_subcommand(subparsers):
    """Register this plugin as a subcommand."""
    parser = subparsers.add_parser("{plugin_name}", help=__description__)
    common_arg_parser(parser)
    parser.set_defaults(func=main)
'''
    
    # Create test file
    test_file = test_dir / f"test_{plugin_name}.py"
    if test_file.exists():
        raise FileExistsError(f"Test file already exists: {test_file}")
    
    test_content = f'''"""
Test suite for the {plugin_name} plugin.

This script tests the transformation logic using fixtures from
tests/fixtures/{plugin_name}/.

For each .adoc file, it expects a corresponding .expected file in the same directory.
"""

import os
import sys
import unittest

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from asciidoc_dita_toolkit.asciidoc_dita.plugins.{plugin_name} import transform_line, process_file
from tests.asciidoc_testkit import run_linewise_test, get_same_dir_fixture_pairs, run_file_based_test

FIXTURE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures', '{plugin_name}'))


class Test{plugin_name}(unittest.TestCase):
    
    def test_basic_functionality(self):
        """Test basic transformation functionality."""
        # TODO: Add specific test cases
        input_text = "example input"
        expected = "example input"  # TODO: Update with expected output
        result = transform_line(input_text)
        self.assertEqual(result, expected)
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        # TODO: Add edge case tests
        pass
    
    def test_fixture_based_tests(self):
        """Run tests based on fixture files if they exist."""
        if os.path.exists(FIXTURE_DIR):
            fixture_count = 0
            for input_path, expected_path in get_same_dir_fixture_pairs(FIXTURE_DIR):
                fixture_count += 1
                with self.subTest(fixture=os.path.basename(input_path)):
                    fixture_name = os.path.basename(input_path)
                    
                    # TODO: Choose appropriate test method
                    # Use run_linewise_test for simple transformations
                    # Use run_file_based_test for state-dependent transformations
                    success = run_linewise_test(input_path, expected_path, transform_line)
                    self.assertTrue(success, f"Fixture test failed for {{input_path}}")
            
            if fixture_count > 0:
                print(f"Ran {{fixture_count}} fixture-based tests")
        else:
            self.skipTest(f"Fixture directory not found: {{FIXTURE_DIR}}")


if __name__ == '__main__':
    unittest.main()
'''
    
    # Create directories
    plugin_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)
    fixture_dir.mkdir(parents=True, exist_ok=True)
    
    # Write plugin file
    with open(plugin_file, 'w', encoding='utf-8') as f:
        f.write(plugin_content)
    
    # Write test file
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # Create vale.ini if fixtures exist
    vale_ini = fixture_dir / "vale.ini"
    if not vale_ini.exists():
        vale_content = f"""[*]
BasedOnStyles = AsciiDocDITA
AsciiDocDITA.{plugin_name} = YES

[*.adoc]
AsciiDocDITA.{plugin_name} = YES
"""
        with open(vale_ini, 'w', encoding='utf-8') as f:
            f.write(vale_content)
    
    print(f"✅ Created plugin template for {plugin_name}")
    print(f"📁 Plugin file: {plugin_file}")
    print(f"🧪 Test file: {test_file}")
    print(f"📋 Fixture directory: {fixture_dir}")
    print(f"")
    print(f"Next steps:")
    print(f"1. Analyze fixtures in {fixture_dir}")
    print(f"2. Implement transformation logic in {plugin_file}")
    print(f"3. Update test cases in {test_file}")
    print(f"4. Run tests: python -m pytest {test_file}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Generate plugin template")
    parser.add_argument("plugin_name", help="Name of the plugin (e.g., AttributeReference)")
    parser.add_argument("description", help="Brief description of the plugin")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    
    args = parser.parse_args()
    
    try:
        create_plugin_template(args.plugin_name, args.description)
    except (ValueError, FileExistsError) as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()