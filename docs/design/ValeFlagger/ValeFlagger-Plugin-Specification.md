# ValeFlagger Plugin Specification

## Overview

ValeFlagger is a plugin for the asciidoc-dita-toolkit (ADT) that integrates Vale linter with the asciidoctor-dita-vale (ADV) ruleset to identify and flag AsciiDoc syntax violations that are incompatible with DITA conversion.

## System Architecture

### Components

1. **vale-adv container**: Custom Docker image containing Vale + ADV ruleset
2. **ValeFlagger plugin**: Python/Node.js script that processes Vale output and inserts flags
3. **DirectoryConfig integration**: Respects ADT's directory inclusion/exclusion rules
4. **Configuration layer**: Handles rule selection and directory configuration

### Data Flow

```
DirectoryConfig → vale-adv → JSON output → ValeFlagger → Flagged .adoc files
```

## Technical Specifications

## Prerequisites & Dependencies
- Python 3.8+ with pip
- Docker Engine 20.0+ installed and running
- PyYAML package: `pip install pyyaml`
- Access to build and push Docker images
- asciidoc-dita-toolkit repository structure

### 1. vale-adv Container

**Dockerfile:**
````dockerfile
FROM jdkato/vale:latest

WORKDIR /vale
RUN vale sync --config=/dev/null jhradilek/asciidoctor-dita-vale

COPY vale-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/vale-entrypoint.sh

COPY .vale.ini /vale/.vale.ini

WORKDIR /docs
ENTRYPOINT ["/usr/local/bin/vale-entrypoint.sh"]
````

**Required .vale.ini file:**
```ini
StylesPath = /vale/styles

[formats]
adoc = md

[*.{adoc,md}]
BasedOnStyles = asciidoctor-dita-vale
```

**Required vale-entrypoint.sh:**
```bash
#!/bin/bash
set -e

CONFIG_FILE="/vale/.vale.ini"
TEMP_CONFIG="/tmp/.vale.ini"

# Copy base config
cp "$CONFIG_FILE" "$TEMP_CONFIG"

# Process arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --enable-rules)
            IFS=',' read -ra RULES <<< "$2"
            for rule in "${RULES[@]}"; do
                echo "asciidoctor-dita-vale.$rule = YES" >> "$TEMP_CONFIG"
            done
            shift 2
            ;;
        --disable-rules)
            IFS=',' read -ra RULES <<< "$2"
            for rule in "${RULES[@]}"; do
                echo "asciidoctor-dita-vale.$rule = NO" >> "$TEMP_CONFIG"
            done
            shift 2
            ;;
        *)
            break
            ;;
    esac
done

exec vale --config="$TEMP_CONFIG" "$@"
```

### 2. ValeFlagger Plugin

**Core Functionality:**
````python
# Required imports
import os
import subprocess
import json
import yaml
from pathlib import Path

class DirectoryConfig:
    def get_allowed_paths(self, target_path):
        """
        Returns a list of allowed directory paths based on configuration.
        """
        # ...implementation...
        return [target_path]

