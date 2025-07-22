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

**Entrypoint Script Features:**
- Dynamic rule enabling/disabling via CLI arguments
- Directory exclusion pattern support
- JSON output formatting

### 2. ValeFlagger Plugin

**Core Functionality:**
````python
class ValeFlagger:
    def __init__(self, config_path=None):
        self.config = self.load_config(config_path)
        self.directory_config = DirectoryConfig()

    def run(self, target_path=".", rules=None, exclude_dirs=None):
        # 1. Get allowed directories from DirectoryConfig
        allowed_dirs = self.directory_config.get_allowed_paths(target_path)

        # 2. Run vale-adv with specified rules
        vale_output = self.run_vale(allowed_dirs, rules, exclude_dirs)

        # 3. Process JSON output and insert flags
        self.insert_flags(vale_output)

    def run_vale(self, paths, rules, exclude_dirs):
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
        return json.loads(result.stdout)

    def insert_flags(self, vale_output):
        for file_path, issues in vale_output.items():
            self.flag_file(file_path, issues)

    def flag_file(self, file_path, issues):
        # Read file
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Sort issues by line number (descending) to avoid offset issues
        sorted_issues = sorted(issues, key=lambda x: x['Line'], reverse=True)

        # Insert flags
        for issue in sorted_issues:
            flag = self.format_flag(issue)
            line_num = issue['Line'] - 1

            # Insert flag above the problematic line
            lines.insert(line_num, flag + '\n')

        # Write back
        with open(file_path, 'w') as f:
            f.writelines(lines)

    def format_flag(self, issue):
        return f"// ADT-FLAG [{issue['Check']}]: {issue['Message']}"
````

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
  backup_files: true
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
1. Add backup functionality before flagging
2. Implement flag removal command
3. Add dry-run mode for preview

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

## Future Enhancements

1. **Interactive Mode**: Review and approve flags before insertion
2. **Flag Management**: Commands to remove, update, or convert flags
3. **IDE Integration**: VS Code extension for real-time flagging
4. **Report Generation**: HTML/PDF reports of flagged issues
5. **Auto-fix Support**: For rules with deterministic fixes
