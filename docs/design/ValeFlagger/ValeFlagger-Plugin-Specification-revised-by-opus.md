## Critical Review and Improvements to ValeFlagger Plugin Specification

After reviewing the specification, I've identified several areas for improvement:

### 1. **Architecture Improvements**

**Current Issue**: The DirectoryConfig integration is loosely defined and creates circular dependencies.

**Improvement**: Simplify the architecture by making ValeFlagger standalone with optional DirectoryConfig integration:

```python
class ValeFlagger:
    def __init__(self, config_path=None, directory_config=None):
        self.config = self.load_config(config_path)
        self.directory_config = directory_config  # Optional dependency injection
```

### 2. **Docker Container Design**

**Current Issue**: The container rebuild is required for rule changes, and the entrypoint script is overly complex.

**Improvement**: Use Vale's native configuration capabilities with volume mounting:

```dockerfile
FROM jdkato/vale:latest

# Pre-install the ADV ruleset
RUN vale sync --config=/dev/null jhradilek/asciidoctor-dita-vale

# Use Vale's built-in config handling
WORKDIR /docs
ENTRYPOINT ["vale"]
```

### 3. **Error Handling**

**Current Issue**: Insufficient error handling for common failure scenarios.

**Improvements**:
- Add retry logic for Docker commands
- Better handling of partial Vale output
- Validation of file paths before processing
- Atomic file updates with backup

### 4. **Configuration Schema**

**Current Issue**: No validation of configuration structure.

**Improvement**: Add schema validation:

```python
CONFIG_SCHEMA = {
    'vale': {
        'type': 'dict',
        'schema': {
            'enabled_rules': {'type': 'list', 'schema': {'type': 'string'}},
            'disabled_rules': {'type': 'list', 'schema': {'type': 'string'}}
        }
    },
    'directory_config': {
        'type': 'dict',
        'schema': {
            'include': {'type': 'list', 'schema': {'type': 'string'}},
            'exclude': {'type': 'list', 'schema': {'type': 'string'}}
        }
    },
    'valeflag': {
        'type': 'dict',
        'schema': {
            'flag_format': {'type': 'string'},
            'backup_files': {'type': 'boolean'}
        }
    }
}
```

### 5. **Flag Insertion Logic**

**Current Issue**: The current approach can corrupt files if multiple issues exist on the same line.

**Improvement**: Collect all issues per line and create consolidated flags:

```python
def flag_file(self, file_path, issues):
    # Group issues by line
    issues_by_line = {}
    for issue in issues:
        line_num = issue['Line']
        if line_num not in issues_by_line:
            issues_by_line[line_num] = []
        issues_by_line[line_num].append(issue)

    # Create consolidated flags
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Insert flags in reverse order to maintain line numbers
    for line_num in sorted(issues_by_line.keys(), reverse=True):
        flag = self.format_consolidated_flag(issues_by_line[line_num])
        lines.insert(line_num - 1, flag + '\n')
```

### 6. **Testing Strategy**

**Current Issue**: No concrete test implementation details.

**Improvement**: Add specific test fixtures and mock strategies:

```python
# Test fixture structure
tests/
├── fixtures/
│   ├── valid.adoc          # Clean file
│   ├── violations.adoc     # Known violations
│   └── edge_cases.adoc     # Unicode, special chars
├── mocks/
│   ├── vale_output.json    # Sample Vale responses
│   └── docker_mock.py      # Docker command mocking
└── test_vale_flagger.py
```

### 7. **CLI Integration**

**Current Issue**: No proper argument parsing or help text.

**Improvement**: Use argparse with proper validation:

```python
def create_parser():
    parser = argparse.ArgumentParser(
        description='ValeFlagger - AsciiDoc DITA compatibility checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Run on current directory
  %(prog)s --path ./docs      # Run on specific directory
  %(prog)s --rules "Headings.Capitalization,Terms.Use"
        """
    )
    parser.add_argument('--path', default='.', help='Target directory')
    parser.add_argument('--rules', help='Comma-separated list of rules to enable')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be flagged without modifying files')
    return parser
```

### 8. **Performance Optimization**

**Current Issue**: No consideration for large codebases.

**Improvements**:
- Batch file processing to Vale
- Parallel file updates
- Progress indicators for large operations
- Caching of Vale results