class ValeFlagger:
    def __init__(self, config_path=None):
        self.config = self.load_config(config_path)
        self.directory_config = DirectoryConfig()

    def load_config(self, config_path=None):
        """
        Loads YAML configuration from the given path or default.
        Returns a dict with keys: vale, directory_config, valeflag.
        """
        default_config = {
            'vale': {'enabled_rules': [], 'disabled_rules': []},
            'directory_config': {'include': ['.'], 'exclude': []},
            'valeflag': {'flag_format': '// ADT-FLAG [{rule}]: {message}'}
        }

        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f) or {}
                # Merge with defaults
                for key in default_config:
                    if key in user_config:
                        default_config[key].update(user_config[key])

        return default_config

    def run(self, target_path=".", rules=None, exclude_dirs=None):
        # 1. Get allowed directories from DirectoryConfig
        allowed_dirs = self.directory_config.get_allowed_paths(target_path)

        # 2. Run vale-adv with specified rules
        vale_output = self.run_vale(allowed_dirs, rules, exclude_dirs)

        # 3. Process JSON output and insert flags
        self.insert_flags(vale_output)

    def run_vale(self, paths, rules, exclude_dirs):
        # Check Docker availability
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("Docker is not installed or not running. Please install Docker and ensure it's running.")

        cmd = ["docker", "run", "--rm", "-v", f"{os.getcwd()}:/docs",
               "asciidoc-dita-toolkit/vale-adv"]

        # Add rule specifications
        if rules:
            cmd.extend(["--enable-rules", ",".join(rules)])

        # Add exclusions
        if exclude_dirs:
            for dir in exclude_dirs:
                cmd.append("--glob")
                cmd.append(f"!{dir}/**/*.adoc")

        cmd.extend(["--output=JSON"] + paths)

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Vale execution failed with return code {result.returncode}. "
                               f"Error: {result.stderr.strip()}")

        # Handle empty output
        if not result.stdout.strip():
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON output from Vale. Raw output: {result.stdout}") from e

    def insert_flags(self, vale_output):
        for file_path, issues in vale_output.items():
            self.flag_file(file_path, issues)

    def flag_file(self, file_path, issues):
        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Warning: File not found: {file_path}")
            return
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return

        # Sort issues by line number (descending) to avoid offset issues
        sorted_issues = sorted(issues, key=lambda x: x['Line'], reverse=True)

        # Insert flags, handling multiple issues on the same line
        inserted_lines = set()
        for issue in sorted_issues:
            flag = self.format_flag(issue)
            line_num = max(issue['Line'] - 1, 0)
            # Avoid duplicate flags on the same line
            if line_num in inserted_lines:
                continue
            lines.insert(line_num, flag + '\n')
            inserted_lines.add(line_num)

        # Write back
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        except Exception as e:
            print(f"Error writing {file_path}: {e}")

    def format_flag(self, issue):
        flag_format = self.config.get('valeflag', {}).get('flag_format', '// ADT-FLAG [{rule}]: {message}')
        return flag_format.format(rule=issue['Check'], message=issue['Message'])
````

### Expected Vale JSON Output Format

Vale outputs JSON in the following structure for Copilot to understand:

```json
{
  "path/to/file.adoc": [
    {
      "Check": "asciidoctor-dita-vale.Headings.Capitalization",
      "Message": "Heading should use sentence-style capitalization.",
      "Line": 15,
      "Span": [1, 25],
      "Severity": "error"
    }
  ]
}
```


### DirectoryConfig Interface

The `DirectoryConfig` class must provide this exact interface:

```python
class DirectoryConfig:
    def __init__(self, config=None):
        self.config = config or {}

    def get_allowed_paths(self, target_path):
        """
        Returns a list of allowed directory paths based on configuration.

        Args:
            target_path: Base path to scan (string)

        Returns:
            List of absolute paths that should be processed
        """
        include_dirs = self.config.get('directory_config', {}).get('include', ['.'])
        exclude_dirs = self.config.get('directory_config', {}).get('exclude', [])

        # Convert relative paths to absolute
        allowed_paths = []
        for include_dir in include_dirs:
            abs_path = os.path.abspath(os.path.join(target_path, include_dir))
            if os.path.exists(abs_path):
                # Check if this path should be excluded
                should_exclude = False
                for exclude_dir in exclude_dirs:
                    exclude_abs = os.path.abspath(os.path.join(target_path, exclude_dir))
                    if abs_path.startswith(exclude_abs):
                        should_exclude = True
                        break
                if not should_exclude:
                    allowed_paths.append(abs_path)

        return allowed_paths if allowed_paths else [target_path]
```

### 3. Configuration Integration

**ADT Configuration File (adt-config.yaml):**
````yaml
vale:
  enabled_rules:
    - "Headings.Capitalization"
    - "Terms.Use"
    - "Spelling.Terms"
  disabled_rules:
    - "Style.Passive"

directory_config:
  include:
    - "docs/"
    - "modules/"
  exclude:
    - "build/"
    - "node_modules/"
    - ".git/"

valeflag:
  flag_format: "// ADT-FLAG [{rule}]: {message}"
  # backup_files: true
