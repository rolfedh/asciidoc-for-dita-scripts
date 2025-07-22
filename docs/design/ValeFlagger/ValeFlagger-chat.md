rolfedh: I need to run vale linter with the vale ruleset in asciidoctor-dita-vale and get its output as json. The json file contains key information like the rule being violated, the filename, and the line number. Then I want to run a script or plugin that takes the json and uses it to insert comments into the file at the location of the issues the Vale linter flagged. The script or plugin is named ValeFlagger. I need your advice: How should i do this?

GitHub Copilot: Here’s a step-by-step approach to achieve your workflow using the `asciidoctor-dita-vale` ruleset and a custom `ValeFlagger` script:

---

### 1. **Run Vale with JSON Output**

Run Vale on your AsciiDoc files and output the results as JSON:

```bash
vale --output=JSON --no-wrap --sort . > vale_report.json
```

- This will lint all `.adoc` files in the current directory and subdirectories.
- The output file `vale_report.json` will contain all issues, with fields like `Check` (rule), `Filename`, and `Line`.

---

### 2. **Design the ValeFlagger Script**

Your `ValeFlagger` script should:

- Parse `vale_report.json`.
- For each issue, open the corresponding file.
- Insert a comment at the flagged line (or just above/below, as needed).
- Save the modified file.

**Comment format example:**
```adoc
// ADT [RuleName]: [Vale message]
```

---

### 3. **ValeFlagger Implementation Outline**

Here’s a Python outline for `ValeFlagger`:

````python
import json

def insert_comment(filename, line_number, comment):
    with open(filename, 'r') as f:
        lines = f.readlines()
    # Insert comment above the flagged line
    lines.insert(line_number - 1, comment + '\n')
    with open(filename, 'w') as f:
        f.writelines(lines)

with open('vale_report.json') as f:
    issues = json.load(f)

for issue in issues:
    filename = issue['Filename']
    line = issue['Line']
    rule = issue['Check']
    message = issue['Message']
    comment = f"// ADT {rule}: {message}"
    insert_comment(filename, line, comment)
````

- Adjust for edge cases (multiple issues on the same line, file encoding, etc.).
- Consider making a backup of each file before modifying.

---

### 4. **Workflow Summary**

1. **Lint:**
   `vale --output=JSON --no-wrap --sort . > vale_report.json`
2. **Flag:**
   `python ValeFlagger.py` (or however you name/invoke your script)

---

### 5. **Best Practices**

- Run Vale and ValeFlagger on a test branch or with backups.
- Review the inserted comments before committing changes.
- You can extend ValeFlagger to support custom comment formats or interactive review.

---

