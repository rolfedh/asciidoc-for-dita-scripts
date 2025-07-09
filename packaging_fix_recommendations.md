# ADT Packaging Fix Recommendations

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

### Step 1: Backup Current Configuration
```bash
cp pyproject.toml pyproject.toml.backup
```

### Step 2: Edit pyproject.toml
1. **Change package name**: `name = "adt-core"` → `name = "adt"`
2. **Replace packages.find section**:
   - Remove: `where = ["src"]`
   - Add: `where = ["."]`
   - Add: `include = ["adt_core*", "asciidoc_dita_toolkit*"]`
   - Add: `exclude = ["tests*", "build*", "dist*", "*.egg-info*"]`
3. **Remove package-dir section entirely**
4. **Update main script**: Keep `adt = "adt_core.cli:main"`, remove `adt-core = ...`

### Step 3: Update Version Bumping Scripts
Update both:
- `Makefile` bump-version target: Look for `name = "adt"` instead of `name = "adt-core"`
- `.github/workflows/nightly-release.yml`: Update package name references

### Step 4: Test Locally
```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info/

# Test editable install
pip uninstall adt-core  # Remove old package
pip install -e .

# Verify it works
adt --list-plugins
adt --help
```

### Step 5: Build and Test Package
```bash
python -m build
pip install dist/adt-*.whl  # Test wheel installation
```

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
- [ ] Both directories included in wheel: Check `dist/*.whl` contents
- [ ] Entry points work: `adt --list-plugins` shows all modules
- [ ] No import errors when loading modules
- [ ] Version synchronization still works: `make bump-version`
- [ ] All tests pass: `make test`

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