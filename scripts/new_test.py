#!/usr/bin/env python3
"""
Script to create new test files in the correct location with proper template.
Usage: python3 scripts/new_test.py <test_name> [plugin_name]
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

TEST_TEMPLATE = '''#!/usr/bin/env python3
"""
Test suite for {module_name}.
Created: {date}
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the module under test
# from asciidoc_dita_toolkit.asciidoc_dita.plugins.{module_name} import {class_name}


class Test{class_name}:
    """Test cases for {class_name} functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up after each test method."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test that the class initializes correctly."""
        # TODO: Implement initialization test
        assert True  # Placeholder
        
    def test_basic_functionality(self):
        """Test basic functionality."""
        # TODO: Implement basic functionality test
        assert True  # Placeholder


class Test{class_name}Integration:
    """Integration test cases for {class_name}."""
    
    def setup_method(self):
        """Set up test fixtures for integration tests."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up after integration tests."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    @pytest.mark.integration
    def test_end_to_end_workflow(self):
        """Test complete workflow integration."""
        # TODO: Implement integration test
        assert True  # Placeholder


if __name__ == '__main__':
    pytest.main([__file__])
'''

def create_test_file(test_name: str, plugin_name: str = None):
    """Create a new test file with proper template."""
    
    # Determine paths
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / "tests"
    
    # Ensure tests directory exists
    tests_dir.mkdir(exist_ok=True)
    
    # Generate file name
    if not test_name.startswith("test_"):
        test_name = f"test_{test_name}"
    if not test_name.endswith(".py"):
        test_name = f"{test_name}.py"
    
    test_file = tests_dir / test_name
    
    # Check if file already exists
    if test_file.exists():
        print(f"❌ Test file already exists: {test_file}")
        return False
    
    # Determine module and class names
    if plugin_name:
        module_name = plugin_name
        class_name = plugin_name
    else:
        # Extract from test name (test_module_name.py -> ModuleName)
        base_name = test_name.replace("test_", "").replace(".py", "")
        class_name = "".join(word.capitalize() for word in base_name.split("_"))
        module_name = base_name
    
    # Generate content from template
    content = TEST_TEMPLATE.format(
        module_name=module_name,
        class_name=class_name,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    # Write the file
    test_file.write_text(content)
    
    print(f"✅ Created test file: {test_file}")
    print(f"📝 Module: {module_name}")
    print(f"🏗️  Class: {class_name}")
    print()
    print("Next steps:")
    print(f"1. Edit {test_file}")
    print("2. Import the module under test")
    print("3. Implement actual test cases")
    print("4. Run: pytest tests/{test_name}")
    
    return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create new test files in the correct location"
    )
    parser.add_argument(
        "test_name", 
        help="Name of the test (will be prefixed with test_ if needed)"
    )
    parser.add_argument(
        "--plugin", "-p",
        help="Plugin name (for proper imports and class names)"
    )
    
    args = parser.parse_args()
    
    success = create_test_file(args.test_name, args.plugin)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
