# Tab Completion for adt CLI

The AsciiDoc DITA Toolkit supports intelligent tab completion for bash shells, making it easier to discover and use available modules and options.

## Automatic Installation

Tab completion is automatically installed when you first run the `adt` command. You'll see a message like:

```
✅ Tab completion installed! Try: adt <TAB><TAB>
   (Restart your shell if completion doesn't work immediately)
```

## Manual Installation

If automatic installation doesn't work, you can install completion manually:

```bash
# Install for current user
make install-completion

# Or run the script directly  
./scripts/install-completion.sh

# For system-wide installation (requires sudo)
sudo ./scripts/install-completion.sh --system
```

## Usage Examples

Once installed, you can use tab completion in these ways:

### Module Name Completion
```bash
adt <TAB><TAB>                    # Shows all available modules
adt User<TAB>                     # Completes to "UserJourney"
adt Content<TAB>                  # Completes to "ContentType"
adt Cross<TAB>                    # Completes to "CrossReference"
```

### Module Options
```bash
adt ContentType <TAB><TAB>        # Shows module options (-f, -r, -d, -v, -h)
adt ValeFlagger <TAB><TAB>        # Shows ValeFlagger-specific options
```

### UserJourney Subcommands
```bash
adt journey <TAB><TAB>            # Shows: start, resume, continue, status, list, cleanup
adt journey start <TAB><TAB>      # Shows journey options (-n, --name, etc.)
```

### File and Directory Completion
```bash
adt ContentType -f <TAB>          # Completes .adoc files
adt CrossReference -d <TAB>       # Completes directory names
adt ValeFlagger -c <TAB>          # Completes config files (.yaml, .yml, .json)
```

### Journey Name Completion
```bash
adt journey resume -n <TAB>       # Completes with existing journey names
adt journey status -n <TAB>       # Completes with existing journey names
```

## Available Completions

### Base Commands
- `--help`, `--version`, `--list-modules`, `--suppress-warnings`, `--show-warnings`

### Modules
- `ArchiveUnusedFiles`
- `ContentType`
- `ContextAnalyzer` 
- `ContextMigrator`
- `CrossReference`
- `DirectoryConfig`
- `EntityReference`
- `ExampleBlock`
- `UserJourney`
- `ValeFlagger`

### Common Module Options
- `-f, --file` - Process specific file
- `-r, --recursive` - Process recursively 
- `-d, --directory` - Specify directory
- `-v, --verbose` - Enable verbose output
- `-h, --help` - Show module help

### ValeFlagger-Specific Options
- `--enable-rules` - Enable specific rules
- `--disable-rules` - Disable specific rules
- `--config` - Configuration file
- `--execute-changes` - Actually modify files

### UserJourney Commands
- `start` - Create new workflow
- `resume` - Resume existing workflow
- `continue` - Execute next module
- `status` - Show workflow status
- `list` - List all workflows
- `cleanup` - Delete workflows

## Dynamic Module Discovery

The completion system dynamically discovers available modules from your installed package, so it automatically stays up-to-date with new modules or changes.

If dynamic discovery fails, it falls back to a static list of known modules.

## Troubleshooting

### Completion Not Working
1. **Restart your shell** - New completions require a fresh shell session
2. **Source manually**: `source ~/.local/share/bash-completion/completions/adt`
3. **Check installation**: Look for `~/.local/share/bash-completion/completions/adt`
4. **Reinstall**: Run `make install-completion` again

### No Dynamic Module Discovery
If you see static fallback modules instead of your actual modules:
1. Ensure `adt` command is in your PATH
2. Check that the package is properly installed: `pip list | grep asciidoc-dita-toolkit`
3. Test module listing: `adt --list-modules`

### Permission Issues
If installation fails with permission errors:
```bash
# Install for user only (default)
./scripts/install-completion.sh

# Or use make target
make install-completion
```

## Technical Details

The completion system consists of:

1. **Bash completion script**: `scripts/adt-completion.bash`
2. **Python completion helper**: `asciidoc_dita_toolkit.adt_core.completion`
3. **Dynamic module discovery**: Uses the same system as `adt --list-modules`
4. **Automatic installation**: Triggered on first `adt` command execution

The completion script intelligently handles:
- Context-aware completions based on command position
- File type filtering (.adoc, .yaml, .yml, .json)
- Journey name discovery from existing workflows
- Fallback to static lists when dynamic discovery fails

## Shell Support

Currently supported shells:
- **Bash** - Full support with intelligent completion
- **Zsh** - Basic support via bash compatibility mode

Future shell support planned:
- Native Zsh completion
- Fish shell completion