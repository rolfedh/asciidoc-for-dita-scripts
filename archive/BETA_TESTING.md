# Beta Testing Guide

🎉 **Welcome to beta testing for the AsciiDoc DITA Toolkit v0.1.9b1!**

This guide helps you test the **modernized CLI and enhanced ContentType plugin** using **included test files**.

## 📋 Quick Start

1. [Install the beta](#-installation) 
2. [Get test files](#-accessing-test-files)
3. [Test the new features](#-testing-the-contenttype-plugin)
4. [Report feedback](#-providing-feedback)

## 🚀 What's New in v0.1.9b1

### CLI Modernization

Major improvements to user experience:
- **Auto-detection** of files vs directories - no more `-f` or `-d` flags needed
- **Recursive processing by default** for directories
- **Simple command structure**: `adt ContentType <file_or_dir>`
- **Non-recursive option** with `-nr/--no-recursive` flag

### ContentType Plugin Improvements

Enhanced with comprehensive new features:
- **Smart content type analysis** based on title style, filename, and content patterns
- **Interactive prompts** with intelligent pre-selection when content type cannot be determined
- **Deprecated attribute conversion** (`:_content-type:` and `:_module-type:` → `:_mod-docs-content-type:`)
- **Filename-based auto-detection** for all standard prefixes
- **Clear visual feedback** with colored output and separator lines
- **Empty attribute handling** with user prompts

## 📦 Installation

Install the beta version via PyPI:

```bash
pip install asciidoc-dita-toolkit==0.1.9b1
adt --version
```

> **💡 Note:** Docker installation is also available but PyPI is recommended for beta testing as it's simpler and provides better debugging information.

## 📁 Accessing Test Files

**Great news!** Test files are now included with the PyPI package. You have several options:

### Option 1: Use the built-in test files utility (Recommended)

```bash
# List all available test files
adt-test-files list

# Copy test files to your current directory
adt-test-files copy ./my_test_files

# Get the path to the test files directory
adt-test-files path
```

### Option 2: Copy test files programmatically

```python
from asciidoc_dita_toolkit.test_files import copy_test_files_to_directory

# Copy test files to a directory of your choice
copy_test_files_to_directory("./my_test_files")
```

### Option 3: Clone the repository (for developers)

```bash
# If you want the full development environment
git clone https://github.com/rolfedh/asciidoc-dita-toolkit.git
cd asciidoc-dita-toolkit/test_files/
```

> **💡 Note:** The `restore_test_files.sh` script is only available in the repository. PyPI users should copy fresh test files for each testing session using `adt-test-files copy <directory>`.

## 🧪 Testing the ContentType Plugin

### Essential Commands

```bash
# See all options
adt ContentType --help

# Process single file (auto-detected)
adt ContentType FILE

# Process directory (recursive by default, auto-detected)
adt ContentType DIR

# Process directory non-recursively  
adt ContentType DIR -nr

# Process current directory (default, recursive)
adt ContentType .
```

### Quick Test Workflow

**For PyPI users** (now with included test files):

```bash
# 1. Copy test files to your working directory
adt-test-files copy ./my_test_files
cd my_test_files

# 2. Test single file processing (auto-detection)
adt ContentType missing_content_type.adoc

# 3. Test directory processing (recursive by default)
adt ContentType .

# 4. Test interactive prompts (select option 1-7 when prompted)
adt ContentType ignore_comments.adoc

# 5. Test filename auto-detection  
adt ContentType proc_example.adoc

# 6. Test smart content type analysis
adt ContentType installing_docker.adoc

# 7. For another test round, copy fresh files
cd .. && adt-test-files copy ./my_test_files_2
```

**For repository users** (with restore script):

```bash
# 1. Use included test files
cd test_files/

# 2-6. Same testing steps as above

# 7. IMPORTANT: Reset test files for another round
cd .. && ./restore_test_files.sh
```

> **⚠️ Production Safety Reminder:** When testing on your actual documentation repository, always:
> * **Create a working branch** (`git checkout -b test-content-type`)
> * **Review all changes carefully** before committing

## 📋 Understanding Test Files

The included test files cover all ContentType plugin scenarios:

### Files Requiring Fixes

| File | Issue | Expected Behavior |
|------|-------|------------------|
| `missing_content_type.adoc` | No content type attribute | Interactive prompt to select type |
| `empty_content_type.adoc` | Empty `:_mod-docs-content-type:` | Interactive prompt to select type |
| `commented_content_type.adoc` | Only commented-out content type | Interactive prompt to select type |
| `deprecated_test.adoc` | Uses `:_content-type: CONCEPT` | Auto-converts to `:_mod-docs-content-type: CONCEPT` |
| `proc_test.adoc` | Uses `:_module-type: REFERENCE` | Auto-converts to `:_mod-docs-content-type: REFERENCE` |

### Files with Auto-Detection

| File | Filename Pattern | Expected Auto-Detection |
|------|------------------|------------------------|
| `assembly_example.adoc` | `assembly_` prefix | Adds `:_mod-docs-content-type: ASSEMBLY` |
| `proc_example.adoc` | `proc_` prefix | Adds `:_mod-docs-content-type: PROCEDURE` |
| `con_example.adoc` | `con_` prefix | Adds `:_mod-docs-content-type: CONCEPT` |
| `ref_example.adoc` | `ref_` prefix | Adds `:_mod-docs-content-type: REFERENCE` |
| `snip_example.adoc` | `snip_` prefix | Adds `:_mod-docs-content-type: SNIPPET` |

### Smart Analysis Test Files

| File | Analysis Target | Expected Smart Detection |
|------|----------------|-------------------------|
| `installing_docker.adoc` | Gerund title + procedure patterns | Should suggest PROCEDURE |
| `docker_commands.adoc` | Reference indicators | Should suggest REFERENCE |
| `what_is_containerization.adoc` | Concept indicators | Should suggest CONCEPT |
| `docker_guide_assembly.adoc` | Assembly patterns | Should suggest ASSEMBLY |

### Files Already Correct

| File | Reason |
|------|--------|
| `correct_procedure.adoc` | Has valid `:_mod-docs-content-type: PROCEDURE` |

> **� Between Tests:** Run `./restore_test_files.sh` to reset test files to their original state for consistent results.


## 🔍 What to Test & Report

Focus your testing on these areas:

### Detection Accuracy
- Does the plugin correctly identify missing/empty/deprecated content types?
- Does filename-based auto-detection work for all prefixes (`assembly_`, `proc_`, `con_`, `ref_`, `snip_`)?
- Are interactive prompts triggered appropriately?
- Any false positives or missed problems?

### Fix Quality  
- Are deprecated attribute conversions correct?
- Does interactive content type selection work properly?
- Are auto-detected content types appropriate for filenames?
- Does formatting remain proper after fixes?

### User Experience
- Are interactive prompts clear and easy to use?
- Is the colored output helpful and readable?
- Are separator lines improving readability?
- Does the output clearly show what was changed?
- Is the CLI intuitive to use?

### Performance
- How does it handle large files?
- Performance with complex AsciiDoc features?
- Speed on your real-world content?



## 📝 Providing Feedback

**[Create a GitHub issue](https://github.com/rolfedh/asciidoc-dita-toolkit/issues)** with your feedback using this template:

```markdown
## Beta Testing Feedback - v0.1.9b1

**Setup:** [PyPI/Docker] | [OS] | [Python version]
**Plugin:** [ContentType/EntityReference/Other]

### ✅ What Worked Well
- List things that worked as expected

### ❌ Issues Found  
- Describe problems with sample files/commands to reproduce

### 💡 Suggestions
- Ideas for improvements

### 📊 Quick Rating
- Detection accuracy: [Good/Fair/Poor]
- Fix quality: [Good/Fair/Poor]
- User experience: [Good/Fair/Poor]
- Performance: [Good/Fair/Poor]

**Additional Comments:** [Your detailed feedback]
```

## 🎯 Priority Testing Areas

We especially need feedback on:

1. **Interactive prompts** - Are the content type options clear? Is the selection process intuitive?
2. **Filename auto-detection** - Does it correctly identify content types from filename prefixes?
3. **Deprecated attribute conversion** - Are conversions accurate and preserve content?
4. **Visual feedback** - Is the colored output and separator formatting helpful?
5. **Real-world content** - Performance and accuracy on your actual files?
6. **Test file workflow** - Is the backup/restore system useful for testing?

## 📅 Beta Timeline

- **Beta period**: 2-4 weeks (launched July 2025)
- **Feedback deadline**: Late July 2025  
- **Final release**: Early August 2025

## 📚 Additional Resources

- [Main Documentation](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/README.md)
- [Contributing Guide](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/docs/CONTRIBUTING.md)  
- [GitHub Repository](https://github.com/rolfedh/asciidoc-dita-toolkit)

---

**Thank you for testing the AsciiDoc DITA Toolkit!** 🎉  
Your feedback helps make this tool better for the entire technical writing community.