**References:**
- [Vale JSON output docs](https://vale.sh/docs/topics/output-formats/)
- [AsciiDocDITA Vale rules](https://github.com/jhradilek/asciidoctor-dita-vale)

Let me know if you want a more robust script or integration with your toolkit!

rolfedh: I need to give end users a reliable way to run vale and the https://github.com/jhradilek/asciidoctor-dita-vale ruleset with asciidoc-dita-toolkit.
I think this might involve:
- Serving Vale as a container. (It is available on Docker Hub at jdkato/vale. See https://vale.sh/docs/install#docker.)
- I'm not sure what the best way to provide the asciidoctor-dita-vale ruleset. How should I ship the .vale.ini file? Should I provide the asciidoctor-dita-vale ruleset by running `vale sync`, shipping it in another container, or including both in my asciidoc-dita-toolkit container?
What do you recommend?


GitHub Copilot: Here's my recommendation for reliably distributing Vale with the `asciidoctor-dita-vale` ruleset:

## **Option 1: Single Container Approach (Recommended)**

Create your own Docker image that extends the official Vale image and includes the ruleset:

````dockerfile
FROM jdkato/vale:latest

# Install the asciidoctor-dita-vale ruleset
WORKDIR /vale
RUN vale sync --config=/dev/null jhradilek/asciidoctor-dita-vale

# Copy your custom .vale.ini
COPY .vale.ini /vale/.vale.ini

# Set working directory for user files
WORKDIR /docs

# Default command
CMD ["vale", "--config=/vale/.vale.ini", "."]
````

Then provide a `.vale.ini` configuration:

````ini
StylesPath = /vale/styles

Vocab = asciidoc-dita

[formats]
adoc = md

[*.{adoc,md}]
BasedOnStyles = asciidoctor-dita-vale
````

**Usage:**
```bash
# Build your custom image
docker build -f Dockerfile.vale -t asciidoc-dita-toolkit/vale .

# Run Vale on current directory
docker run --rm -v $(pwd):/docs asciidoc-dita-toolkit/vale --output=JSON
```

---

## **Option 2: Docker Compose Approach**

If you prefer keeping Vale separate, use Docker Compose:

````yaml
version: '3.8'
services:
  vale:
    image: jdkato/vale:latest
    volumes:
      - .:/docs
      - ./vale-config/.vale.ini:/root/.vale.ini
      - vale-styles:/root/styles
    working_dir: /docs
    command: ["vale", "--output=JSON", "."]

volumes:
  vale-styles:
````

With an init container to sync styles:

````yaml
version: '3.8'
services:
  vale-init:
    image: jdkato/vale:latest
    volumes:
      - vale-styles:/root/styles
      - ./vale-config/.vale.ini:/root/.vale.ini
    command: ["vale", "sync"]

  vale:
    image: jdkato/vale:latest
    depends_on:
      - vale-init
    volumes:
      - .:/docs
      - ./vale-config/.vale.ini:/root/.vale.ini
      - vale-styles:/root/styles
    working_dir: /docs

volumes:
  vale-styles:
````

---

## **Option 3: Include in Main Toolkit Container**

Add Vale to your existing `asciidoc-dita-toolkit` container:

````dockerfile
# ...existing code...

# Install Vale
RUN wget -O vale.tar.gz https://github.com/errata-ai/vale/releases/latest/download/vale_Linux_64-bit.tar.gz && \
    tar -xzf vale.tar.gz && \
    mv vale /usr/local/bin/ && \
    rm vale.tar.gz

# Install asciidoctor-dita-vale ruleset
RUN vale sync --config=/dev/null jhradilek/asciidoctor-dita-vale

# Copy Vale configuration
COPY .vale.ini /etc/vale/.vale.ini

# ...existing code...
````

---

## **My Recommendation: Option 1**

The single container approach is best because it:

1. **Ensures consistency** - Users get exact same Vale version and ruleset
2. **Simplifies distribution** - One image to maintain
3. **Reduces complexity** - No multi-container orchestration needed
4. **Version locks everything** - No surprise updates breaking compatibility

**Implementation steps:**
1. Create the custom Vale Dockerfile
2. Include `.vale.ini` in your toolkit repo
3. Build and push to Docker Hub as `asciidoc-dita-toolkit/vale`
4. Provide simple wrapper scripts or Makefile targets

**Wrapper script example:**
````bash
#!/bin/bash
docker run --rm -v $(pwd):/docs asciidoc-dita-toolkit/vale "$@"
````

This gives users a simple `./scripts/vale-lint.sh --output=JSON` command while ensuring reproducible results.

rolfedh: Whatever implementation I choose from the options you've suggested, let's call it the "vale-adv combo" from now on.

Which option should I choose if I want to pass an argument to the vale-adv combo that enables or disables a specific rule in the asciidoctor-dita-vale (ADV) ruleset.


GitHub Copilot: For passing arguments to enable/disable specific ADV rules, **Option 1 (Single Container)** is the best choice. Here's why and how to implement it:

## **Why Option 1 Works Best for Rule Control**

The single container approach gives you full control over Vale's configuration and allows you to dynamically modify rule settings through command-line arguments.

## **Implementation with Rule Control**

````dockerfile
FROM jdkato/vale:latest

# Install the asciidoctor-dita-vale ruleset
WORKDIR /vale
RUN vale sync --config=/dev/null jhradilek/asciidoctor-dita-vale

# Copy entrypoint script for rule control
COPY vale-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/vale-entrypoint.sh

# Copy base configuration
COPY .vale.ini /vale/.vale.ini

WORKDIR /docs
ENTRYPOINT ["/usr/local/bin/vale-entrypoint.sh"]
CMD ["--config=/vale/.vale.ini", "."]
````

Create an entrypoint script that handles rule enabling/disabling:

````bash
#!/bin/bash

CONFIG_FILE="/vale/.vale.ini"
TEMP_CONFIG="/tmp/.vale.ini"

# Copy base config to temp location
cp "$CONFIG_FILE" "$TEMP_CONFIG"

# Process rule control arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --disable-rule)
            RULE="$2"
            echo "asciidoctor-dita-vale.$RULE = NO" >> "$TEMP_CONFIG"
            shift 2
            ;;
        --enable-rule)
            RULE="$2"
            echo "asciidoctor-dita-vale.$RULE = YES" >> "$TEMP_CONFIG"
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

# Run vale with the modified config and remaining arguments
exec vale --config="$TEMP_CONFIG" "$@"
````

## **Usage Examples**

````bash
# Disable a specific rule
docker run --rm -v $(pwd):/docs asciidoc-dita-toolkit/vale-adv \
    --disable-rule "Headings.Capitalization" --output=JSON .

# Disable multiple rules
docker run --rm -v $(pwd):/docs asciidoc-dita-toolkit/vale-adv \
    --disable-rules "Headings.Capitalization,Terms.Use" --output=JSON .

# Enable a rule (if disabled in base config)
docker run --rm -v $(pwd):/docs asciidoc-dita-toolkit/vale-adv \
    --enable-rule "Headings.Capitalization" --output=JSON .
````

## **Wrapper Script for Convenience**

````bash
#!/bin/bash

CONTAINER_NAME="asciidoc-dita-toolkit/vale-adv"

# Pass all arguments directly to the container
docker run --rm -v "$(pwd):/docs" "$CONTAINER_NAME" "$@"
````

## **Alternative: Configuration Override**

You could also support passing a custom `.vale.ini` file:

````bash
# Use custom config file
docker run --rm \
    -v $(pwd):/docs \
    -v $(pwd)/custom-vale.ini:/vale/.vale.ini \
    asciidoc-dita-toolkit/vale-adv --output=JSON .
````

## **Why Not Options 2 & 3?**

- **Option 2 (Docker Compose)**: Harder to pass dynamic arguments through compose
- **Option 3 (Main Container)**: Adds complexity to your main toolkit container

The single container approach gives you the cleanest interface for rule control while keeping the vale-adv combo self-contained and easy to distribute.

rolfedh: Definitions:
- ADV = asciidoctor-dita-vale, a set of Vale rules to detect asciidoc syntax that isn't permissible in DITA.
- ADT = asciidoc-dita-toolkit, a software toolkit to identify, and flag or fix  asciidoc syntax that isn't permissible in DITA.

Following your recommendations, describe a system that consists of a new ValeFlagger plugin that works with Vale and ADV such that:
- vale runs with the ADV rule set to search *.adoc for rule violations
- The user can specify which ADV rule or rules to apply. The ADT software can also pass this information from a config file.
- the system respects the constraints imposed by the DirectoryConfig plugin: which directories are allowed and which ones are excluded.
- ValeFlagger uses the output from Vale and ADV to flag specific lines in the *.adoc content files.

Use your expertise and critical judgement as a software architect to describe an MVP system that does these things in a new markdown file named ValeFlagger-specs.md

GitHub Copilot: ````markdown
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
                # Add a separate --glob flag for each exclusion
                cmd.append(f"--glob=!{dir}/**/*.adoc")
        cmd.extend(["--output=JSON"] + paths)

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Vale command failed with return code {result.returncode}. Error: {result.stderr.strip()}")
        if result.returncode != 0:
            raise RuntimeError(f"Vale command failed with return code {result.returncode}. Error: {result.stderr}")
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Vale output as JSON. Error: {e}. Output: {result.stdout}")

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
