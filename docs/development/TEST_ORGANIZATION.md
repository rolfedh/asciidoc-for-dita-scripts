# Test File Organization Guidelines

This document ensures all test files are created in the correct location to maintain project organization.

## 🎯 **Test File Location Rules**

### ✅ **Correct Location**
- All test files MUST go in the `tests/` directory
- Test files: `test_*.py` or `*_test.py`
- Debug/validation files: Use `tests/debug_*.py` or `tests/validate_*.py`

### ❌ **Incorrect Locations**
- Root directory: No `test_*.py` files allowed
- Plugin directories: No test files in `asciidoc_dita_toolkit/`
- Other subdirectories: Tests belong in `tests/` only

## 🛠️ **Tools to Enforce Organization**

### 1. **Pytest Configuration** (`pyproject.toml`)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]              # Only discover tests in tests/
collect_ignore = ["test_*.py"]     # Ignore root-level test files
```

### 2. **Pre-commit Hook** (`.git/hooks/pre-commit`)
- Automatically checks for misplaced test files before commits
- Blocks commits with test files in wrong locations
- Provides helpful error messages with fix suggestions

### 3. **Makefile Checks**
```bash
make test           # Includes test location check
make check-test-locations  # Standalone location check
```

### 4. **New Test Creation Script**
```bash
# Create new test files in correct location with template
python3 scripts/new_test.py my_feature
python3 scripts/new_test.py my_plugin --plugin MyPlugin
```

## 📝 **Creating New Test Files**

### Method 1: Use the Script (Recommended)
```bash
cd /home/rolfedh/asciidoc-dita-toolkit
python3 scripts/new_test.py feature_name
# Creates tests/test_feature_name.py with proper template
```

### Method 2: Manual Creation
1. Create file in `tests/test_*.py`
2. Use existing test files as templates
3. Follow naming convention: `test_<feature_name>.py`

## 🧪 **Test Categories and Markers**

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_basic_functionality():
    """Unit test example."""
    pass

@pytest.mark.integration  
def test_end_to_end_workflow():
    """Integration test example."""
    pass

@pytest.mark.slow
def test_performance():
    """Slow test example."""
    pass
```

## 🚦 **Validation Commands**

### Check Test Organization
```bash
make check-test-locations    # Check for misplaced files
pytest --collect-only        # Show all discovered tests
find . -name "test_*.py"     # List all test files
```

### Run Tests by Category
```bash
pytest tests/ -m unit                    # Unit tests only
pytest tests/ -m "not slow"             # Skip slow tests  
pytest tests/ -k "user_journey"         # UserJourney tests only
```

## 🔧 **Fixing Misplaced Files**

If you have test files in wrong locations:

```bash
# Move individual files
mv test_something.py tests/

# Move all misplaced test files
find . -maxdepth 1 -name "test_*.py" -exec mv {} tests/ \;

# Git add the moves
git add tests/
git commit -m "fix: Move test files to tests/ directory"
```

## ⚡ **Automation Benefits**

This setup provides:
- ✅ **Automatic enforcement** via pre-commit hooks
- ✅ **Template generation** for consistent test structure  
- ✅ **Clear error messages** when files are misplaced
- ✅ **IDE integration** through pytest configuration
- ✅ **CI/CD compatibility** with proper test discovery

## 🎯 **Summary**

Following these guidelines ensures:
1. **Clean project structure** with tests in proper locations
2. **Consistent developer experience** across the team
3. **Reliable CI/CD** with predictable test discovery
4. **Easy maintenance** with automated checks and templates

---

**Remember**: When in doubt, use `python3 scripts/new_test.py <name>` to create tests in the right place! 🎯