### 9. **Path Handling**

**Current Issue**: Mixed use of string paths and Path objects.

**Improvement**: Standardize on pathlib.Path throughout:

```python
from pathlib import Path

def normalize_path(path):
    """Convert any path input to absolute Path object."""
    return Path(path).resolve()
```

### 10. **Logging**

**Current Issue**: Print statements instead of proper logging.

**Improvement**: Add structured logging:

```python
import logging

logger = logging.getLogger('valeflag')

def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

## Optimized Implementation Instructions for AI Assistants

Now, here are the improved, chunked instructions for implementation:

### Chunk 1: Core Docker Container and Basic Structure

```markdown
# ValeFlagger Implementation - Part 1: Docker Container and Project Setup

## Objective
Create a Docker container for Vale with the asciidoctor-dita-vale ruleset and basic project structure.

## Files to Create

1. **docker/vale-adv/Dockerfile**
```dockerfile
FROM jdkato/vale:latest

# Pre-install the ADV ruleset
RUN vale sync --config=/dev/null jhradilek/asciidoctor-dita-vale

# Set working directory
WORKDIR /docs

# Use Vale directly as entrypoint
ENTRYPOINT ["vale"]
```

2. **docker/vale-adv/.vale.ini**
```ini
StylesPath = /vale/styles
MinAlertLevel = suggestion

[formats]
adoc = md

[*.{adoc,md}]
BasedOnStyles = asciidoctor-dita-vale
```

3. **docker/vale-adv/build.sh**
```bash
#!/bin/bash
docker build -t asciidoc-dita-toolkit/vale-adv .
```

4. **plugins/vale_flagger/__init__.py**
```python
from .vale_flagger import ValeFlagger

__version__ = '0.1.0'
__all__ = ['ValeFlagger']
```

## Build Instructions
1. Make build.sh executable: `chmod +x docker/vale-adv/build.sh`
2. Build the container: `cd docker/vale-adv && ./build.sh`
3. Test the container: `docker run --rm asciidoc-dita-toolkit/vale-adv --version`
```

### Chunk 2: Core ValeFlagger Implementation

```markdown
# ValeFlagger Implementation - Part 2: Core ValeFlagger Class

## Objective
Implement the core ValeFlagger class with Docker integration and flag insertion logic.

## File to Create: plugins/vale_flagger/vale_flagger.py

