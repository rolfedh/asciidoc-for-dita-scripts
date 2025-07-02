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

Enhanced detection and fixing of:
- Missing content type attributes
- Empty or invalid content type values  
- Commented-out content type lines
- Misplaced content type attributes

### File Processing Options

Both plugins now support:
- Single file processing (`-f/--file`)
- Directory processing (`-d/--directory`)
- Recursive processing (enabled by default, disable with `-nr/--no-recursive`)

## 📦 Installation Options

Choose your preferred installation method:

### PyPI (Recommended)

```bash
pip install asciidoc-dita-toolkit==0.1.8b2
adt --version
```

### Docker (Zero Setup)

```bash
docker run --rm -v $(pwd):/workspace asciidoc-dita-toolkit:latest --help
```

## 📁 Accessing Test Files

Create test files manually or copy from examples:

```bash
# Create test directory
mkdir test_files && cd test_files

# Copy existing .adoc files from your project
# Or create test files as shown in the examples below
```

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
# 1. Create test files (see examples below)
mkdir test_files && cd test_files

# 2. Test single file
adt ContentType -f missing_content_type.adoc

# 3. Test directory processing (now recursive by default)
adt ContentType .
```

## 📋 Understanding Test Files

### Files with Issues (Test the Fixes)

| File | Issue | Expected Fix |
|------|-------|--------------|
| `missing_content_type.adoc` | No content type attribute | Adds `:_mod-docs-content-type: PROCEDURE` |
| `empty_content_type.adoc` | Empty value | Adds appropriate content type |
| `commented_content_type.adoc` | Commented out | Uncomments and fixes |

### Files that Should Pass (No Changes Expected)

| File | Reason |
|------|--------|
| `correct_procedure.adoc` | Valid `:_mod-docs-content-type: PROCEDURE` |
| `correct_concept.adoc` | Valid `:_mod-docs-content-type: CONCEPT` |
| `correct_reference.adoc` | Valid `:_mod-docs-content-type: REFERENCE` |


## 🔍 What to Test & Report

Focus your testing on these areas:

### 🎯 Detection Accuracy
- Does the plugin correctly identify issues?
- Any false positives or missed problems?

### 🛠️ Fix Quality  
- Are automatic fixes appropriate and correct?
- Does formatting remain proper after fixes?

### 👤 User Experience
- Are error messages clear and helpful?
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

1. **File processing accuracy** - Does it correctly identify and fix issues?
2. **Real-world content** - Performance on your actual files?
3. **Workflow integration** - Fits your existing processes?
4. **Error handling** - Clear and actionable messages?

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
