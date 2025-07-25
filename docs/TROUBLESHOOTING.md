# Troubleshooting Guide

This guide helps resolve common issues when installing and using the AsciiDoc DITA Toolkit.

## Installation Issues

### "Failed to load module" Errors with "No module named 'modules'"

**Symptoms:**
```
Failed to load module ContentType: No module named 'modules'
Failed to load module DirectoryConfig: No module named 'modules'
Failed to load module EntityReference: No module named 'modules'
```

**Root Cause:**
This error occurs when you have conflicting Python packages installed. Specifically, an old package called `adt-core` or other legacy ADT packages are installed alongside the current `asciidoc-dita-toolkit` package. These old packages provide entry points that reference obsolete import paths.

**Solution:**

1. **Identify conflicting packages:**
   ```bash
   # List all ADT-related packages
   pip list | grep -i asciidoc
   pip list | grep -i dita
   pip list | grep -i adt
   ```

2. **Remove legacy packages:**
   ```bash
   # Common legacy package names to remove
   pip uninstall adt-core
   pip uninstall adt
   pip uninstall asciidoc-dita
   pip uninstall dita-toolkit
   ```

   **Note:** For detailed upgrade instructions from `adt-core`, see the [Upgrading section](#upgrading-from-adt-core-to-asciidoc-dita-toolkit) below.

3. **Clear package cache:**
   ```bash
   pip cache purge
   ```

4. **Reinstall the current package:**
   ```bash
   pip install --upgrade asciidoc-dita-toolkit
   ```

5. **Verify the fix:**
   ```bash
   adt --help
   ```

**Advanced Diagnosis:**
To see which packages are providing conflicting entry points:
```bash
python3 -c "
import importlib.metadata
for dist in importlib.metadata.distributions():
    try:
        eps = dist.entry_points
        adt_eps = eps.select(group='adt.modules') if hasattr(eps, 'select') else eps.get('adt.modules', [])
        if adt_eps:
            print(f'Package: {dist.metadata[\"Name\"]} v{dist.version}')
            for ep in adt_eps:
                print(f'  {ep.name}: {ep.value}')
    except: pass
"
```

This will show you exactly which packages are providing `adt.modules` entry points and help identify conflicts.

### Multiple Package Versions

**Symptoms:**
- Different behavior when running `adt` vs `python -m asciidoc_dita_toolkit`
- Inconsistent plugin availability
- Version mismatches

**Solution:**

1. **Check installation locations:**
   ```bash
   # Find where adt command is installed
   which adt
   type adt

   # Check user vs system installations
   pip list --user | grep asciidoc
   pip list | grep asciidoc
   ```

2. **Clean up all installations:**
   ```bash
   # Remove from user space
   pip uninstall --user asciidoc-dita-toolkit

   # Remove from system (may need sudo)
   pip uninstall asciidoc-dita-toolkit
   ```

3. **Fresh installation:**
   ```bash
   # Install to user space (recommended)
   pip install --user asciidoc-dita-toolkit

   # Or install system-wide
   sudo pip install asciidoc-dita-toolkit
   ```

### Command Not Found

**Symptoms:**
```
adt: command not found
```

**Solution:**

1. **Check if package is installed:**
   ```bash
   pip show asciidoc-dita-toolkit
   ```

2. **Check PATH configuration:**
   ```bash
   # Find where scripts are installed
   python -m site --user-base

   # Add to PATH if needed (add to ~/.bashrc or ~/.profile)
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. **Alternative execution methods:**
   ```bash
   # Try these alternatives if 'adt' command is not found:

   # Option 1: Direct module execution
   python -m asciidoc_dita_toolkit.adt_core --help

   # Option 2: If package supports top-level execution
   python -m asciidoc_dita_toolkit --help

   # Option 3: Using the full package name (if available)
   asciidoc-dita-toolkit --help
   ```

### Upgrading from adt-core to asciidoc-dita-toolkit

**Important:** If you previously had the `adt-core` package installed, you should remove it before installing the new package to avoid conflicts.

**Symptoms of conflict:**
- "No module named 'modules'" errors
- Plugin discovery failures
- Entry point conflicts

**Upgrade Steps:**

1. **Check for old package:**
   ```bash
   # Check if old package exists
   pip list | grep adt-core
   ```

2. **Remove old package first:**
   ```bash
   # If found, remove old package
   pip uninstall adt-core

   # Also remove any other legacy ADT packages
   pip uninstall adt asciidoc-dita dita-toolkit
   ```

3. **Clean installation:**
   ```bash
   # Clear package cache to avoid conflicts
   pip cache purge

   # Install new package
   pip install asciidoc-dita-toolkit
   ```

**One-liner for convenience:**
```bash
pip uninstall adt-core -y && pip cache purge && pip install asciidoc-dita-toolkit
```

**Verify successful upgrade:**
```bash
# Should work without errors
adt --help
adt --list-plugins
```

## Runtime Issues

### Plugin Not Found

**Symptoms:**
- Plugin appears in `adt --list-plugins` but fails when executed
- "Plugin not found" errors

**Solution:**

1. **Verify plugin installation:**
   ```bash
   adt --list-plugins
   ```

2. **Check plugin-specific help:**
   ```bash
   adt PluginName --help
   ```

3. **Run with verbose output:**
   ```bash
   adt PluginName -v [other options]
   ```

### Configuration Issues

**Symptoms:**
- "Developer config file not found" warnings
- "Failed to initialize ModuleSequencer: Error loading configuration: Developer config file not found: .adt-modules.json"
- Modules not initializing properly

**Solution:**

1. **Check for configuration files:**
   ```bash
   # Look for developer config
   ls -la .adt-modules.json

   # Look for user config
   ls -la ~/.adt-user-config.json
   ls -la .adt-user-config.json
   ```

2. **Create the required developer configuration file:**
   ```bash
   # Create .adt-modules.json with default configuration
   cat > .adt-modules.json << 'EOF'
   {
     "version": "1.0",
     "modules": [
       {
         "name": "DirectoryConfig",
         "required": true,
         "version": "~1.0.0",
         "dependencies": [],
         "init_order": 1,
         "config": {
           "scan_depth": 5,
           "exclude_patterns": ["*.tmp", "*.log"]
         }
       },
       {
         "name": "EntityReference",
         "required": true,
         "version": ">=1.2.0",
         "dependencies": ["DirectoryConfig"],
         "init_order": 2,
         "config": {
           "timeout_seconds": 30,
           "cache_size": 1000
         }
       },
       {
         "name": "ContentType",
         "required": false,
         "version": ">=2.0.0",
         "dependencies": ["EntityReference"],
         "init_order": 3,
         "config": {
           "cache_enabled": true,
           "supported_types": ["text", "image", "video"]
         }
       },
       {
         "name": "ExampleBlock",
         "required": false,
         "version": ">=1.0.0",
         "dependencies": ["DirectoryConfig"],
         "init_order": 4,
         "config": {
           "interactive": true,
           "verbose": false
         }
       },
       {
         "name": "ArchiveUnusedFiles",
         "required": false,
         "version": ">=1.0.0",
         "dependencies": [],
         "init_order": 5,
         "config": {
           "scan_dirs": ["./modules", "./modules/rn", "./assemblies"],
           "archive_dir": "./archive",
           "archive": false
         }
       }
     ],
     "global_config": {
       "max_retries": 3,
       "log_level": "INFO"
     }
   }
   EOF
   ```

3. **Alternative: Download the default configuration:**
   ```bash
   # Download the default configuration from the repository
   curl -sSL https://raw.githubusercontent.com/rolfedh/asciidoc-dita-toolkit/HEAD/.adt-modules.json -o .adt-modules.json
   ```

4. **Verify the fix:**
   ```bash
   adt --help
   ```

**Note:** This configuration file should be included automatically in newer versions of the package. If you're still encountering this issue with the latest version, please report it as a bug.

## Getting Help

### Diagnostic Information

When reporting issues, please include:

1. **Version information:**
   ```bash
   adt --version
   python --version
   pip show asciidoc-dita-toolkit
   ```

2. **Environment information:**
   ```bash
   which adt
   echo $PATH
   pip list | grep -i asciidoc
   ```

3. **Plugin status:**
   ```bash
   adt --list-plugins
   ```

4. **Error output:**
   Run the failing command with verbose output and include the full error message.

### Common Command Patterns

```bash
# Get help
adt --help
adt PluginName --help

# List all available plugins
adt --list-plugins

# Process files with specific plugins
adt ContentType -r                    # Process all .adoc files recursively
adt EntityReference -f myfile.adoc    # Process specific file
adt CrossReference -d docs/           # Process files in docs/ directory

# Verbose output for debugging
adt PluginName -v [other options]
```

### Support Resources

- **GitHub Issues:** https://github.com/rolfedh/asciidoc-dita-toolkit/issues
- **Documentation:** https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/docs/
- **User Guide:** Check the `user-guide/` directory in the repository

When opening an issue, please include the diagnostic information mentioned above and a clear description of what you were trying to do when the problem occurred.
