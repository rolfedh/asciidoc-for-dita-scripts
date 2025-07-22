# ValeFlagger - AsciiDoc DITA Compatibility Checker

ValeFlagger is a plugin for the AsciiDoc DITA Toolkit that integrates Vale linter to check AsciiDoc files for DITA compatibility issues. It automatically flags violations by inserting comments directly into your source files.

## Features

- **Docker-based Vale Integration**: Uses a pre-configured Docker container with the asciidoctor-dita-vale ruleset
- **Automatic Flag Insertion**: Inserts formatted comments above violations for easy identification
- **Flexible Configuration**: Supports YAML configuration files and CLI arguments
- **Dry Run Mode**: Preview issues without modifying files
- **Rule Customization**: Enable/disable specific Vale rules as needed
- **VS Code Integration**: Pre-configured tasks for seamless editor integration

## Quick Start

### Prerequisites

- Docker installed and running
- Python 3.8+ with PyYAML

### Installation

1. Build the Vale Docker container:
   ```bash
   cd docker/vale-adv
   chmod +x build.sh
   ./build.sh
   ```

2. Install dependencies:
   ```bash
   pip install pyyaml
   ```

### Basic Usage

#### Standalone CLI

```bash
# Check current directory (dry run)
python3 -m asciidoc_dita_toolkit.plugins.vale_flagger.cli --dry-run

# Check specific file and insert flags
python3 -m asciidoc_dita_toolkit.plugins.vale_flagger.cli --path docs/myfile.adoc

# Use configuration file
python3 -m asciidoc_dita_toolkit.plugins.vale_flagger.cli --config valeflag-config.yaml
```

#### Shell Wrapper

```bash
# Make wrapper executable
chmod +x bin/valeflag

# Use wrapper script
./bin/valeflag --dry-run
./bin/valeflag --path docs/
```

#### Via Console Script (after installation)

```bash
# If installed via pip
valeflag --dry-run
valeflag --path docs/
```

### Configuration

Create a `valeflag-config.yaml` file:

```yaml
vale:
  enabled_rules:
    - "Headings.Capitalization"
    - "Terms.Use"
    - "Spelling.Terms"
  disabled_rules:
    - "Style.Passive"

valeflag:
  flag_format: "// ADT-FLAG [{rule}]: {message}"
```

## How It Works

1. **Vale Execution**: Runs Vale via Docker with the asciidoctor-dita-vale ruleset
2. **Issue Detection**: Parses Vale's JSON output to identify violations
3. **Flag Insertion**: Inserts formatted comments above problematic lines
4. **File Updates**: Modifies source files with flags (unless in dry-run mode)

### Flag Format

Flags are inserted as AsciiDoc comments:

```adoc
// ADT-FLAG [Headings.Capitalization]: Heading should use sentence-style capitalization.
= this heading needs capitalization

// ADT-FLAG [Terms.Use]: Use 'repository' instead of 'repo'.
We store code in our repo.
```

## Command Line Options

```
--path, -p PATH           Target directory or file to check
--enable-rules, -e RULES  Comma-separated list of rules to enable
--disable-rules, -d RULES Comma-separated list of rules to disable
--dry-run, -n            Show issues without modifying files
--config, -c CONFIG      Path to configuration file (YAML format)
--flag-format FORMAT     Custom flag format string
--verbose, -v            Enable verbose output
```

## Integration

### VS Code

Pre-configured tasks are available in `.vscode/tasks.json`:

- **ValeFlagger: Check Current File** - Dry run on current file
- **ValeFlagger: Flag Current File** - Insert flags in current file
- **ValeFlagger: Check All Docs** - Dry run on entire project

Access via `Ctrl+Shift+P` → "Tasks: Run Task"

### Makefile

Available targets:

```bash
make valeflag-build    # Build Vale Docker container
make valeflag-check    # Run dry check on docs/
make valeflag-test     # Run unit tests
```

### ADT Integration

ValeFlagger integrates with the main ADT CLI system (when properly installed):

```bash
adt ValeFlagger --dry-run
adt ValeFlagger --path docs/ --verbose
```

## Available Rules

Common asciidoctor-dita-vale rules:

- **Headings.Capitalization** - Enforce sentence-style capitalization
- **Terms.Use** - Enforce preferred terminology
- **Links.External** - Check external link formatting
- **Spelling.Terms** - Check technical term spelling
- **Style.Passive** - Detect passive voice
- **Style.WordChoice** - Suggest better word choices

To see all available rules:
```bash
docker run --rm asciidoc-dita-toolkit/vale-adv ls-config
```

## Maintenance

### Removing Flags

To remove all flags from files:

```bash
find . -name "*.adoc" -exec sed -i '/^\/\/ ADT-FLAG/d' {} \;
```

### Updating Vale Rules

Rebuild the Docker container to get updated rules:

```bash
cd docker/vale-adv
./build.sh
```

## Troubleshooting

### Docker Not Found
- Ensure Docker Desktop is running
- Check `docker --version` works
- On Linux, ensure user is in docker group

### Vale Rules Not Found
- Rebuild container: `cd docker/vale-adv && ./build.sh`
- Check container has rules: `docker run --rm asciidoc-dita-toolkit/vale-adv ls-config`

### Import Errors
- Ensure you're in the project root
- Check PYTHONPATH includes project root
- Verify `__init__.py` files exist in all package directories

### No Flags Inserted
- Run with `--dry-run` first to see if issues are found
- Check file permissions
- Verify Vale is finding issues with direct Docker command

## Architecture

ValeFlagger consists of:

- **Core Class** (`vale_flagger.py`) - Main logic for Vale integration
- **CLI Module** (`cli.py`) - Command-line interface
- **Configuration** (`config.py`) - YAML configuration support
- **Plugin Integration** (`plugin.py`) - ADT plugin system integration
- **Docker Container** - Pre-configured Vale with asciidoctor-dita-vale rules

## Testing

Run the test suite:

```bash
python3 -m unittest tests.test_vale_flagger -v
```

Tests cover:
- Docker availability checking
- Vale execution and JSON parsing
- Flag formatting and insertion
- Configuration file handling
- Error handling scenarios

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

Part of the AsciiDoc DITA Toolkit - see main project license.