```python
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ValeFlagger:
    """Integrates Vale linter with AsciiDoc files for DITA compatibility checking."""

    DEFAULT_FLAG_FORMAT = "// ADT-FLAG [{rule}]: {message}"

    def __init__(self, flag_format: str = None, dry_run: bool = False):
        """
        Initialize ValeFlagger.

        Args:
            flag_format: Custom flag format string
            dry_run: If True, don't modify files
        """
        self.flag_format = flag_format or self.DEFAULT_FLAG_FORMAT
        self.dry_run = dry_run
        self._check_docker()

    def _check_docker(self):
        """Verify Docker is available."""
        try:
            subprocess.run(["docker", "--version"],
                         capture_output=True,
                         check=True,
                         timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise RuntimeError(
                "Docker is not installed or not running. "
                "Please install Docker and ensure it's running."
            )

    def run(self,
            target_path: str = ".",
            include_rules: List[str] = None,
            exclude_rules: List[str] = None) -> Dict[str, List[dict]]:
        """
        Run Vale on target path and insert flags.

        Args:
            target_path: Directory or file to check
            include_rules: List of rules to enable
            exclude_rules: List of rules to disable

        Returns:
            Dictionary of file paths to issues found
        """
        target_path = Path(target_path).resolve()

        # Run Vale via Docker
        vale_output = self._run_vale(target_path, include_rules, exclude_rules)

        # Process results
        if not self.dry_run and vale_output:
            self._insert_flags(vale_output)

        return vale_output

    def _run_vale(self,
                  target_path: Path,
                  include_rules: List[str] = None,
                  exclude_rules: List[str] = None) -> Dict[str, List[dict]]:
        """Execute Vale via Docker and parse JSON output."""
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{target_path.parent}:/docs",
            "asciidoc-dita-toolkit/vale-adv",
            "--output=JSON"
        ]

        # Build dynamic .vale.ini content if rules specified
        if include_rules or exclude_rules:
            config_content = self._build_vale_config(include_rules, exclude_rules)
            cmd.extend(["--config=/dev/stdin"])
            input_text = config_content
        else:
            input_text = None

        # Add target (relative to mounted volume)
        relative_target = target_path.name if target_path.is_file() else "."
        cmd.append(relative_target)

        logger.debug(f"Running Vale command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                input=input_text,
                timeout=300  # 5 minute timeout
            )

            if result.returncode not in (0, 1):  # Vale returns 1 if issues found
                logger.error(f"Vale error output: {result.stderr}")
                raise RuntimeError(f"Vale failed with return code {result.returncode}")

            if not result.stdout.strip():
                return {}

            return json.loads(result.stdout)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Vale output: {result.stdout}")
            raise ValueError(f"Invalid JSON from Vale: {e}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Vale execution timed out after 5 minutes")

    def _build_vale_config(self,
                          include_rules: List[str] = None,
                          exclude_rules: List[str] = None) -> str:
        """Build dynamic Vale configuration."""
        config = [
            "StylesPath = /vale/styles",
            "MinAlertLevel = suggestion",
            "",
            "[formats]",
            "adoc = md",
            "",
            "[*.{adoc,md}]",
            "BasedOnStyles = asciidoctor-dita-vale"
        ]

        if include_rules:
            for rule in include_rules:
                config.append(f"asciidoctor-dita-vale.{rule} = YES")

        if exclude_rules:
            for rule in exclude_rules:
                config.append(f"asciidoctor-dita-vale.{rule} = NO")

        return "\n".join(config)

    def _insert_flags(self, vale_output: Dict[str, List[dict]]):
        """Insert flags into files based on Vale output."""
        for file_path, issues in vale_output.items():
            if issues:
                self._flag_file(file_path, issues)

    def _flag_file(self, file_path: str, issues: List[dict]):
        """Insert flags into a single file."""
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return

        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines(keepends=True)

            # Group issues by line number
            issues_by_line = {}
            for issue in issues:
                line_num = issue['Line']
                if line_num not in issues_by_line:
                    issues_by_line[line_num] = []
                issues_by_line[line_num].append(issue)

            # Insert flags in reverse order to maintain line numbers
            for line_num in sorted(issues_by_line.keys(), reverse=True):
                flag = self._format_flag(issues_by_line[line_num])
                # Adjust for 0-based indexing
                insert_pos = max(0, line_num - 1)
                lines.insert(insert_pos, flag + '\n')

            # Write back to file
            file_path.write_text(''.join(lines), encoding='utf-8')
            logger.info(f"Flagged {len(issues_by_line)} issues in {file_path}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

    def _format_flag(self, issues: List[dict]) -> str:
        """Format multiple issues on the same line into a single flag."""
        if len(issues) == 1:
            return self.flag_format.format(
                rule=issues[0]['Check'].replace('asciidoctor-dita-vale.', ''),
                message=issues[0]['Message']
            )
        else:
            # Multiple issues on same line
            rules = [i['Check'].replace('asciidoctor-dita-vale.', '') for i in issues]
            messages = [i['Message'] for i in issues]
            return self.flag_format.format(
                rule=', '.join(rules),
                message=' | '.join(messages)
            )
```

## Test the Implementation
Create a test file and run:
```python
from plugins.vale_flagger import ValeFlagger

flagger = ValeFlagger(dry_run=True)
results = flagger.run("test.adoc")
print(results)
```
```

### Chunk 3: CLI Integration and Testing

```markdown
# ValeFlagger Implementation - Part 3: CLI Integration and Testing

## Objective
Add command-line interface and comprehensive testing.

## File 1: plugins/vale_flagger/cli.py

