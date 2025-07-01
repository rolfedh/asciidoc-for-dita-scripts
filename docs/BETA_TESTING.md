# Beta Testing Guide

🎉 **Welcome to beta testing for the AsciiDoc DITA Toolkit!**

This guide covers both the **new ContentType interactive UI (v0.1.8b1)** and how to access **beta testing files** included with all installations.

## 🚀 What's New in v0.1.8b1

### ContentType Plugin - Interactive UI Framework

We've completely reimplemented the ContentType plugin with a powerful interactive framework:

- **Auto mode**: Automatically fixes detected issues
- **Review mode**: Shows what would be changed without applying fixes  
- **Interactive mode**: Prompts you to approve each fix individually
- **Guided mode**: Provides detailed explanations and recommendations

### Enhanced Detection & Fixes

The plugin now detects and can fix:
- ✅ Missing content type attributes
- ✅ Empty or invalid content type values  
- ✅ Commented-out content type lines
- ✅ Deprecated content type formats
- ✅ Misplaced content type attributes

## 📦 Installation Options

### Option 1: PyPI (Recommended)

```bash
# Install the latest beta
pip install asciidoc-dita-toolkit==0.1.8b1

# Verify installation
asciidoc-dita-toolkit --version
find-beta-files --help
```

### Option 2: Docker (No Setup Required)

```bash
# Latest published version
docker run --rm -v $(pwd):/workspace asciidoc-dita-toolkit:latest --help

# Test ContentType plugin
docker run --rm -v $(pwd):/workspace asciidoc-dita-toolkit:latest \
  ContentType --mode interactive --file your_file.adoc
```

## 📁 Accessing Beta Testing Files

Every installation includes comprehensive test files. Use the helper script to find them:

### Quick Access

```bash
# Find test files location
find-beta-files

# Get path for scripting
BETA_DIR=$(find-beta-files --path-only)
echo "Test files at: $BETA_DIR"

# Copy files to work with
cp "$BETA_DIR"/*.adoc ./my-tests/
```

### Docker Access

```bash
# Find files in container
docker run --rm asciidoc-dita-toolkit:latest find-beta-files

# Copy test files from container to host
docker run --rm -v $(pwd):/output asciidoc-dita-toolkit:latest sh -c '
  BETA_DIR=$(find-beta-files --path-only)
  cp "$BETA_DIR"/*.adoc /output/
'

# Interactive exploration
docker run --rm -it -v $(pwd):/workspace asciidoc-dita-toolkit:latest /bin/bash
```

## 🧪 Testing the ContentType Plugin

### Command Reference

```bash
# See all available options
asciidoc-dita-toolkit ContentType --help

# Available modes: auto, review, interactive, guided
# File options: --file FILE or --directory DIRECTORY  
# Additional flags: --recursive, --dry-run, --batch, --quiet, --verbose
```

### Test Different Modes

```bash
# 1. Review mode - See issues without making changes
asciidoc-dita-toolkit ContentType --mode review --file your_file.adoc

# 2. Interactive mode - Approve each fix individually  
asciidoc-dita-toolkit ContentType --mode interactive --file your_file.adoc

# 3. Auto mode - Automatically apply all fixes
asciidoc-dita-toolkit ContentType --mode auto --file your_file.adoc

# 4. Guided mode - Get detailed explanations
asciidoc-dita-toolkit ContentType --mode guided --file your_file.adoc

# 5. Directory processing with dry-run
asciidoc-dita-toolkit ContentType --mode auto --directory . --recursive --dry-run
```

### Using Included Test Files

The installation includes ready-to-test files with various content type issues:

```bash
# Get test files
BETA_DIR=$(find-beta-files --path-only)
cp "$BETA_DIR"/*.adoc ./test-workspace/
cd test-workspace/

# Test each file type
asciidoc-dita-toolkit ContentType --mode review --file missing_content_type.adoc
asciidoc-dita-toolkit ContentType --mode auto --file empty_content_type.adoc --dry-run
asciidoc-dita-toolkit ContentType --mode interactive --file commented_content_type.adoc
```

## 📋 Test File Categories

### Files That Need Fixing

| File | Issue | Expected Fix |
|------|-------|--------------|
| `missing_content_type.adoc` | No content type attribute | Add `:_mod-docs-content-type: PROCEDURE` |
| `empty_content_type.adoc` | Empty content type value | Add appropriate content type value |
| `commented_content_type.adoc` | Content type is commented out | Uncomment and fix if needed |
| `wrong_content_type.adoc` | Deprecated content type format | Update to modern format |

### Files That Should Be Ignored

| File | Reason |
|------|--------|
| `correct_procedure.adoc` | Has valid `:_mod-docs-content-type: PROCEDURE` |
| `correct_concept.adoc` | Has valid `:_mod-docs-content-type: CONCEPT` |
| `correct_reference.adoc` | Has valid `:_mod-docs-content-type: REFERENCE` |

## 🧪 Test Scenarios

### Create Your Own Test Cases

#### Missing Content Type
```asciidoc
= Your Topic Title

Content goes here without any content type.
```

#### Empty Content Type  
```asciidoc
:_mod-docs-content-type:
= Your Topic Title

Content with empty content type attribute.
```

