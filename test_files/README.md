# Test Files Reference

This directory contains comprehensive test files for the ContentType plugin.

## 📁 Backup & Restore
- **Backup location**: `test_files_backup/`
- **Restore command**: `./restore_test_files.sh`

## 🧪 Test Files Overview

### ✅ Current Format - Working
- `correct_procedure.adoc` - Has `:_mod-docs-content-type: PROCEDURE`

### ⚠️ Current Format - Empty
- `empty_content_type.adoc` - Has empty `:_mod-docs-content-type:`

### 🔄 Deprecated Attributes
- `deprecated_test.adoc` - Has `:_content-type: CONCEPT`
- `proc_test.adoc` - Has `:_module-type: REFERENCE`
- `empty_deprecated.adoc` - Has empty `:_content-type:`

### 🤖 Filename Auto-Detection
- `assembly_example.adoc` - `assembly_` prefix → ASSEMBLY
- `proc_example.adoc` - `proc_` prefix → PROCEDURE
- `con_example.adoc` - `con_` prefix → CONCEPT
- `ref_example.adoc` - `ref_` prefix → REFERENCE
- `snip_example.adoc` - `snip_` prefix → SNIPPET

### 💬 Interactive Prompts
- `ignore_comments.adoc` - No content type, no detectable filename
- `commented_content_type.adoc` - Only commented-out content type
- `missing_content_type.adoc` - No content type attribute at all

### 🔧 Other Plugin Tests
- `with_entities.adoc` - For EntityReference plugin testing

## 🚀 Usage

1. **Run tests**: Use any combination of files with the ContentType plugin
2. **Reset after test**: Run `./restore_test_files.sh` to restore clean state
3. **Comprehensive test**: Run plugin on entire `test_files/` directory

## 📋 Expected Behaviors

| File | Expected Plugin Behavior |
|------|--------------------------|
| `correct_procedure.adoc` | ✅ Content type already set: PROCEDURE |
| `empty_content_type.adoc` | 💬 Prompt user to select content type |
| `deprecated_test.adoc` | 🔄 Convert `:_content-type: CONCEPT` → `:_mod-docs-content-type: CONCEPT` |
| `proc_test.adoc` | 🔄 Convert `:_module-type: REFERENCE` → `:_mod-docs-content-type: REFERENCE` |
| `empty_deprecated.adoc` | 💬 Prompt user (empty deprecated attribute) |
| `assembly_example.adoc` | 🤖 Auto-detect and add `:_mod-docs-content-type: ASSEMBLY` |
| `proc_example.adoc` | 🤖 Auto-detect and add `:_mod-docs-content-type: PROCEDURE` |
| `con_example.adoc` | 🤖 Auto-detect and add `:_mod-docs-content-type: CONCEPT` |
| `ref_example.adoc` | 🤖 Auto-detect and add `:_mod-docs-content-type: REFERENCE` |
| `snip_example.adoc` | 🤖 Auto-detect and add `:_mod-docs-content-type: SNIPPET` |
| `ignore_comments.adoc` | 💬 Prompt user to select content type |
| `commented_content_type.adoc` | 💬 Prompt user (commented doesn't count) |
| `missing_content_type.adoc` | 💬 Prompt user to select content type |
