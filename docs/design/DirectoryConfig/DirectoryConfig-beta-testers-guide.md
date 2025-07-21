# DirectoryConfig Beta Testing Guide

🎉 **Thank you for beta testing the DirectoryConfig feature!**

We need your feedback to make directory scoping better before its full release. As a beta tester, you'll help us identify what works well and what needs improvement in the user experience.

## What is DirectoryConfig?

The DirectoryConfig feature lets you configure which directories ADT should process or skip. Instead of manually specifying directories each time, you set up a configuration once and all ADT plugins automatically respect your directory scope.

**How DirectoryConfig works:**

1. **Interactive setup** - Guides you through configuring repository root, include/exclude directories
2. **Persistent configuration** - Saves settings in `.adtconfig.json` (local or home directory)
3. **Automatic scoping** - All plugins (ContentType, EntityReference, etc.) use your configuration
4. **Smart filtering** - Warns when specified directories conflict with configuration
5. **Graceful fallback** - Works seamlessly with existing workflows when disabled

## 📋 Quick Start

1. [Enable the feature](#-enable-directoryconfig) 
2. [Test basic configuration](#-testing-basic-configuration)
3. [Test with existing plugins](#-testing-with-existing-plugins)
4. [Report feedback](#-providing-feedback)

## 🔧 Enable DirectoryConfig

DirectoryConfig is a **preview** feature that must be explicitly enabled:

```bash
# Enable the feature
export ADT_ENABLE_DIRECTORY_CONFIG=true

# Verify it's available
adt --list-plugins
```

## 🧪 Testing Basic Configuration

### Quick Test Workflow

```bash
# 1. Create test environment with sample directory structure
mkdir ~/adt-directory-test && cd ~/adt-directory-test

# 2. Create minimal test structure with sample .adoc files
mkdir -p docs/{user-guide,admin-guide,legacy} guides/{installation,troubleshooting} archive
echo -e "= User Guide\n\nContent here." > docs/user-guide/index.adoc
echo -e "= Admin Guide\n\nAdmin content." > docs/admin-guide/setup.adoc
echo -e "= Legacy\n\nOld content." > docs/legacy/old.adoc
echo -e "= Installation\n\nHow to install." > guides/installation/setup.adoc

# 3. Test configuration setup
adt DirectoryConfig

# 4. View your configuration
adt DirectoryConfig --show

# 5. Test directory filtering with ContentType
adt ContentType   # Uses configuration
adt ContentType -d docs/legacy  # Tests exclude behavior
```

### Configuration Scenarios to Test

**Scenario 1: Include specific directories**
- Set `includeDirs: ["docs/user-guide", "guides"]`
- Test that only these directories are processed

**Scenario 2: Exclude directories**  
- Set `excludeDirs: ["docs/legacy", "archive"]`
- Test that these directories are skipped

**Scenario 3: Multiple config files**
- Create both `./.adtconfig.json` and `~/.adtconfig.json`
- Test that ADT prompts you to choose and preselects most recent

## 🔧 Testing with Existing Plugins

```bash
# Make sure you're in the test directory with sample files
cd ~/adt-directory-test

# Test with ContentType plugin
export ADT_ENABLE_DIRECTORY_CONFIG=true
adt ContentType   # Should show "✓ Using directory configuration"

# Test directory override behavior
adt ContentType -d docs/legacy   # Should warn if excluded
adt ContentType -d other-dir     # Should warn if not included

# Test traditional behavior (disabled)
unset ADT_ENABLE_DIRECTORY_CONFIG
adt ContentType   # Should work normally without status messages
```

## 📝 Providing Feedback

Please share your thoughts with us by
[creating a beta testing feedback issue in GitHub](https://github.com/rolfedh/asciidoc-dita-toolkit/issues/new?template=beta-testing-feedback.md).

We especially appreciate your feedback on:

1. **Setup wizard** - Is the interactive configuration clear and intuitive?
2. **Directory filtering** - Does include/exclude behavior work as expected?
3. **Status messages** - Are the ✓ progress indicators helpful?
4. **Configuration file handling** - Is the local vs. home directory choice clear?
5. **Integration** - Does it work smoothly with ContentType and other plugins?
6. **Override behavior** - Is the `-d directory` interaction behavior intuitive?

**Thank you for testing DirectoryConfig!** 🎉

----
**You can stop here. The remaining content is optional.**
----

## 📋 Understanding Test Scenarios

### Basic Configuration Tests

| Test | Configuration | Expected Behavior |
|------|---------------|------------------|
| Include only | `includeDirs: ["docs"]` | Only processes `docs/` directory |
| Exclude specific | `excludeDirs: ["legacy"]` | Processes all except `legacy/` |
| No restrictions | Empty arrays | Processes all directories |

### Override Behavior Tests

| Command | Config: includes `["docs"]`, excludes `["legacy"]` | Expected Result |
|---------|--------------------------------------------------|----------------|
| `adt ContentType -d docs` | Directory matches include | ✓ Processes normally |
| `adt ContentType -d legacy` | Directory is excluded | ⚠ Warns and skips |
| `adt ContentType -d other` | Directory not in includes | ⚠ Warns but processes |

### Configuration File Priority Tests

| Local `.adtconfig.json` | Home `~/.adtconfig.json` | Expected Behavior |
|-------------------------|--------------------------|------------------|
| Exists | Doesn't exist | Uses local automatically |
| Doesn't exist | Exists | Uses home automatically |
| Exists (newer) | Exists (older) | Prompts, preselects local |
| Exists (older) | Exists (newer) | Prompts, preselects home |