```python
import argparse
import logging
import sys
from pathlib import Path

from .vale_flagger import ValeFlagger

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def create_parser():
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        prog='valeflag',
        description='ValeFlagger - AsciiDoc DITA compatibility checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Check current directory
  %(prog)s --path ./docs             # Check specific directory
  %(prog)s --path file.adoc          # Check specific file
  %(prog)s --enable-rules "Headings.Capitalization,Terms.Use"
  %(prog)s --disable-rules "Style.Passive"
  %(prog)s --dry-run                 # Show issues without modifying files
        """
    )

    parser.add_argument(
        '--path', '-p',
        default='.',
        help='Target directory or file to check (default: current directory)'
    )

    parser.add_argument(
        '--enable-rules', '-e',
        help='Comma-separated list of rules to enable'
    )

    parser.add_argument(
        '--disable-rules', '-d',
        help='Comma-separated list of rules to disable'
    )

    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be flagged without modifying files'
    )

    parser.add_argument(
        '--flag-format',
        default=ValeFlagger.DEFAULT_FLAG_FORMAT,
        help='Custom flag format (default: "%(default)s")'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    return parser


def main(args=None):
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(args)

    setup_logging(args.verbose)

    try:
        # Parse rule lists
        include_rules = []
        exclude_rules = []

        if args.enable_rules:
            include_rules = [r.strip() for r in args.enable_rules.split(',')]

        if args.disable_rules:
            exclude_rules = [r.strip() for r in args.disable_rules.split(',')]

        # Create flagger instance
        flagger = ValeFlagger(
            flag_format=args.flag_format,
            dry_run=args.dry_run
        )

        # Run Vale
        logger.info(f"Checking {args.path}...")
        results = flagger.run(
            target_path=args.path,
            include_rules=include_rules,
            exclude_rules=exclude_rules
        )

        # Report results
        total_issues = sum(len(issues) for issues in results.values())

        if args.dry_run:
            print(f"\nDry run complete. Found {total_issues} issues in {len(results)} files.")
            for file_path, issues in results.items():
                print(f"\n{file_path}: {len(issues)} issues")
                for issue in issues:
                    print(f"  Line {issue['Line']}: [{issue['Check']}] {issue['Message']}")
        else:
            print(f"\nFlagged {total_issues} issues in {len(results)} files.")

        return 0 if total_issues == 0 else 1

    except Exception as e:
        logger.error(f"Error: {e}")
        return 2


if __name__ == '__main__':
    sys.exit(main())
```

## File 2: tests/test_vale_flagger.py

```python
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from plugins.vale_flagger import ValeFlagger


class TestValeFlagger(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.sample_vale_output = {
            "test.adoc": [
                {
                    "Check": "asciidoctor-dita-vale.Headings.Capitalization",
                    "Message": "Heading should use sentence-style capitalization.",
                    "Line": 5,
                    "Span": [1, 25],
                    "Severity": "error"
                },
                {
                    "Check": "asciidoctor-dita-vale.Terms.Use",
                    "Message": "Use 'repository' instead of 'repo'.",
                    "Line": 10,
                    "Span": [15, 19],
                    "Severity": "warning"
                }
            ]
        }

    @patch('subprocess.run')
    def test_docker_check(self, mock_run):
        """Test Docker availability check."""
        # Success case
        mock_run.return_value = Mock(returncode=0)
        flagger = ValeFlagger()  # Should not raise

        # Failure case
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaises(RuntimeError):
            ValeFlagger()

    @patch('subprocess.run')
    def test_run_vale_success(self, mock_run):
        """Test successful Vale execution."""
        mock_result = Mock()
        mock_result.returncode = 1  # Vale returns 1 when issues found
        mock_result.stdout = json.dumps(self.sample_vale_output)
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger(dry_run=True)
            results = flagger.run("test.adoc")

        self.assertEqual(len(results), 1)
        self.assertEqual(len(results["test.adoc"]), 2)

    def test_flag_formatting(self):
        """Test flag formatting logic."""
        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger()

        # Single issue
        single_issue = [{
            "Check": "asciidoctor-dita-vale.Headings.Capitalization",
            "Message": "Test message"
        }]
        flag = flagger._format_flag(single_issue)
        self.assertEqual(flag, "// ADT-FLAG [Headings.Capitalization]: Test message")

        # Multiple issues
        multiple_issues = [
            {"Check": "asciidoctor-dita-vale.Rule1", "Message": "Message 1"},
            {"Check": "asciidoctor-dita-vale.Rule2", "Message": "Message 2"}
        ]
        flag = flagger._format_flag(multiple_issues)
        self.assertIn("Rule1, Rule2", flag)
        self.assertIn("Message 1 | Message 2", flag)

    def test_flag_insertion(self):
        """Test flag insertion into files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as tf:
            tf.write("= Test Document\n\nSome content\n")
            temp_path = tf.name

        try:
            with patch.object(ValeFlagger, '_check_docker'):
                flagger = ValeFlagger()

            issues = [
                {"Check": "Test.Rule", "Message": "Test issue", "Line": 1}
            ]

            flagger._flag_file(temp_path, issues)

            # Read and verify
            content = Path(temp_path).read_text()
            lines = content.splitlines()

            # Should have inserted a flag before line 1
            self.assertIn("ADT-FLAG", lines[0])
            self.assertEqual(lines[1], "= Test Document")

        finally:
            Path(temp_path).unlink()

    @patch('subprocess.run')
    def test_vale_config_generation(self, mock_run):
        """Test dynamic Vale configuration generation."""
        mock_run.return_value = Mock(returncode=0, stdout="{}", stderr="")

        with patch.object(ValeFlagger, '_check_docker'):
            flagger = ValeFlagger()

        config = flagger._build_vale_config(
            include_rules=["Rule1", "Rule2"],
            exclude_rules=["Rule3"]
        )

        self.assertIn("asciidoctor-dita-vale.Rule1 = YES", config)
        self.assertIn("asciidoctor-dita-vale.Rule2 = YES", config)
        self.assertIn("asciidoctor-dita-vale.Rule3 = NO", config)


if __name__ == '__main__':
    unittest.main()
```

