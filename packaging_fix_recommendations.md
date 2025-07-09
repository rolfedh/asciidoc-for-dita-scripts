# ADT Packaging Fix Recommendations

## For AI Implementation (Cursor.com)

**IMPLEMENT THESE SECTIONS:**
- ✅ **"Required Changes"** → Edit `pyproject.toml` exactly as specified
- ✅ **"Step 2: Edit pyproject.toml"** → Make the 4 specific changes listed
- ✅ **"Step 3: Update Version Bumping Scripts"** → Update Makefile and workflow files

**DO NOT IMPLEMENT THESE SECTIONS (Human Tasks):**
- ❌ **Step 1: Backup** → User should backup manually
- ❌ **Step 4: Test Locally** → User needs to test in their environment
- ❌ **Step 5: Build and Test** → User needs to verify build
- ❌ **"Important Considerations"** → Information only
- ❌ **"User Experience"** → Documentation only
- ❌ **"Release Preparation"** → User decisions required

**FOCUS: Only edit configuration files (`pyproject.toml`, `Makefile`, `.github/workflows/*.yml`)**

---

## Problem
- `adt-core` package only contains the core framework (`src/adt_core/`)
- Missing the actual processing modules (`asciidoc_dita_toolkit/`)
- Users get "No module named 'asciidoc_dita_toolkit'" errors
- Entry points reference modules that aren't packaged

## Solution Overview
Change from shipping just the core framework to shipping a complete toolkit.

## Required Changes

### 1. Update `pyproject.toml` Package Configuration

**Current:**
```toml
[project]
name = "adt-core"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"
```

**New:**
```toml
[project]
name = "adt"

[tool.setuptools.packages.find]
where = ["."]
include = ["adt_core*", "asciidoc_dita_toolkit*"]
exclude = ["tests*", "build*", "dist*", "*.egg-info*"]

# Remove the package-dir section entirely - use root as source
```

### 2. Update Entry Points (Keep Current Module References)

**Current:**
```toml
[project.scripts]
adt-core = "adt_core.cli:main"
adg = "adt_core.cli:main"
adt = "adt_core.cli:main"
# ... other scripts
```

**New:**
```toml
[project.scripts]
adt = "adt_core.cli:main"
asciidoc-dita-toolkit = "adt_core.cli:main"
# Remove adt-core (old name)
# Keep adg if you want the short alias
```

**Keep Current Module Entry Points (No Changes Needed):**
```toml
[project.entry-points."adt.modules"]
EntityReference = "asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference:EntityReferenceModule"
ContentType = "asciidoc_dita_toolkit.asciidoc_dita.plugins.ContentType:ContentTypeModule"
DirectoryConfig = "asciidoc_dita_toolkit.asciidoc_dita.plugins.DirectoryConfig:DirectoryConfigModule"
ContextAnalyzer = "asciidoc_dita_toolkit.asciidoc_dita.plugins.ContextAnalyzer:ContextAnalyzerModule"
ContextMigrator = "asciidoc_dita_toolkit.asciidoc_dita.plugins.ContextMigrator:ContextMigratorModule"
CrossReference = "asciidoc_dita_toolkit.asciidoc_dita.plugins.CrossReference:CrossReferenceModule"
```

## Implementation Steps

### Step 1: Backup Current Configuration (HUMAN TASK - DO NOT IMPLEMENT)
```bash
cp pyproject.toml pyproject.toml.backup
```

### Step 2: Edit pyproject.toml (✅ IMPLEMENT THIS)
1. **Change package name**: `name = "adt-core"` → `name = "adt"`
2. **Replace packages.find section**:
   - Remove: `where = ["src"]`
   - Add: `where = ["."]`
   - Add: `include = ["adt_core*", "asciidoc_dita_toolkit*"]`
   - Add: `exclude = ["tests*", "build*", "dist*", "*.egg-info*"]`
3. **Remove package-dir section entirely**
4. **Update main script**: Keep `adt = "adt_core.cli:main"`, remove `adt-core = ...`

### Step 3: Update Version Bumping Scripts (✅ IMPLEMENT THIS)
Update both:
- `Makefile` bump-version target: Look for `name = "adt"` instead of `name = "adt-core"`
- `.github/workflows/nightly-release.yml`: Update package name references

