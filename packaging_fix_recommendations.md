# ADT Packaging Fix Recommendations

## Problem
- `adt-core` package only contains the core framework (`src/adt_core/`)
- Missing the actual processing modules (`asciidoc_dita_toolkit/`)
- Users get "No module named 'asciidoc_dita_toolkit'" errors
- Entry points reference modules that aren't packaged

## Solution Overview
Change from shipping just the core framework to shipping a complete toolkit.

## Required Changes

### 1. Update `pyproject.toml`

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
where = ["src", "."]
include = ["adt_core*", "asciidoc_dita_toolkit*"]

[tool.setuptools.package-dir]
"" = "src"
"asciidoc_dita_toolkit" = "asciidoc_dita_toolkit"
```

### 2. Update Main Script Reference

**Current:**
```toml
[project.scripts]
adt-core = "adt_core.cli:main"
```

**New:**
```toml
[project.scripts]
adt = "adt_core.cli:main"
```

## Result
- Users install one package: `pip install adt`
- Package includes both core framework and all processing modules
- Entry points can find their referenced modules
- No more "Failed to load module" errors

## Testing Steps
1. Backup current `pyproject.toml`
2. Apply changes above
3. Test locally: `pip install -e .`
4. Verify: `adt --list-plugins` works without errors
5. Build and test package: `python -m build`

## User Experience After Fix
```bash
pip install adt
adt --list-plugins    # Shows all available modules
adt --help           # Shows full interface
```

## Key Benefits
- Single package installation
- All functionality included
- No missing dependencies
- Matches user expectations for complete toolkit