# ContentType Plugin Beta Test Files

This directory contains test files specifically designed for beta testing the new ContentType plugin interactive features.

## 📋 Test File Categories

### 🔴 Files That Need Fixing

These files have content type issues that the plugin should detect and offer to fix:

| File | Issue | Expected Fix |
|------|-------|--------------|
| `missing_content_type.adoc` | No content type attribute | Add `:_mod-docs-content-type: PROCEDURE` |
| `empty_content_type.adoc` | Empty content type value | Add appropriate content type value |
| `commented_content_type.adoc` | Content type is commented out | Uncomment and fix if needed |
| `wrong_content_type.adoc` | Deprecated content type format | Update to modern format |

### 🟢 Files That Should Be Ignored

These files have correct content type attributes and should not trigger any changes:

| File | Reason | 
|------|--------|
| `correct_procedure.adoc` | Has valid `:_mod-docs-content-type: PROCEDURE` |
| `correct_concept.adoc` | Has valid `:_mod-docs-content-type: CONCEPT` |
| `correct_reference.adoc` | Has valid `:_mod-docs-content-type: REFERENCE` |

## 🧪 Quick Testing Commands

### Test Individual Files
```bash
# Test review mode (shows issues without fixing)
asciidoc-dita-toolkit ContentType --mode review --file missing_content_type.adoc

# Test auto mode (automatically fixes issues)
asciidoc-dita-toolkit ContentType --mode auto --file missing_content_type.adoc

# Test interactive mode (prompts for each fix)
asciidoc-dita-toolkit ContentType --mode interactive --file missing_content_type.adoc
```

### Test All Files at Once
```bash
# Review all files in this directory
asciidoc-dita-toolkit ContentType --mode review --directory .

# Auto-fix all files (be careful!)
asciidoc-dita-toolkit ContentType --mode auto --directory . --dry-run

# Interactive mode for all files
asciidoc-dita-toolkit ContentType --mode interactive --directory .
```

### Docker Testing
```bash
# From this directory, test with Docker
docker run --rm -v $(pwd):/workspace asciidoc-dita-toolkit:latest \
  ContentType --mode review --directory /workspace

docker run --rm -v $(pwd):/workspace asciidoc-dita-toolkit:latest \
  ContentType --mode interactive --file missing_content_type.adoc
```

## 📝 How to Use These Files

### Option 1: Install via PyPI (includes test files)
```bash
pip install asciidoc-dita-toolkit
find-beta-files  # Shows where test files are located
```

### Option 2: Use Docker (includes test files)
```bash
# Test files are automatically available in the container
docker run --rm asciidoc-dita-toolkit:latest find-beta-files
```

### Option 3: Download or clone this directory
1. **Download or clone** this directory
2. **Make copies** of the files before testing (the plugin will modify them)
3. **Test different modes** on each file type
4. **Compare results** with the expected behavior described above
5. **Report any unexpected behavior** in GitHub issues

## 🔄 Resetting Test Files

After testing, you can restore the original files:

### If you downloaded files:
```bash
# Use the helper command to get fresh copies
find-beta-files  # Shows location and copy instructions
```

### If you cloned the repository:
```bash
git checkout -- *.adoc
```

### Manual reset:
Simply delete the modified files and use the `find-beta-files` command to get fresh copies:
```bash
find-beta-files  # Shows location and copy command
```

## 🎯 What to Look For

- ✅ **Correct detection**: Does the plugin identify the right issues?
- ✅ **Appropriate fixes**: Are the suggested/applied fixes correct?
- ✅ **No false positives**: Are correct files left unchanged?
- ✅ **Good user experience**: Are prompts clear and helpful?
- ✅ **Performance**: Does it handle multiple files efficiently?

Happy testing! 🚀