### Step 4: Test Locally (HUMAN TASK - DO NOT IMPLEMENT)
```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info/

# IMPORTANT: Remove both old packages to avoid conflicts
pip uninstall adt-core -y
pip uninstall asciidoc-dita-toolkit -y

# Test editable install
pip install -e .

# Verify it works
adt --list-plugins     # Should show all modules without import errors
adt --help
```

### Step 5: Build and Test Package (HUMAN TASK - DO NOT IMPLEMENT)
```bash
python -m build

# Verify both packages are included in the wheel
unzip -l dist/adt-*.whl | grep -E "(adt_core|asciidoc_dita_toolkit)"

# Should show files like:
# adt_core/__init__.py
# adt_core/module_sequencer.py
# asciidoc_dita_toolkit/asciidoc_dita/plugins/ContentType.py
# asciidoc_dita_toolkit/asciidoc_dita/plugins/EntityReference.py
# etc.

# Test wheel installation in clean environment
pip install dist/adt-*.whl
```

## Important Considerations (INFORMATION ONLY - DO NOT IMPLEMENT)

### Import Paths Compatibility
✅ **Existing imports will work unchanged**. When we use `where = ["."]`, setuptools creates the same package structure:
- `adt_core.module_sequencer` imports will still work
- `from adt_core.exceptions import ...` will still work
- No code changes needed in existing modules

The package structure remains: `adt_core/` and `asciidoc_dita_toolkit/` - we're just telling setuptools to find them from the root directory instead of `src/`.

### Version Strategy
**Recommended: Continue from current version (2.0.1)**
- Maintains version continuity for existing users
- Reflects that this is an enhanced version of the same functionality
- Alternative: Start at 1.0.0 if you want to emphasize the "new complete package"

Current version: `2.0.1` → New version: `2.0.2` (or `2.1.0` for minor feature bump)

### Migration Path for Existing Users
**Critical**: Users may have BOTH packages installed and need to clean up:

```bash
# Required cleanup for existing users
pip uninstall adt-core -y                    # Remove the incomplete package
pip uninstall asciidoc-dita-toolkit -y       # Remove the old complete package
pip install adt                              # Install the new unified package
```

**Background**: 
- `adt-core` was the incomplete framework-only package
- `asciidoc-dita-toolkit` was the previous complete package name
- `adt` will be the new unified, complete package

We should document this prominently in release notes and README.

## User Experience After Fix
```bash
pip install adt                    # Single package installation
adt --list-plugins                 # Shows all available modules (EntityReference, ContentType, etc.)
adt --help                         # Shows full interface
adt some-command                   # All functionality works
asciidoc-dita-toolkit --version    # Backward compatibility alias
```

## Critical Files to Update
1. **`pyproject.toml`**: Main package configuration (detailed above)
2. **`Makefile`**: Update version bumping to look for `name = "adt"`
3. **`.github/workflows/nightly-release.yml`**: Update package name references
4. **Documentation**: Update install instructions from `adt-core` to `adt`

## Verification Checklist
- [ ] Package builds without errors: `python -m build`
- [ ] Both directories included in wheel: `unzip -l dist/adt-*.whl | grep -E "(adt_core|asciidoc_dita_toolkit)"`
- [ ] Entry points work: `adt --list-plugins` shows all modules
- [ ] No import errors when loading modules
- [ ] All imports work: `python -c "from adt_core.module_sequencer import ModuleSequencer; print('✓')"`
- [ ] Version synchronization still works: `make bump-version`
- [ ] All tests pass: `make test`

## Release Preparation
1. **Update version**: Continue from current `2.0.1` → `2.0.2` (or `2.1.0`)
2. **Release notes**: Emphasize this consolidates both previous packages (`adt-core` + `asciidoc-dita-toolkit`) into one complete package
3. **Migration guide**: Document the cleanup requirement for both old packages
4. **README update**: Change install instructions from `asciidoc-dita-toolkit` to `adt`
5. **Deprecation notice**: Consider adding deprecation warnings to both old packages pointing to `adt`

<!--
## Alternative Approach (More Complex - Not Recommended)
Move all code to src/ directory first, then use:
```toml
[tool.setuptools.packages.find]
where = ["src"]
include = ["adt_core*", "asciidoc_dita_toolkit*"]
```
This requires moving asciidoc_dita_toolkit/ to src/asciidoc_dita_toolkit/ first.
-->