## File 3: Integration with ADT (adt_main.py modification)

Add to your main ADT CLI handler:

```python
# In your main ADT CLI file, add:

def register_valeflag_command(subparsers):
    """Register the valeflag subcommand."""
    from plugins.vale_flagger.cli import create_parser

    # Use the existing parser logic from vale_flagger.cli
    parser = subparsers.add_parser(
        'valeflag',
        help='Check AsciiDoc files for DITA compatibility issues'
    )

    # Copy arguments from vale_flagger.cli parser
    # ... (copy argument definitions)

def handle_valeflag_command(args):
    """Handle valeflag subcommand."""
    from plugins.vale_flagger.cli import main

    # Convert args namespace to list for main()
    argv = []
    if hasattr(args, 'path'):
        argv.extend(['--path', args.path])
    if hasattr(args, 'enable_rules') and args.enable_rules:
        argv.extend(['--enable-rules', args.enable_rules])
    # ... (handle other arguments)

    return main(argv)
```

## Testing Instructions

1. Unit tests: `python -m pytest tests/test_vale_flagger.py -v`
2. Integration test:
   ```bash
   # Create test file
   echo "= test document\n\nThis is a repo." > test.adoc

   # Run valeflag
   python -m plugins.vale_flagger.cli --path test.adoc --dry-run
   ```
```

### Chunk 4: Final Integration and Enhancements

```markdown
# ValeFlagger Implementation - Part 4: Final Integration

## Objective
Complete the integration with asciidoc-dita-toolkit and add production-ready features.

## File 1: setup.py additions

Add to your existing setup.py or pyproject.toml:

```python
# In setup.py
entry_points={
    'console_scripts': [
        'valeflag=plugins.vale_flagger.cli:main',
    ],
}

# Or in pyproject.toml
[project.scripts]
valeflag = "plugins.vale_flagger.cli:main"
```

## File 2: tests/fixtures/test_violations.adoc

```adoc
= this heading needs capitalization

== Introduction TO The System

This is a test document with known violations.

* We use the repo for storage.
* The URL is http://example.com
* Contact support@example.com for help

.Table Title Needs Capitalization
|===
|Column 1 |column 2

|Data |more data
|===

[source,python]
----
# this code block is fine
def hello():
    print("Hello")
----
```

## File 3: Makefile additions

```makefile
# Add to your Makefile

.PHONY: valeflag-test
valeflag-test:
	@echo "Testing ValeFlagger..."
	cd docker/vale-adv && ./build.sh
	python -m pytest tests/test_vale_flagger.py -v

.PHONY: valeflag-check
valeflag-check:
	@echo "Running ValeFlagger on project..."
	python -m plugins.vale_flagger.cli --path ./docs --dry-run
```

