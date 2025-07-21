# Beta Testing Guide

🎉 **Thank you for beta testing the AsciiDoc DITA Toolkit!**

We need your feedback to make this toolkit better before its full release. As a beta tester, you'll help us identify what works well and what needs improvement in the user experience. 

## What is this toolkit?

The AsciiDoc DITA Toolkit (`adt`) helps you prepare your AsciiDoc files for eventual migration to DITA. It identifies and resolves syntax issues to ensure a smooth migration. It automates as much of the work as possible, but prompts you when it needs your input.

When `adt` is released, you'll typically create a new working branch in your repo, run the command line tool, and respond to the prompts. When finished, you'll review and make any additional edits to your files before committing and pushing them.

**How the ContentType plugin works:**

1. **Scans files** - Identifies AsciiDoc files that need content type analysis
2. **Converts deprecated attributes** - Updates old format attributes (`:_content-type:`, `:_module-type:`) to current standards
3. **Auto-detects from filename** - Analyzes filename prefixes (`proc_`, `con_`, `assembly_`, etc.) to determine content type
4. **Smart content analysis** - Examines file content patterns (headings, structure, keywords) to suggest appropriate content type
5. **Interactive prompts** - When auto-detection fails, it guides you through manual content type selection

## 📋 Quick Start

1. [Install the beta](#-installation) 
2. [Get test files](#-accessing-test-files)
3. [Test the new features](#-testing-the-contenttype-plugin)
4. [Report feedback](#-providing-feedback)

## 📦 Installation

Install the beta version via PyPI:

```bash
pip install asciidoc-dita-toolkit==0.1.9b3
adt --version
```

> **💡 Need to upgrade or having issues?** See [Upgrading and Troubleshooting](#-upgrading-and-troubleshooting)

> **💡 Reset test files:** The toolkit modifies files during testing. To get fresh test files for another round, simply copy them again: `adt-test-files copy ./test_files_fresh`

## 🧪 Testing the ContentType Plugin

### Command overview

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

> **💡 Tip:** Replace `FILE` with a specific filename, or `DIR` with a directory path.

### Quick Test Workflow

```bash
# 1. Create a test directory and copy the test files
mkdir ~/adt-beta-test
cd ~/adt-beta-test
adt-test-files copy ./test_files_1
adt-test-files copy ./test_files_2
adt-test-files copy ./test_files_3
cd test_files_1

# 2. Test single file processing
adt ContentType missing_content_type.adoc

# 3. Test directory processing (recursive by default)
adt ContentType .

# Start with a fresh set of files after directory processing (files have been modified)
cd ../test_files_2

# 4. Test interactive prompts (select option 1-7 when prompted)
adt ContentType ignore_comments.adoc

# 5. Test filename auto-detection  
adt ContentType proc_example.adoc

# 6. Test smart content type analysis
adt ContentType installing_docker.adoc

# 7. Optional: If you want another set of test files to play with
cd ../test_files_3
```

## 📝 Providing Feedback

Please share your thoughts with us by
[creating a beta testing feedback issue in GitHub](https://github.com/rolfedh/asciidoc-dita-toolkit/issues/new?template=beta-testing-feedback.md).
Please also check out [the list of open and closed user feedback issues](https://github.com/rolfedh/asciidoc-dita-toolkit/issues?q=is%3Aissue%20label%3A%22user%20feedback%22). 

We especially appreciate your feedback on:

1. **Interactive prompts** - Are the content type options clear?
2. **Filename auto-detection** - Does it correctly identify content types from filename prefixes?
3. **Deprecated attribute conversion** - Are conversions accurate?
4. **Visual feedback** - Is the colored output helpful?
5. **Real-world content** - Performance and accuracy on your actual files?

**Thank you for testing the AsciiDoc DITA Toolkit!** 🎉

----
**You can stop here. The remaining content is optional.**
----

## 📋 Understanding Test Files

The test files cover all ContentType plugin scenarios:

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

## 📋 Upgrading and Troubleshooting

### Upgrading

If you already have an earlier version installed, upgrade to the latest beta:

```bash
pip install --upgrade asciidoc-dita-toolkit==0.1.9b3
adt --version
```

### Troubleshooting upgrade issues

If the upgrade fails or you're having issues, try a clean reinstall:

```bash
# Uninstall the current version
pip uninstall asciidoc-dita-toolkit

# Install the beta version fresh
pip install asciidoc-dita-toolkit==0.1.9b3
adt --version
```

## 📚 Additional Resources

- [Main Documentation](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/README.md)
- [GitHub Repository](https://github.com/rolfedh/asciidoc-dita-toolkit)

---

**Thank you for testing the AsciiDoc DITA Toolkit!** 🎉