#### Commented Content Type
```asciidoc
//:_mod-docs-content-type: PROCEDURE
= Your Topic Title

Content with commented-out content type.
```

#### Misplaced Content Type
```asciidoc
= Your Topic Title
:_mod-docs-content-type: PROCEDURE

Content type appears after title (should be at top).
```

## 🔍 What to Test & Report

### Detection Accuracy
- ✅ Does the plugin correctly identify content type issues?
- ❌ Are there false positives (incorrect issues reported)?
- ❌ Are there false negatives (real issues missed)?

### Fix Quality  
- ✅ Are automatic fixes appropriate and correct?
- ✅ Do fixes maintain proper AsciiDoc formatting?
- ✅ Are content type values sensible defaults?

### User Experience
- ✅ Are interactive prompts clear and helpful?
- ✅ Is the guided mode educational and informative?
- ✅ Are error messages understandable?

### Performance & Edge Cases
- ✅ How does it handle large files or complex structures?
- ✅ Does it work with includes, conditionals, or advanced AsciiDoc features?
- ✅ How does it perform on your real-world content?

## 🐛 Testing Other Plugins

The toolkit includes test files for all plugins:

### EntityReference Plugin
```bash
# Test HTML entity reference conversion
BETA_DIR=$(find-beta-files --path-only)
cp "$BETA_DIR"/*.adoc ./entity-tests/

# Process a file with HTML entities
asciidoc-dita-toolkit EntityReference --file entity-tests/sample_with_entities.adoc

# Compare before/after
diff entity-tests/sample_with_entities.adoc entity-tests/expected_output.adoc
```

### General Testing Workflow
```bash
# 1. Set up test workspace
mkdir test-workspace && cd test-workspace

# 2. Copy test files
BETA_DIR=$(find-beta-files --path-only)
cp -r "$BETA_DIR"/* .

# 3. Test plugins on sample data
asciidoc-dita-toolkit EntityReference --recursive
asciidoc-dita-toolkit ContentType --mode review --directory .

# 4. Validate results against expected outputs
```

## 📝 Providing Feedback

Create a GitHub issue with your feedback: [GitHub Issues](https://github.com/rolfedh/asciidoc-dita-toolkit/issues)

### Feedback Template
```markdown
## Beta Testing Feedback - v0.1.8b1

**Installation Method:** [PyPI/Docker]
**Test Environment:** [OS, Python version]
**Plugin Tested:** [ContentType/EntityReference/Other]

### ✅ What Worked Well
- List things that worked as expected

### ❌ Issues Found  
- Describe problems or unexpected behavior
- Include sample files or commands that reproduce issues

### 💡 Suggestions
- Ideas for improvements or missing features

### 📊 Test Results
- [ ] Detection accuracy: Good/Fair/Poor
- [ ] Fix quality: Good/Fair/Poor
- [ ] User experience: Good/Fair/Poor  
- [ ] Performance: Good/Fair/Poor

**Additional Comments:** [Your detailed feedback]
```

## 🎯 Priority Testing Areas

We're especially interested in feedback on:

1. **ContentType Interactive UI** - Is it intuitive and helpful?
2. **Real-world content** - How does it perform on your actual files?
3. **Workflow integration** - Does it fit into your existing processes?
4. **Error handling** - Are error messages clear and actionable?
5. **Performance** - How does it handle your typical file sizes?

## 🗓️ Beta Timeline

- **Beta period**: 2-4 weeks (launched July 2025)
- **Feedback deadline**: Late July 2025  
- **Final release target**: Early August 2025

## 🚀 Advanced Usage

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Test with beta files
  run: |
    pip install asciidoc-dita-toolkit==0.1.8b1
    BETA_DIR=$(find-beta-files --path-only)
    cp -r "$BETA_DIR"/* ./test/
    asciidoc-dita-toolkit ContentType --mode auto --directory test/ --dry-run
```

### Docker in CI
```yaml  
- name: Test with Docker
  run: |
    docker run --rm -v $(pwd):/workspace asciidoc-dita-toolkit:latest sh -c '
      cp -r $(find-beta-files --path-only)/* /workspace/test/
      asciidoc-dita-toolkit ContentType --mode review --directory /workspace/test/
    '
```

### Troubleshooting

**Files not found:**
```bash
# Verify installation
find-beta-files
pip install --upgrade asciidoc-dita-toolkit==0.1.8b1
```

**Container issues:**
```bash
# Verify container has test files
docker run --rm asciidoc-dita-toolkit:latest find-beta-files
```

**Permission errors:**
```bash
# Fix permissions when copying from container
docker run --rm -v $(pwd):/output asciidoc-dita-toolkit:latest sh -c '
  cp -r $(find-beta-files --path-only)/* /output/ && chmod -R 644 /output/*
'
```

## 📚 Additional Resources

- [Main Documentation](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/README.md)
- [Contributing Guide](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/docs/CONTRIBUTING.md)  
- [GitHub Repository](https://github.com/rolfedh/asciidoc-dita-toolkit)

---

**Thank you for helping us test and improve the AsciiDoc DITA Toolkit!** Your feedback is invaluable for making this tool better for the entire technical writing community. 🎉