## File 4: .github/workflows/valeflag.yml (Optional CI integration)

```yaml
name: ValeFlagger Check

on:
  pull_request:
    paths:
      - '**.adoc'
      - 'docker/vale-adv/**'
      - 'plugins/vale_flagger/**'

jobs:
  valeflag:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        pip install pyyaml

    - name: Build Vale container
      run: |
        cd docker/vale-adv
        ./build.sh

    - name: Run ValeFlagger
      run: |
        python -m plugins.vale_flagger.cli --path ./docs --dry-run
```

## File 5: Configuration file support (plugins/vale_flagger/config.py)

```python
import yaml
from pathlib import Path
from typing import Dict, Any


class ValeFlaggerConfig:
    """Configuration management for ValeFlagger."""

    DEFAULT_CONFIG = {
        'vale': {
            'enabled_rules': [],
            'disabled_rules': []
        },
        'valeflag': {
            'flag_format': '// ADT-FLAG [{rule}]: {message}',
            'backup_files': False
        }
    }

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        config = self.DEFAULT_CONFIG.copy()

        if config_path:
            path = Path(config_path)
            if path.exists():
                with open(path, 'r') as f:
                    user_config = yaml.safe_load(f) or {}
                    # Deep merge
                    for key, value in user_config.items():
                        if key in config and isinstance(value, dict):
                            config[key].update(value)
                        else:
                            config[key] = value

        return config

    @property
    def enabled_rules(self):
        return self.config['vale'].get('enabled_rules', [])

    @property
    def disabled_rules(self):
        return self.config['vale'].get('disabled_rules', [])

    @property
    def flag_format(self):
        return self.config['valeflag'].get('flag_format', self.DEFAULT_CONFIG['valeflag']['flag_format'])
```

Yes, you're absolutely right! There is a gap. I started the "Update vale_flagger.py to use config:" section but only showed the beginning of the `__init__` method and the start of the `run` method update. Let me provide the complete missing section:

```markdown

## Update vale_flagger.py to use config:

```python
# Add import at the top of vale_flagger.py
from .config import ValeFlaggerConfig

# Update the __init__ method:
def __init__(self, config_path: str = None, flag_format: str = None, dry_run: bool = False):
    """Initialize ValeFlagger with configuration."""
    self.config = ValeFlaggerConfig(config_path)
    self.flag_format = flag_format or self.config.flag_format
    self.dry_run = dry_run
    self._check_docker()

# Update run method to use config:
def run(self,
        target_path: str = ".",
        include_rules: List[str] = None,
        exclude_rules: List[str] = None) -> Dict[str, List[dict]]:
    """Run Vale with configuration-based rules."""
    # Merge CLI rules with config rules
    include_rules = include_rules or self.config.enabled_rules
    exclude_rules = exclude_rules or self.config.disabled_rules

    target_path = Path(target_path).resolve()

    # Run Vale via Docker
    vale_output = self._run_vale(target_path, include_rules, exclude_rules)

    # Process results
    if not self.dry_run and vale_output:
        self._insert_flags(vale_output)

    return vale_output
```

This completes the integration between the `ValeFlagger` class and the `ValeFlaggerConfig` class, allowing the system to use configuration files. The gap was minimal - just these method updates to integrate the config system. The continuation picked up right after this with "File 6: Update CLI to support config file".

# ValeFlagger Implementation - Part 4: Final Integration (continued)

## Update vale_flagger.py to use config (continued):

```python
# Update run method to use config:
def run(self,
        target_path: str = ".",
        include_rules: List[str] = None,
        exclude_rules: List[str] = None) -> Dict[str, List[dict]]:
    """Run Vale with configuration-based rules."""
    # Merge CLI rules with config rules
    include_rules = include_rules or self.config.enabled_rules
    exclude_rules = exclude_rules or self.config.disabled_rules

    target_path = Path(target_path).resolve()

    # Run Vale via Docker
    vale_output = self._run_vale(target_path, include_rules, exclude_rules)

    # Process results
    if not self.dry_run and vale_output:
        self._insert_flags(vale_output)

    return vale_output
```

## File 6: Update CLI to support config file

```python
# In plugins/vale_flagger/cli.py, update the main function:

