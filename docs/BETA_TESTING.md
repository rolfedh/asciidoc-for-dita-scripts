# Beta Testing Guide

🎉 **Welcome to beta testing for the AsciiDoc DITA Toolkit v0.1.8b2!**

This guide helps you test the **new ContentType interactive UI** and explore features using **included test files**.

## 📋 Quick Start

1. [Install the beta](#-installation-options) 
2. [Get test files](#-accessing-test-files)
3. [Test the new features](#-testing-the-contenttype-plugin)
4. [Report feedback](#-providing-feedback)

## 🚀 What's New in v0.1.8b2

### ContentType Plugin Improvements

Enhanced with comprehensive new features:
- **Interactive prompts** when content type cannot be determined
- **Deprecated attribute conversion** (`:_content-type:` and `:_module-type:` → `:_mod-docs-content-type:`)
- **Filename-based auto-detection** for all standard prefixes
- **Clear visual feedback** with colored output and separator lines
- **Empty attribute handling** with user prompts

### File Processing Enhancements

- **Recursive processing by default** for directories
- **Simplified command structure** - no more `--directory` flag needed
- **Non-recursive option** with `-nr/--no-recursive` flag
- **Comprehensive test file suite** with backup and restore system

## 📦 Installation

Install the beta version via PyPI:

```bash
pip install asciidoc-dita-toolkit==0.1.8b2
adt --version
```

> **💡 Note:** Docker installation is also available but PyPI is recommended for beta testing as it's simpler and provides better debugging information.

## 📁 Accessing Test Files

The toolkit includes a comprehensive set of test files for thorough testing:

```bash
# Test files are included in the repository
cd asciidoc-dita-toolkit/test_files/

# Or create your own test directory
mkdir my_test_files && cd my_test_files
```

**Complete test suite available at:** `test_files/` directory with backup system via `restore_test_files.sh`

> **💡 Important:** Always run `./restore_test_files.sh` between test runs to reset files to their original state for consistent testing.

## 🧪 Testing the ContentType Plugin

### Essential Commands

```bash
# See all options
adt ContentType --help

# Process single file
adt ContentType -f FILE

# Process directory (recursive by default)
adt ContentType DIR

# Process directory non-recursively  
adt ContentType DIR -nr

# Process current directory (default, recursive)
adt ContentType
```

### Quick Test Workflow

```bash
# 1. Use included test files
cd test_files/

# 2. Test single file processing
adt ContentType -f missing_content_type.adoc

# 3. Test directory processing (recursive by default)
adt ContentType .

# 4. Test interactive prompts (select option 1-7 when prompted)
adt ContentType ignore_comments.adoc

# 5. Test filename auto-detection  
adt ContentType proc_example.adoc

# 6. IMPORTANT: Reset test files for another round
cd .. && ./restore_test_files.sh

# 7. Repeat tests as needed
```

> **⚠️ Production Safety Reminder:** When testing on your actual documentation repository, always:
> * **Create a working branch** (`git checkout -b test-content-type`)
> * **Review all changes carefully** before committing

## 📋 Understanding Test Files

The included test files cover all ContentType plugin scenarios:

### 🔧 Files Requiring Fixes

| File | Issue | Expected Behavior |
|------|-------|------------------|
| `missing_content_type.adoc` | No content type attribute | Interactive prompt to select type |
| `empty_content_type.adoc` | Empty `:_mod-docs-content-type:` | Interactive prompt to select type |
| `commented_content_type.adoc` | Only commented-out content type | Interactive prompt to select type |
| `deprecated_test.adoc` | Uses `:_content-type: CONCEPT` | Auto-converts to `:_mod-docs-content-type: CONCEPT` |
| `proc_test.adoc` | Uses `:_module-type: REFERENCE` | Auto-converts to `:_mod-docs-content-type: REFERENCE` |
| `empty_deprecated.adoc` | Empty `:_content-type:` | Interactive prompt to select type |

### 🤖 Files with Auto-Detection

| File | Filename Pattern | Expected Auto-Detection |
|------|------------------|------------------------|
| `assembly_example.adoc` | `assembly_` prefix | Adds `:_mod-docs-content-type: ASSEMBLY` |
| `proc_example.adoc` | `proc_` prefix | Adds `:_mod-docs-content-type: PROCEDURE` |
| `con_example.adoc` | `con_` prefix | Adds `:_mod-docs-content-type: CONCEPT` |
| `ref_example.adoc` | `ref_` prefix | Adds `:_mod-docs-content-type: REFERENCE` |
| `snip_example.adoc` | `snip_` prefix | Adds `:_mod-docs-content-type: SNIPPET` |

### ✅ Files Already Correct

| File | Reason |
|------|--------|
| `correct_procedure.adoc` | Has valid `:_mod-docs-content-type: PROCEDURE` |

### 🔧 Utility Files

| File | Purpose |
|------|---------|
| `with_entities.adoc` | For testing EntityReference plugin |
| `ignore_comments.adoc` | Generic file for interactive testing |


## 🔍 What to Test & Report

Focus your testing on these areas:

> **🔄 Between Tests:** Run `./restore_test_files.sh` to reset test files to their original state for consistent results.

### 🎯 Detection Accuracy
- Does the plugin correctly identify missing/empty/deprecated content types?
- Does filename-based auto-detection work for all prefixes (`assembly_`, `proc_`, `con_`, `ref_`, `snip_`)?
- Are interactive prompts triggered appropriately?
- Any false positives or missed problems?

### 🛠️ Fix Quality  
- Are deprecated attribute conversions correct?
- Does interactive content type selection work properly?
- Are auto-detected content types appropriate for filenames?
- Does formatting remain proper after fixes?

### 👤 User Experience
- Are interactive prompts clear and easy to use?
- Is the colored output helpful and readable?
- Are separator lines improving readability?
- Does the output clearly show what was changed?
- Is the CLI intuitive to use?

### ⚡ Performance
- How does it handle large files?
- Performance with complex AsciiDoc features?
- Speed on your real-world content?



## 📝 Providing Feedback

**[Create a GitHub issue](https://github.com/rolfedh/asciidoc-dita-toolkit/issues)** with your feedback using this template:

```markdown
## Beta Testing Feedback - v0.1.8b2

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

## � Beta Timeline

- **Beta period**: 2-4 weeks (launched July 2025)
- **Feedback deadline**: Late July 2025  
- **Final release**: Early August 2025

---

## 🧪 Additional Testing

<details>
<summary><strong>Testing Other Plugins</strong></summary>

### EntityReference Plugin
```bash
# Test HTML entity reference conversion
adt EntityReference -f sample_with_entities.adoc
```

### General Testing
```bash
# Test all plugins on sample data
adt EntityReference
adt ContentType .
```
</details>

<details>
<summary><strong>Create Custom Test Cases</strong></summary>

#### Missing Content Type
```asciidoc
= Your Topic Title

Content without content type attribute.
```

#### Empty Content Type  
```asciidoc
:_mod-docs-content-type:
= Your Topic Title

Content with empty content type.
```

#### Commented Content Type
```asciidoc
//:_mod-docs-content-type: PROCEDURE
= Your Topic Title

Content with commented-out content type.
```
</details>

<details>
<summary><strong>CI/CD Integration Examples</strong></summary>

### GitHub Actions
```yaml
- name: Test with beta files
  run: |
    pip install asciidoc-dita-toolkit==0.1.8b2
    adt ContentType test/
```

### Docker in CI
```yaml  
- name: Test with Docker
  run: |
    docker run --rm -v $(pwd):/workspace asciidoc-dita-toolkit:latest \
      adt ContentType /workspace/test/
```
</details>

<details>
<summary><strong>Troubleshooting</strong></summary>

**Files not found:**
```bash
adt --help
pip install --upgrade asciidoc-dita-toolkit==0.1.8b2
```

**Container issues:**
```bash
docker run --rm asciidoc-dita-toolkit:latest adt --help
```

**Permission errors:**
```bash
# Ensure files are writable
chmod 644 *.adoc
```
</details>

## 📚 Additional Resources

- [Main Documentation](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/README.md)
- [Contributing Guide](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/docs/CONTRIBUTING.md)  
- [GitHub Repository](https://github.com/rolfedh/asciidoc-dita-toolkit)

---

**Thank you for testing the AsciiDoc DITA Toolkit!** 🎉  
Your feedback helps make this tool better for the entire technical writing community.
