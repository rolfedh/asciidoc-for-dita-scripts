# Contributing to AsciiDoc DITA Toolkit

Thank you for your interest in contributing! This guide will help you get started, whether you're a technical writer who wants to create plugins or an experienced developer looking to enhance the toolkit.

## For Technical Writers (New to Coding)

If you're new to programming but want to create plugins to solve specific AsciiDoc problems:
- Start with the **Quick Start for Writers** section below
- Focus on the **Simple Plugin Example** 
- Don't worry about understanding every technical detail - the examples will get you started
- Ask questions in issues if you get stuck!

## Quick Start for Writers

**I want to create a plugin but I'm new to coding - where do I start?**

1. **Look at existing plugins** in `asciidoc_dita/plugins/` - they're your best learning resource
2. **Copy and modify** - start with an existing plugin and change it for your needs
3. **Test early and often** - run your plugin frequently to see if it works
4. **Start simple** - solve one small problem first, then expand

### What You Need on Your Computer

- **Python 3.7 or newer** (check with `python3 --version`)
- **A text editor** (VS Code, Sublime Text, or even Notepad work fine)
- **Basic command line comfort** (you'll need to run a few commands)

### Your First Plugin in 5 Steps

1. **Pick a problem** - What do you want to fix in your .adoc files?
2. **Copy an existing plugin** - Use `EntityReference.py` as a starting point
3. **Change the name and description** - Make it yours
4. **Modify the logic** - Change what the plugin actually does
5. **Test it** - Run it on a test file to see if it works

## Project Structure

The toolkit uses a clean, unified architecture:

- **`asciidoc_dita_toolkit/asciidoc_dita/`**: Main Python package
  - `cli.py`: Unified CLI interface with plugin subcommands
  - `file_utils.py`: Shared file and argument utilities
  - `plugins/`: Plugin directory with auto-discovery ← **Your plugins go here**
    - `EntityReference.py`: HTML entity reference fixer
    - `ContentType.py`: Content type label adder
    - `__init__.py`: Plugin initialization
- **`tests/`**: Automated tests and test fixtures
- **`docs/`**: Project documentation
- **`pyproject.toml`**: Packaging, metadata, and CLI entry point

## CLI Entry Point

The toolkit provides a single, clean entry point:

| Command | Description | Target |
|---------|-------------|--------|
| `asciidoc-dita` | Main unified CLI | `asciidoc_dita.cli:main` |

## Getting Started (Step by Step)

### For Technical Writers New to Development

1. **Fork and clone the repository**
   
   *What this means*: Create your own copy of the project that you can modify
   
   ```sh
   # Go to GitHub, click "Fork" on the project page, then:
   git clone https://github.com/<your-username>/asciidoc-dita-toolkit.git
   cd asciidoc-dita-toolkit
   ```

2. **Set up a virtual environment** *(optional but recommended)*
   
   *What this means*: Create an isolated space for this project so it doesn't interfere with other Python projects
   
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate  # On Linux/macOS
   # or .venv\Scripts\activate  # On Windows
   ```

3. **Install the toolkit in development mode**
   
   *What this means*: Install it so you can make changes and see them immediately
   
   ```sh
   # For basic installation:
   pip install -e .
   
   # For development with all tools (recommended):
   pip install -e ".[dev]"
   ```

4. **Test that everything works**
   ```sh
   asciidoc-dita --list-plugins
   asciidoc-dita --help
   
   # Optional: Run a quick demo
   make demo
   ```

### For Experienced Developers

The same steps apply, but you can also use the Makefile for common tasks:

```sh
make install-dev    # Install with development dependencies
make test          # Run tests
make lint          # Run code quality checks
make help          # See all available commands
```

## Creating New Plugins

### Simple Plugin Example (Start Here!)

**Copy this template and modify it for your needs:**

```python
"""
Plugin for the AsciiDoc DITA toolkit: FixMyProblem

This plugin fixes [describe your specific problem here].
For example: "This plugin removes extra spaces at the end of lines."
"""

import sys
import re
from ..file_utils import process_adoc_files

# What your plugin will be called in the CLI
__description__ = "Fix my specific AsciiDoc problem"
__version__ = "1.0.0"

def fix_my_content(content):
    """
    This is where you put your logic to fix the content.
    
    Args:
        content (str): The content of one .adoc file
        
    Returns:
        str: The fixed content
    """
    # Example: Remove trailing spaces
    # lines = content.split('\n')
    # fixed_lines = [line.rstrip() for line in lines]
    # return '\n'.join(fixed_lines)
    
    # Replace this with your own logic:
    return content  # This does nothing - replace with your fixes!

def main(args):
    """
    Main function - you usually don't need to change this much.
    """
    try:
        def process_file_content(content, filepath):
            return fix_my_content(content), True
        
        exit_code = process_adoc_files(args, process_file_content)
        return exit_code
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

def register_subcommand(subparsers):
    """
    Register this plugin as a CLI command - you can customize the arguments.
    """
    parser = subparsers.add_parser(
        "FixMyProblem",  # This becomes: asciidoc-dita FixMyProblem
        help=__description__
    )
    
    # Add command-line options (these are optional):
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Search subdirectories recursively')
    parser.add_argument('-f', '--file', help='Process only this specific .adoc file')
    parser.add_argument('--version', action='version', version=f'FixMyProblem {__version__}')
    
    # This line is required:
    parser.set_defaults(func=main)
```

### How to Customize Your Plugin

1. **Change the name**: Replace `FixMyProblem` with your plugin name (in 3 places)
2. **Update the description**: Explain what your plugin does
3. **Write your logic**: Replace the `fix_my_content` function with your own code
4. **Add arguments**: Modify the `register_subcommand` function if you need special options

### Complete Plugin Structure (For Reference)

Each plugin needs these parts:

1. **Documentation at the top** - Explains what the plugin does
2. **`main(args)` function** - The entry point that accepts command-line arguments
3. **`register_subcommand(subparsers)` function** - Registers your plugin as a CLI command
4. **Your custom logic** - The actual code that processes the files

Here's a more detailed template:

```python
"""
Plugin for the AsciiDoc DITA toolkit: MyPlugin

Brief description of what the plugin does.
"""

__description__ = "Brief description for CLI help"
__version__ = "1.0.0"

import sys

def main(args):
    """
    Main entry point for the plugin.
    
    Args:
        args: Parsed command line arguments (from argparse)
        
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    try:
        # Your plugin logic here
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

def register_subcommand(subparsers):
    """Register this plugin as a subcommand in the main CLI."""
    parser = subparsers.add_parser(
        "MyPlugin",
        help=__description__
    )
    # Add your arguments here
    parser.add_argument('--version', action='version', version=f'MyPlugin {__version__}')
    parser.set_defaults(func=main)
```

### Plugin Auto-Discovery (How It Works)

You don't need to register your plugin anywhere! Just:

1. **Save your plugin** in the `asciidoc_dita/plugins/` directory
2. **Name it something.py** (like `MyPlugin.py`)
3. **Run the toolkit** - it will automatically find your plugin

```sh
asciidoc-dita --list-plugins  # Your plugin will appear here
asciidoc-dita MyPlugin --help # Your plugin is available as a subcommand
```

## Testing Your Plugin

### Quick Testing (For Beginners)

1. **Create a test file**:
   ```sh
   echo "Some test content" > test.adoc
   ```

2. **Run your plugin on it**:
   ```sh
   asciidoc-dita YourPluginName -f test.adoc
   ```

3. **Check if it worked**:
   ```sh
   cat test.adoc  # See if the content changed as expected
   ```

### Formal Testing (Recommended)

Create a test file in `tests/` that follows this pattern:

```python
import unittest
import subprocess
import tempfile
import os

class TestYourPlugin(unittest.TestCase):
    def test_your_plugin_basic(self):
        """Test that your plugin does what it should."""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
            f.write("Your test content here")
            test_file = f.name
        
        try:
            # Run your plugin
            result = subprocess.run(['asciidoc-dita', 'YourPluginName', '-f', test_file], 
                                  capture_output=True, text=True)
            
            # Check it succeeded
            self.assertEqual(result.returncode, 0)
            
            # Check the content changed correctly
            with open(test_file, 'r') as f:
                content = f.read()
                self.assertIn("expected result", content)
        
        finally:
            # Clean up
            os.unlink(test_file)

if __name__ == '__main__':
    unittest.main()
```

### Running All Tests

- **Using pytest (recommended)**:
  ```sh
  python -m pytest tests/ -v
  ```

- **Using the Makefile**:
  ```sh
  make test           # Run all tests
  make test-coverage  # Run tests with coverage report
  ```

- **Run your specific test**:
  ```sh
  python -m pytest tests/test_your_plugin.py -v
  ```

## Getting Help

### Common Questions

**Q: I'm getting import errors when I run my plugin**
- Make sure you've run `pip install -e .` or `make install-dev` in the project directory
- Check that your plugin file is in the right location: `asciidoc_dita/plugins/`
- If using development tools, ensure you installed with `pip install -e ".[dev]"`

**Q: My plugin isn't showing up in `--list-plugins`**
- Check that your plugin file ends with `.py`
- Make sure it has both `main()` and `register_subcommand()` functions
- Look for error messages when you run `asciidoc-dita --list-plugins`

**Q: I don't understand the Python code**
- Start by copying an existing plugin and changing small parts
- Focus on the logic inside `fix_my_content()` or similar functions
- Ask questions in GitHub issues - we're happy to help!

**Q: How do I process multiple files?**
- Use the `-r` flag to process files recursively
- The `file_utils.py` module handles file processing for you

### Where to Ask for Help

- **GitHub Issues**: For bugs, feature requests, or technical questions
- **GitHub Discussions**: For general questions about plugin development
- **Look at existing plugins**: They're your best documentation

### Development Tools

The project includes several tools to help with development:

- **Makefile**: Common development tasks (`make help` to see all options)
- **Pre-commit hooks**: Automatic code formatting and quality checks
- **pytest**: Comprehensive testing with coverage reports
- **Code formatters**: Black, isort, and flake8 for consistent code style

## Contributing Your Plugin

When your plugin is working:

1. **Test it thoroughly** - Make sure it works on different types of files
2. **Write a simple test** - Even a basic test is better than no test
3. **Update documentation** - Add a line about your plugin to the README.md
4. **Run quality checks** - Use `make lint` to ensure code style consistency
5. **Open a pull request** - Share your plugin with the community!

### Pull Request Process

1. **Create a branch** for your plugin:
   ```sh
   git checkout -b add-my-plugin
   ```

2. **Commit your changes**:
   ```sh
   git add .
   git commit -m "Add MyPlugin to fix specific AsciiDoc issue"
   ```

3. **Push to GitHub**:
   ```sh
   git push origin add-my-plugin
   ```

4. **Open a pull request** on GitHub

5. **Respond to feedback** - Maintainers may suggest improvements

6. **Celebrate!** - Your plugin will help other technical writers

## Advanced Topics

### Development Workflow with Makefile

The project includes a Makefile with common development tasks:

```sh
make help           # Show all available commands
make install        # Basic installation 
make install-dev    # Install with development dependencies
make test           # Run all tests
make test-coverage  # Run tests with coverage report
make lint           # Check code quality
make format         # Format code with black and isort
make clean          # Clean build artifacts
make build          # Build distribution packages
```

### Working with File Content

Most plugins follow this pattern:

```python
def process_file_content(content, filepath):
    """Process the content of one file."""
    # Your logic here
    modified_content = your_processing_function(content)
    
    # Return: (new_content, was_changed)
    return modified_content, True  # or False if nothing changed
```

### Using Regular Expressions

Many text processing tasks use regex patterns:

```python
import re

def fix_content(content):
    # Find all instances of a pattern and replace them
    pattern = r'old-pattern'
    replacement = 'new-pattern'
    new_content = re.sub(pattern, replacement, content)
    return new_content
```

### Command-Line Arguments

Add custom arguments to your plugin:

```python
def register_subcommand(subparsers):
    parser = subparsers.add_parser("MyPlugin", help="My plugin description")
    
    # Boolean flag
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without changing it')
    
    # Option with a value
    parser.add_argument('--pattern', default='default-value',
                       help='Pattern to search for')
    
    # Required argument
    parser.add_argument('--required-option', required=True,
                       help='This option must be provided')
    
    parser.set_defaults(func=main)
```

## Why Contribute?

### For Technical Writers
- **Solve your own problems** - Create tools that fix issues you encounter daily
- **Help the community** - Share solutions that benefit other technical writers
- **Learn coding gradually** - Start simple and build your skills over time
- **Improve your workflow** - Automate repetitive tasks in your documentation

### For Developers
- **Modern Python practices** - Clean, well-structured codebase
- **Real-world impact** - Tools used by technical writers and content teams
- **Active maintenance** - Regular review and feedback on contributions
- **Growing ecosystem** - Help build a comprehensive toolkit for AsciiDoc DITA workflows

## Quick Reference

### Plugin Checklist
- [ ] Plugin file in `asciidoc_dita/plugins/`
- [ ] Has `main(args)` function
- [ ] Has `register_subcommand(subparsers)` function  
- [ ] Includes docstring explaining what it does
- [ ] Tested manually on sample files
- [ ] Follows the naming pattern of existing plugins
- [ ] Code formatted with `make format` or `black`
- [ ] Passes `make lint` quality checks

### Common File Patterns
```python
# Process all .adoc files recursively
from ..file_utils import process_adoc_files

# Simple content transformation
def fix_content(content):
    return content.replace('old', 'new')

# File processing with change detection
def process_file_content(content, filepath):
    new_content = fix_content(content)
    changed = (new_content != content)
    return new_content, changed
```

Ready to contribute? Start by looking at existing plugins and copying one that's similar to what you want to build!