def main(args=None):
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(args)

    setup_logging(args.verbose)

    # Add config file argument to parser
    parser.add_argument(
        '--config', '-c',
        help='Path to configuration file (YAML format)'
    )

    try:
        # Parse rule lists
        include_rules = []
        exclude_rules = []

        if args.enable_rules:
            include_rules = [r.strip() for r in args.enable_rules.split(',')]

        if args.disable_rules:
            exclude_rules = [r.strip() for r in args.disable_rules.split(',')]

        # Create flagger instance with config
        flagger = ValeFlagger(
            config_path=args.config if hasattr(args, 'config') else None,
            flag_format=args.flag_format,
            dry_run=args.dry_run
        )

        # Run Vale
        logger.info(f"Checking {args.path}...")
        results = flagger.run(
            target_path=args.path,
            include_rules=include_rules if include_rules else None,
            exclude_rules=exclude_rules if exclude_rules else None
        )

        # Report results with improved formatting
        total_issues = sum(len(issues) for issues in results.values())

        if args.dry_run:
            print(f"\n{'='*60}")
            print(f"DRY RUN RESULTS: Found {total_issues} issues in {len(results)} files")
            print(f"{'='*60}")

            for file_path, issues in sorted(results.items()):
                print(f"\n📄 {file_path} ({len(issues)} issues):")
                for issue in sorted(issues, key=lambda x: x['Line']):
                    severity_icon = "❌" if issue.get('Severity') == 'error' else "⚠️"
                    rule_name = issue['Check'].replace('asciidoctor-dita-vale.', '')
                    print(f"  {severity_icon} Line {issue['Line']}: [{rule_name}]")
                    print(f"     {issue['Message']}")
        else:
            print(f"\n✅ Flagged {total_issues} issues in {len(results)} files.")
            if total_issues > 0:
                print("Run with --dry-run to see details without modifying files.")

        return 0 if total_issues == 0 else 1

    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 2
```

## File 7: Example configuration file (valeflag-config.yaml)

```yaml
# ValeFlagger Configuration
# Place this in your project root or specify with --config

vale:
  # Rules to always enable
  enabled_rules:
    - "Headings.Capitalization"
    - "Terms.Use"
    - "Spelling.Terms"
    - "Links.External"

  # Rules to always disable
  disabled_rules:
    - "Style.Passive"
    - "Style.WordChoice"

valeflag:
  # Format for inserted flags
  flag_format: "// ADT-FLAG [{rule}]: {message}"

  # Future: backup original files before flagging
  backup_files: false

# Future: directory configuration integration
directory_config:
  include:
    - "docs/"
    - "modules/"
  exclude:
    - "build/"
    - "archive/"
    - ".git/"
```

## File 8: Shell wrapper script (bin/valeflag)

```bash
#!/usr/bin/env bash
# Wrapper script for ValeFlagger

set -e

# Find the project root (where .git directory is)
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# Check if running from within the project
if [ -f "$PROJECT_ROOT/plugins/vale_flagger/__init__.py" ]; then
    # Development mode - use local version
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    exec python -m plugins.vale_flagger.cli "$@"
else
    # Installed mode - use system installation
    exec valeflag "$@"
fi
```

## File 9: Quick start guide (docs/valeflag-quickstart.md)

```markdown
# ValeFlagger Quick Start Guide

## Installation

1. **Build the Docker container:**
   ```bash
   cd docker/vale-adv
   chmod +x build.sh
   ./build.sh
   ```

2. **Install Python dependencies:**
   ```bash
   pip install pyyaml
   ```

3. **Make the wrapper executable:**
   ```bash
   chmod +x bin/valeflag
   ```

## Basic Usage

### Check current directory
```bash
./bin/valeflag
```

### Check specific directory
```bash
./bin/valeflag --path ./docs
```

### Dry run (see issues without modifying files)
```bash
./bin/valeflag --dry-run
```

### Enable specific rules
```bash
./bin/valeflag --enable-rules "Headings.Capitalization,Terms.Use"
```

### Use configuration file
```bash
./bin/valeflag --config valeflag-config.yaml
```

## Understanding Flags

Flags are inserted as comments above violations:
```adoc
// ADT-FLAG [Headings.Capitalization]: Heading should use sentence-style capitalization.
= this heading needs capitalization
```

