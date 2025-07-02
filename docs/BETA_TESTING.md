# Beta Testing Guide

🎉 **Welcome to beta testing for the AsciiDoc DITA Toolkit v0.1.8b2!**

This guide helps you test the **new ContentType interactive UI** and explore features using **included test files**.

## 📋 Quick Start

1. [Install the beta](#-installation-options) 
2. [Get test files](#-accessing-test-files)
3. [Test the new features](#-testing-the-contenttype-plugin)
4. [Report feedback](#-providing-feedback)

## 🚀 What's New in v0.1.8b2

### ContentType Plugin - Interactive UI

Completely redesigned with four operation modes:

- **Auto** - Automatically fixes all detected issues
- **Review** - Preview changes without applying them  
- **Interactive** - Approve each fix individually
- **Guided** - Get detailed explanations and recommendations

### Enhanced Detection

Now detects and fixes:
- Missing content type attributes
- Empty or invalid content type values  
- Commented-out content type lines
- Deprecated content type formats
- Misplaced content type attributes

## 📦 Installation Options

Choose your preferred installation method:

### PyPI (Recommended)

```bash
pip install asciidoc-dita-toolkit==0.1.8b2
asciidoc-dita-toolkit --version
```

### Docker (Zero Setup)

```bash
docker run --rm -v $(pwd):/workspace asciidoc-dita-toolkit:latest --help
```

## 📁 Accessing Test Files

Every installation includes comprehensive test files:

```bash
# List all test files
find-beta-files

# Copy files to current directory
cp "$(find-beta-files --path-only)"/*.adoc .

# Docker: Copy test files to host
docker run --rm -v $(pwd):/output asciidoc-dita-toolkit:latest sh -c \
  'cp $(find-beta-files --path-only)/*.adoc /output/'
```

## 🧪 Testing the ContentType Plugin

### Essential Commands

```bash
# See all options
asciidoc-dita-toolkit ContentType --help

# Basic testing modes
ContentType --mode review --file FILE        # Preview changes
ContentType --mode interactive --file FILE   # Approve each fix
ContentType --mode auto --file FILE          # Apply all fixes
ContentType --mode guided --file FILE        # Get explanations

# Directory operations
ContentType --mode auto --directory . --recursive --dry-run
```

### Quick Test Workflow

```bash
# 1. Get test files
cp "$(find-beta-files --path-only)"/*.adoc .

# 2. Try different modes
asciidoc-dita-toolkit ContentType --mode review --file missing_content_type.adoc
asciidoc-dita-toolkit ContentType --mode interactive --file empty_content_type.adoc
asciidoc-dita-toolkit ContentType --mode auto --file commented_content_type.adoc --dry-run
```

## 📋 Understanding Test Files

### Files with Issues (Test the Fixes)

| File | Issue | Expected Fix |
|------|-------|--------------|
| `missing_content_type.adoc` | No content type attribute | Adds `:_mod-docs-content-type: PROCEDURE` |
| `empty_content_type.adoc` | Empty value | Adds appropriate content type |
| `commented_content_type.adoc` | Commented out | Uncomments and fixes |
| `wrong_content_type.adoc` | Deprecated format | Updates to modern format |

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
- Are interactive prompts clear and helpful?
- Is the guided mode educational?
- Are error messages understandable?

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

1. **ContentType Interactive UI** - Intuitive and helpful?
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
cp "$(find-beta-files --path-only)"/*.adoc .
asciidoc-dita-toolkit EntityReference --file sample_with_entities.adoc
```

### General Testing
```bash
# Test all plugins on sample data
asciidoc-dita-toolkit EntityReference --recursive
asciidoc-dita-toolkit ContentType --mode review --directory .
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
    cp -r "$(find-beta-files --path-only)"/* ./test/
    asciidoc-dita-toolkit ContentType --mode auto --directory test/ --dry-run
```

### Docker in CI
```yaml  
- name: Test with Docker
  run: |
    docker run --rm -v $(pwd):/workspace asciidoc-dita-toolkit:latest sh -c \
      'cp -r $(find-beta-files --path-only)/* /workspace/test/ && \
       asciidoc-dita-toolkit ContentType --mode review --directory /workspace/test/'
```
</details>

<details>
<summary><strong>Troubleshooting</strong></summary>

**Files not found:**
```bash
find-beta-files
pip install --upgrade asciidoc-dita-toolkit==0.1.8b2
```

**Container issues:**
```bash
docker run --rm asciidoc-dita-toolkit:latest find-beta-files
```

**Permission errors:**
```bash
docker run --rm -v $(pwd):/output asciidoc-dita-toolkit:latest sh -c \
  'cp -r $(find-beta-files --path-only)/* /output/ && chmod -R 644 /output/*'
```
</details>

## 📚 Additional Resources

- [Main Documentation](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/README.md)
- [Contributing Guide](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/docs/CONTRIBUTING.md)  
- [GitHub Repository](https://github.com/rolfedh/asciidoc-dita-toolkit)

---

**Thank you for testing the AsciiDoc DITA Toolkit!** 🎉  
Your feedback helps make this tool better for the entire technical writing community.
