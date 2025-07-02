# AsciiDoc DITA Toolkit GUI Guide

## Overview

The AsciiDoc DITA Toolkit GUI provides an intuitive, dialog-based interface for running plugins without needing to remember command-line syntax.

## Starting the GUI

After installing the toolkit:

```bash
asciidoc-dita-toolkit-gui
```

Or use the launcher scripts:
- **Linux/macOS**: `./launch-gui.sh`
- **Windows**: `launch-gui.bat`

## Interface Overview

### 1. Plugin Selection
- **Dropdown menu** at the top lists all available plugins
- **Description** appears below showing what the selected plugin does

### 2. Configuration Section

#### Target Selection
- **File**: Browse and select a single `.adoc` file to process
- **Directory**: Browse and select a directory to process
- Only one target type should be selected at a time

#### Mode Selection (Future Feature)
- **Review**: Preview changes without applying them
- **Interactive**: Approve each change individually  
- **Auto**: Apply all changes automatically
- **Guided**: Get detailed explanations

*Note: Current plugins (ContentType, EntityReference) run in automatic mode only. Interactive modes are planned for future versions.*

#### Options
- **Recursive**: Process all `.adoc` files in subdirectories
- **Dry run**: Preview mode (not yet supported by current plugins)

### 3. Action Buttons

#### Load Test Files
- Creates sample `.adoc` files for testing
- Files are copied to the selected directory (or current directory)
- Includes files with different issues to test the plugins

#### Run Plugin
- Executes the selected plugin with current settings
- Results appear in the Results panel below
- Plugin runs in a background thread to keep GUI responsive

#### Clear Results
- Clears the Results panel

### 4. Results Panel
- Shows real-time output from plugin execution
- Displays any errors or warnings
- Scrollable text area with monospace font for easy reading

### 5. Status Bar
- Shows current operation status
- Updates during plugin execution

## Step-by-Step Usage

### First Time Usage

1. **Launch the GUI**
   ```bash
   asciidoc-dita-toolkit-gui
   ```

2. **Load test files** (recommended for first time)
   - Click "Load Test Files" to get sample files
   - This creates 5 test files in your current directory

3. **Select a plugin**
   - Choose "ContentType" or "EntityReference" from the dropdown
   - Read the description to understand what it does

4. **Configure target**
   - Select the directory where test files were created
   - Check "Recursive" if you want to process subdirectories

5. **Run the plugin**
   - Click "Run Plugin"
   - Watch the results in the Results panel

### Working with Your Files

1. **Select your target**
   - **For a single file**: Use "Browse" next to "File"
   - **For a directory**: Use "Browse" next to "Directory"

2. **Choose appropriate options**
   - Check "Recursive" for directory processing with subdirectories
   - Leave "Dry run" checked if you want to preview (when supported)

3. **Run and review**
   - Click "Run Plugin"
   - Review the results in the Results panel
   - Check your files to see the changes

## Available Plugins

### ContentType Plugin
- **Purpose**: Adds `:_mod-docs-content-type:` labels to `.adoc` files
- **How it works**: Determines content type from filename prefix
- **Filename patterns**:
  - `proc_*` or `proc-*` → PROCEDURE
  - `con_*` or `con-*` → CONCEPT  
  - `ref_*` or `ref-*` → REFERENCE
  - `assembly_*` or `assembly-*` → ASSEMBLY
  - `snip_*` or `snip-*` → SNIPPET

### EntityReference Plugin
- **Purpose**: Converts HTML entity references to AsciiDoc attribute references
- **Examples**:
  - `&copy;` → `{copy}`
  - `&mdash;` → `{mdash}`
  - `&quot;` → `{quot}`

## Test Files Description

The "Load Test Files" button creates these sample files:

| File | Purpose | Expected Result |
|------|---------|----------------|
| `missing_content_type.adoc` | No content type attribute | ContentType plugin adds one |
| `empty_content_type.adoc` | Empty content type value | ContentType plugin fixes it |
| `commented_content_type.adoc` | Commented-out content type | ContentType plugin uncomments |
| `correct_procedure.adoc` | Already correct | No changes needed |
| `with_entities.adoc` | Contains HTML entities | EntityReference plugin converts them |

## Troubleshooting

### GUI Won't Start
- **Check Python installation**: `python3 --version`
- **Install tkinter** (Linux): `sudo apt install python3-tk`
- **Verify toolkit installation**: `pip show asciidoc-dita-toolkit`

### "No Plugin Selected" Error
- Select a plugin from the dropdown before clicking "Run Plugin"

### "No File or Directory" Error  
- Browse and select either a file OR a directory
- Make sure the selected path exists and is accessible

### Plugin Errors
- Check that target files are valid `.adoc` files
- Ensure you have write permissions to the target directory
- Review error messages in the Results panel

### Results Panel Shows No Output
- This is normal for some plugins that modify files without producing output
- Check your target files to see if changes were made
- Try using test files to verify plugin functionality

## Tips for Best Results

1. **Start with test files** to understand how plugins work
2. **Backup your files** before running plugins on important content
3. **Use descriptive filenames** that match the plugin's expected patterns
4. **Run one plugin at a time** to understand what each one does
5. **Check the Results panel** for any warnings or errors

## Getting Help

- **Command line help**: `asciidoc-dita-toolkit --help`
- **Plugin-specific help**: `asciidoc-dita-toolkit <plugin> --help`
- **GitHub Issues**: [Report bugs or request features](https://github.com/rolfedh/asciidoc-dita-toolkit/issues)
- **Documentation**: [Main README](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/README.md)

---

*The GUI makes the AsciiDoc DITA Toolkit accessible to users who prefer visual interfaces over command-line tools, while maintaining all the power and flexibility of the underlying plugins.*