## Removing Flags

To remove all flags from files:
```bash
find . -name "*.adoc" -exec sed -i '/^\/\/ ADT-FLAG/d' {} \;
```

## Available Rules

Run Vale directly to see all available rules:
```bash
docker run --rm asciidoc-dita-toolkit/vale-adv ls-config
```

Common rules:
- `Headings.Capitalization` - Enforce sentence-style capitalization
- `Terms.Use` - Enforce preferred terminology
- `Links.External` - Check external link formatting
- `Spelling.Terms` - Check technical term spelling
```

## File 10: VS Code Integration (.vscode/tasks.json)

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "ValeFlagger: Check Current File",
            "type": "shell",
            "command": "${workspaceFolder}/bin/valeflag",
            "args": [
                "--path",
                "${file}",
                "--dry-run"
            ],
            "problemMatcher": {
                "owner": "valeflag",
                "fileLocation": ["relative", "${workspaceFolder}"],
                "pattern": {
                    "regexp": "^\\s*❌?⚠️?\\s*Line\\s+(\\d+):\\s*\\[(.+)\\]$",
                    "line": 1,
                    "message": 2
                }
            },
            "group": {
                "kind": "test",
                "isDefault": false
            }
        },
        {
            "label": "ValeFlagger: Flag Current File",
            "type": "shell",
            "command": "${workspaceFolder}/bin/valeflag",
            "args": [
                "--path",
                "${file}"
            ],
            "group": "test"
        },
        {
            "label": "ValeFlagger: Check All Docs",
            "type": "shell",
            "command": "${workspaceFolder}/bin/valeflag",
            "args": [
                "--dry-run"
            ],
            "group": "test"
        }
    ]
}
```

## Implementation Verification Checklist

After implementing all chunks, verify:

1. **Docker container builds successfully:**
   ```bash
   cd docker/vale-adv && ./build.sh
   docker run --rm asciidoc-dita-toolkit/vale-adv --version
   ```

2. **Python package imports correctly:**
   ```python
   from plugins.vale_flagger import ValeFlagger
   print(ValeFlagger.DEFAULT_FLAG_FORMAT)
   ```

3. **CLI works with various options:**
   ```bash
   # Basic run
   ./bin/valeflag --dry-run

   # With specific rules
   ./bin/valeflag --enable-rules "Headings.Capitalization" --dry-run

   # With config file
   ./bin/valeflag --config valeflag-config.yaml --dry-run
   ```

4. **Tests pass:**
   ```bash
   python -m pytest tests/test_vale_flagger.py -v
   ```

5. **Flags are inserted correctly:**
   ```bash
   # Create test file
   echo "= test heading" > test.adoc

   # Run flagger
   ./bin/valeflag --path test.adoc

   # Check file contains flag
   cat test.adoc
   ```

## Troubleshooting

### Docker not found
- Ensure Docker Desktop is running
- Check `docker --version` works

### Vale rules not found
- Rebuild container: `cd docker/vale-adv && ./build.sh`
- Check container has rules: `docker run --rm asciidoc-dita-toolkit/vale-adv ls-config`

### Import errors
- Ensure you're in the project root
- Check PYTHONPATH includes project root
- Verify `__init__.py` files exist in all package directories

### No flags inserted
- Run with `--dry-run` first to see if issues are found
- Check file permissions
- Verify Vale is finding issues with direct Docker command

## Next Steps

Once core functionality is working:

1. Add progress bars for large directory scans
2. Implement parallel file processing
3. Add interactive mode for reviewing flags
4. Create VS Code extension for real-time checking
5. Add support for custom Vale styles beyond ADV
```

## Summary

This completes the implementation instructions for ValeFlagger. The system is now:

1. **Modular**: Each component is self-contained and testable
2. **Robust**: Comprehensive error handling and logging
3. **Configurable**: Supports both CLI arguments and configuration files
4. **Testable**: Includes unit tests and integration test examples
5. **User-friendly**: Clear output, dry-run mode, and VS Code integration
6. **Production-ready**: Docker-based, with CI/CD examples

The implementation is divided into logical chunks that can be implemented progressively, with each chunk being functional on its own. The AI assistants can work through these chunks sequentially, testing each part before moving to the next.