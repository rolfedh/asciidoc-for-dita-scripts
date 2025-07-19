# Beta Testing Guide - ContentType Plugin v0.1.7b1

🎉 **Welcome to the beta testing program for the new interactive ContentType plugin!**

We've completely reimplemented the ContentType plugin with a powerful new interactive UI framework that can both detect and automatically fix content type issues in your AsciiDoc files.

## 🚀 What's New in This Beta

### Interactive UI Framework

- **Auto mode**: Automatically fixes detected issues
- **Review mode**: Shows what would be changed without applying fixes
- **Interactive mode**: Prompts you to approve each fix individually
- **Guided mode**: Provides detailed explanations and recommendations

### Enhanced Detection

The plugin now detects and can fix:

- ✅ Missing content type attributes
- ✅ Empty or invalid content type values  
- ✅ Commented-out content type lines
- ✅ Deprecated content type formats
- ✅ Misplaced content type attributes

## 📦 How to Install the Beta

### Option 1: Docker (Recommended - No Setup Required)

```bash
# Pull and test the beta version
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:beta --help

# Test on your AsciiDoc files
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:beta \
  ContentType --mode interactive --file your_file.adoc

# Other useful Docker commands:
# Auto-fix mode
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:beta \
  ContentType --mode auto --file your_file.adoc

# Process directory recursively
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:beta \
  ContentType --mode auto --directory /workspace --recursive

# Dry run to see what would be changed
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:beta \
  ContentType --mode auto --file your_file.adoc --dry-run
```

### Option 2: PyPI Installation

```bash
# Install the beta version
pip install asciidoc-dita-toolkit==0.1.7b1

# Verify installation
asciidoc-dita-toolkit --version
```

## 🧪 Testing Instructions

### Command Reference

First, check the available options:
```bash
# See all available options
asciidoc-dita-toolkit ContentType --help

# Available modes: auto, review, interactive, guided
# File options: --file FILE or --directory DIRECTORY
# Additional flags: --recursive, --dry-run, --batch, --quiet, --verbose
```

### Basic Testing

Test the different interaction modes on your AsciiDoc files:

```bash
# 1. Review mode - See what issues are detected (no changes made)
asciidoc-dita-toolkit ContentType --mode review --file your_file.adoc

# 2. Interactive mode - Approve each fix individually
asciidoc-dita-toolkit ContentType --mode interactive --file your_file.adoc

# 3. Auto mode - Automatically apply all recommended fixes
asciidoc-dita-toolkit ContentType --mode auto --file your_file.adoc

# 4. Guided mode - Get detailed explanations
asciidoc-dita-toolkit ContentType --mode guided --file your_file.adoc

# 5. Process entire directory recursively
asciidoc-dita-toolkit ContentType --mode auto --directory . --recursive

# 6. Dry run - See what would be changed without making changes
asciidoc-dita-toolkit ContentType --mode auto --file your_file.adoc --dry-run
```

### Test Scenarios
Please test these specific scenarios if possible:

#### ✅ Missing Content Type
Create a file without any content type definition:
```asciidoc
= Your Topic Title

Content goes here.
```

#### ✅ Empty Content Type
Create a file with an empty content type:
```asciidoc
:_mod-docs-content-type:
= Your Topic Title

Content goes here.
```

#### ✅ Commented Content Type
Create a file with a commented-out content type:
```asciidoc
//:_mod-docs-content-type: PROCEDURE
= Your Topic Title

Content goes here.
```

#### ✅ Misplaced Content Type
Create a file where the content type appears after the title:
```asciidoc
= Your Topic Title
:_mod-docs-content-type: PROCEDURE

Content goes here.
```

## 🐛 What to Look For

### Detection Accuracy
- Does the plugin correctly identify content type issues?
- Are there any false positives (issues reported that aren't actually problems)?
- Are there any false negatives (real issues that aren't detected)?

### Fix Quality
- Are the automatic fixes appropriate and correct?
- Do the fixes maintain proper AsciiDoc formatting?
- Are content type values set to sensible defaults?

### User Experience
- Are the interactive prompts clear and helpful?
- Is the guided mode educational and informative?
- Are error messages understandable?

### Edge Cases
- How does it handle complex file structures?
- Does it work correctly with includes, conditionals, or other advanced AsciiDoc features?
- How does it perform on very large files?

## 📝 How to Provide Feedback

Please create a GitHub issue with your feedback: [GitHub Issues](https://github.com/rolfedh/asciidoc-dita-toolkit/issues)

### Feedback Template
```markdown
## Beta Testing Feedback - ContentType Plugin v0.1.7b1

**Installation Method:** [Docker/PyPI]
**Test Environment:** [OS, Python version if applicable]

### ✅ What Worked Well
- List things that worked as expected

### ❌ Issues Found
- Describe any problems, unexpected behavior, or bugs
- Include sample files or commands that reproduce the issue

### 💡 Suggestions
- Ideas for improvements
- Missing features you'd like to see

### 📊 Test Results
- [ ] Detection accuracy: Good/Fair/Poor
- [ ] Fix quality: Good/Fair/Poor  
- [ ] User experience: Good/Fair/Poor
- [ ] Performance: Good/Fair/Poor

**Additional Comments:**
[Your detailed feedback here]
```

## 🎯 Focus Areas for This Beta

We're particularly interested in feedback on:

1. **Real-world usage patterns** - How does it fit into your workflow?
2. **Content type detection accuracy** - Does it catch the issues you care about?
3. **Interactive experience** - Is the UI intuitive and helpful?
4. **Performance** - How does it handle your typical file sizes and project structures?
5. **Integration** - How well does it work with your existing toolchain?

## 🗓️ Beta Timeline

- **Beta period**: 2-4 weeks (launched July 2025)
- **Feedback deadline**: Late July 2025
- **Final release target**: Early August 2025

*Timeline may be adjusted based on feedback volume and complexity*

## 📚 Additional Resources

- [Main Documentation](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/README.md)
- [Contributing Guide](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/docs/CONTRIBUTING.md)
- [GitHub Repository](https://github.com/rolfedh/asciidoc-dita-toolkit)

---

Thank you for helping us test and improve the ContentType plugin! Your feedback is invaluable for making this tool better for the entire community.