````

### 4. CLI Interface

````bash
# Run with default configuration
adt valeflag

# Run with specific rules
adt valeflag --rules "Headings.Capitalization,Terms.Use"

# Run on specific directory
adt valeflag --path ./docs

# Disable specific rules
adt valeflag --disable-rules "Style.Passive"

# Use custom config
adt valeflag --config custom-config.yaml
````

## MVP Implementation Plan

### Phase 1: Core Functionality
1. Build vale-adv container with ADV ruleset
2. Implement basic ValeFlagger script
3. Support JSON parsing and flag insertion

### Phase 2: Configuration
1. Integrate with DirectoryConfig plugin
2. Add rule selection via CLI arguments
3. Support configuration file

### Phase 3: User Experience
1. TBD

## Edge Cases and Testing

- If multiple issues are flagged on the same line, only one flag is inserted per line to avoid clutter.
- If a file is missing or cannot be read/written, a warning is printed and processing continues.
- All file operations use UTF-8 encoding to avoid encoding errors.
- The system should be tested with files containing multiple, overlapping, and edge-case violations to ensure robust flag insertion.

## Flag Format Specification

Default flag format:
```adoc
// ADT-FLAG [RuleName]: Vale message describing the issue
```

Flags are:
- Inserted on the line above the violation
- Prefixed with `// ADT-FLAG` for easy identification
- Include the rule name in brackets
- Include the full Vale message

## Integration Points

### DirectoryConfig Plugin
- ValeFlagger queries DirectoryConfig for allowed/excluded paths
- Passes these as glob patterns to Vale

### ADT Main Toolkit
- ValeFlagger is invoked via `adt valeflag` command
- Shares configuration infrastructure
- Outputs to ADT logging system

## Error Handling

1. **Missing Docker**: Check for Docker availability, provide installation instructions
2. **File Permissions**: Handle read-only files gracefully
3. **Encoding Issues**: Support UTF-8 and handle encoding errors
4. **Concurrent Access**: Lock files during modification

## Implementation Steps

### Step 1: Build vale-adv Container
```bash
# Create directory structure
mkdir -p docker/vale-adv
cd docker/vale-adv

# Create files: Dockerfile, .vale.ini, vale-entrypoint.sh (see above)
# Build container
docker build -t asciidoc-dita-toolkit/vale-adv .
```

### Step 2: Implement ValeFlagger Class
Create `plugins/vale_flagger.py` with the complete class shown above.

### Step 3: Add CLI Integration
Add to main ADT CLI handler:
```python
def handle_valeflag_command(args):
    flagger = ValeFlagger(args.config)
    flagger.run(
        target_path=args.path or ".",
        rules=args.rules.split(",") if args.rules else None,
        exclude_dirs=args.exclude_dirs.split(",") if args.exclude_dirs else None
    )
```

## Testing & Validation

**Create these test files:**

1. `tests/fixtures/test.adoc` - Sample AsciiDoc with known violations
2. `tests/test_vale_flagger.py` - Unit tests
3. `tests/test_integration.py` - End-to-end tests

**Test scenarios to implement:**
- Mock Docker command execution and validate JSON parsing
- Test flag insertion with multiple issues on same/different lines
- Test configuration loading with valid/invalid YAML
- Test DirectoryConfig path filtering
- Integration test: run full pipeline and verify flags inserted correctly

**Validation checklist:**
- [ ] Container builds without errors
- [ ] Vale sync downloads ADV ruleset successfully
- [ ] Python class loads configuration correctly
- [ ] Docker execution produces valid JSON
- [ ] Flags are inserted at correct line positions
- [ ] Multiple issues on same line handled properly
- [ ] File encoding (UTF-8) handled correctly

## Future Enhancements

1. **Interactive Mode**: Review and approve flags before insertion
2. **Flag Management**: Commands to remove, update, or convert flags
3. **IDE Integration**: VS Code extension for real-time flagging
4. **Report Generation**: HTML/PDF reports of flagged issues
5. **Auto-fix Support**: For rules with deterministic fixes
