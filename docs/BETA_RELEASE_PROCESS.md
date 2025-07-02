# Beta Release Process Guide for Contributors

This document explains how to perform "Option 1" beta release process for new features in the asciidoc-dita-toolkit project, how to incorporate user feedback, and complete the final release.

## 🎯 When to Use Beta Releases

Use the beta release process when you have:

- **Major new features** that significantly change user experience
- **New interactive functionality** that needs real-world testing
- **Experimental plugins** or substantial plugin modifications
- **Framework changes** that could impact multiple workflows
- **Breaking changes** that need validation before full release

## 📋 Prerequisites

Before starting a beta release, ensure:

- ✅ **Comprehensive testing** - All automated tests pass
- ✅ **Code review** - Implementation has been reviewed
- ✅ **Documentation** - New features are documented
- ✅ **Version planning** - Know target beta and final version numbers
- ✅ **Environment setup** - Virtual environment and build tools ready

## 🚀 Beta Release Process (Option 1)

### Step 1: Prepare Development Environment

```bash
# Ensure you have build tools in virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install build twine

# Verify your setup
python --version
python -m build --help
python -m twine --help
```

### Step 2: Update Version for Beta

Edit `pyproject.toml`:

```toml
[project]
name = "asciidoc-dita-toolkit"
version = "0.1.8b2"  # Format: MAJOR.MINOR.PATCHbN (where N is beta number)
```

**Version Naming Convention:**
- `0.1.8b2` - Second beta of version 0.1.8
- `0.1.8b2` - Second beta if fixes are needed
- `0.1.8` - Final release version

### Step 3: Create Feature Branch

```bash
# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Add all new and modified files
git add .

# Commit with descriptive message
git commit -m "feat: Add [feature description]

- Brief description of main changes
- Key new capabilities added
- Version bump to X.X.XbN for beta testing"

# Push feature branch
git push origin feature/your-feature-name
```

### Step 4: Build and Test Package

```bash
# Activate virtual environment
source .venv/bin/activate

# IMPORTANT: Clean all build artifacts first
rm -rf dist/ build/ *.egg-info/

# Build distribution packages from clean state
python -m build

# Verify build output
ls -la dist/
# Should see: your-package-X.X.XbN-py3-none-any.whl and .tar.gz
```

**⚠️ Critical Step**: Always clean build artifacts before building. This prevents obsolete files from previous versions being packaged into the new distribution.

### Step 5: Create Docker Beta Image

```bash
# Build Docker image with beta tag
docker build -t rolfedh/asciidoc-dita-toolkit:beta .

# Test the beta image locally
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:beta --help

# Push to Docker Hub
docker push rolfedh/asciidoc-dita-toolkit:beta
```

### Step 6: Upload to PyPI

**Option A: Test PyPI First (Recommended)**
```bash
# Upload to test PyPI instance
python -m twine upload --repository testpypi dist/*

# Test installation from test PyPI
pip install --index-url https://test.pypi.org/simple/ asciidoc-dita-toolkit==0.1.8b2
```

**Option B: Direct to PyPI**
```bash
# Upload directly to main PyPI
python -m twine upload dist/*

# Verify availability
pip install asciidoc-dita-toolkit==0.1.8b2
```

### Step 7: Create GitHub Pre-release

```bash
# Tag the beta version
git tag v0.1.8b2
git push origin v0.1.8b2
```

Then on GitHub:
1. Go to **Releases** → **Create a new release**
2. Choose tag: `v0.1.8b2`
3. Target: `feature/your-feature-name` branch
4. Title: `v0.1.8b2 - [Feature Name] Beta`
5. ✅ **Check "This is a pre-release"**
6. Description: Link to beta testing guide and highlight new features

### Step 8: Create User Documentation

Create these documentation files in `/docs`:

1. **`BETA_TESTING_GUIDE.md`** - User testing instructions
2. **`BETA_RELEASE_PROCESS.md`** - This developer guide

Include in the beta testing guide:

- Installation instructions for both Docker and PyPI
- Specific testing scenarios
- Feedback collection process
- Known limitations or areas needing focus

### Step 9: Announce Beta (Do NOT Create PR Yet)

**Important**: At this stage, do **NOT** create a Pull Request to main. The feature branch should remain separate during the entire beta testing period.

**Why no PR during beta:**
- Beta testing might reveal issues requiring changes
- User feedback should be incorporated first
- Main branch should stay stable during beta period
- Final PR should represent the complete, tested feature

**Instead, announce the beta:**
- Create GitHub Discussion in "Announcements"
- Update README.md with beta testing callout
- Share through appropriate channels
- Monitor feedback and respond to users

## 📊 Managing Beta Feedback

### Feedback Collection

Set up feedback channels:
- **GitHub Issues** with `beta-feedback` label
- **GitHub Discussions** for general feedback
- **Direct contact** methods if needed

### Feedback Categorization

Organize feedback into:

| Category | Action | Timeline |
|----------|--------|----------|
| **Bugs** | Fix immediately | Before final release |
| **UX Issues** | Evaluate and fix if possible | Before final release |
| **Feature Requests** | Document for future versions | Post-release planning |
| **Performance Issues** | Investigate and optimize | Before final release |
| **Documentation** | Update docs | Before final release |

### Beta Iteration Process

If significant issues are found:

```bash
# Fix issues in feature branch
git checkout feature/your-feature-name
# Make fixes...
git commit -m "fix: Address beta feedback issues"

# Bump to next beta version
# Edit pyproject.toml: version = "0.1.8b2"

# Rebuild and redeploy
python -m build
docker build -t rolfedh/asciidoc-dita-toolkit:beta .
python -m twine upload dist/*
docker push rolfedh/asciidoc-dita-toolkit:beta

# Tag new beta
git tag v0.1.8b2
git push origin v0.1.8b2
```

## ✅ Final Release Process

**Only create a Pull Request after beta testing is complete and feedback is addressed.**

### Step 1: Prepare for Final Release

When beta testing is complete and feedback addressed:

```bash
# Update version to final
# Edit pyproject.toml: version = "0.1.8"

# Final commit
git commit -m "release: Finalize v0.1.8

- Address all beta feedback
- Update version to final release
- Ready for production use"
```

### Step 2: Create Pull Request

**Now is the time to create the PR:**

```bash
# Ensure feature branch is up to date
git checkout feature/your-feature-name
git push origin feature/your-feature-name
```

**Create PR with comprehensive description:**
- Summary of beta testing results
- Key feedback incorporated  
- Breaking changes (if any)
- Migration notes for users
- Link to beta testing discussion/issues

### Step 3: Merge to Main

After PR approval:

```bash
# Switch to main branch
git checkout main
git pull origin main

# Merge feature branch (or use GitHub merge)
git merge feature/your-feature-name

# Push to main
git push origin main
```

### Step 3: Create Final Release

```bash
# Build final packages
python -m build

# Upload to PyPI
python -m twine upload dist/*

# Build and push final Docker images
docker build -t rolfedh/asciidoc-dita-toolkit:latest .
docker build -t rolfedh/asciidoc-dita-toolkit:0.1.8 .
docker push rolfedh/asciidoc-dita-toolkit:latest
docker push rolfedh/asciidoc-dita-toolkit:0.1.8

# Tag final release
git tag v0.1.8
git push origin v0.1.8
```

### Step 4: GitHub Final Release

Create final release on GitHub:
1. Choose tag: `v0.1.8`
2. Target: `main` branch
3. ✅ **Uncheck "This is a pre-release"**
4. Include changelog with beta feedback improvements

### Step 5: Clean Up

```bash
# Delete feature branch (optional)
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name

# Archive beta tags if desired (optional)
```

## 📚 Post-Release Activities

### Update Documentation
- Update main README.md with new features
- Update CHANGELOG.md
- Archive beta testing guide or mark as completed

### Communication
- Announce release through appropriate channels
- Thank beta testers
- Document lessons learned for next beta cycle

### Monitor
- Watch for issues in production
- Monitor download stats and usage
- Gather ongoing feedback for future improvements

## 🔧 Troubleshooting Common Issues

### Build Problems
```bash
# Clean dist directory and all build artifacts (IMPORTANT!)
rm -rf dist/ build/ *.egg-info/

# Reinstall build tools
pip install --upgrade build twine

# Rebuild from clean state
python -m build
```

**⚠️ Important**: Always clean build artifacts before rebuilding. Leftover files from previous versions can cause packaging issues where obsolete files get included in the new distribution, leading to version conflicts and unexpected behavior.

### Docker Issues
```bash
# Clean Docker cache
docker system prune

# Rebuild without cache
docker build --no-cache -t rolfedh/asciidoc-dita-toolkit:beta .
```

### PyPI Upload Issues

```bash
# Check credentials
python -m twine check dist/*

# If you get "Metadata is missing required fields" error:
# This can happen with older Twine versions and newer pyproject.toml format
pip install --upgrade twine
python -m twine check dist/*

# Use API token instead of password
python -m twine upload --username __token__ --password pypi-... dist/*
```

### .pypirc Configuration Issues

If Twine prompts for API token when using `--repository testpypi` instead of reading from `.pypirc`:

**Issue**: Your `.pypirc` file may only have `[pypi]` section but not `[testpypi]`.

**Solution**: Update `~/.pypirc` to include both repositories:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PYPI_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_PYPI_TOKEN_HERE
```

**Note**: Test PyPI tokens may expire more frequently than production tokens. If you get "403 Forbidden" for test PyPI, you can proceed directly to production PyPI for beta releases since beta versions are appropriate for production PyPI as pre-releases.

## 📊 Success Metrics

Track these metrics during beta:

- **Downloads/Pulls** - Docker and PyPI stats
- **Feedback Volume** - Number of issues/comments
- **Bug Reports** - Critical issues found
- **Feature Adoption** - Usage of new features
- **User Retention** - Continued testing participation

## 🎯 Best Practices

### Do's
- ✅ **Set clear expectations** for beta timeline
- ✅ **Respond promptly** to feedback
- ✅ **Document everything** - decisions, issues, fixes
- ✅ **Test thoroughly** before each beta iteration
- ✅ **Communicate regularly** with testers

### Don'ts
- ❌ **Don't rush** to final release
- ❌ **Don't ignore** feedback, even if you disagree
- ❌ **Don't make** breaking changes during beta
- ❌ **Don't skip** testing iterations
- ❌ **Don't forget** to update documentation

---

## 📋 **Quick Reference Summary**

### Beta Phase Workflow:
1. ✅ **Feature branch** + beta version (v0.1.8b2)
2. ✅ **Build & distribute** (Docker, PyPI)  
3. ✅ **Create GitHub pre-release**
4. ✅ **Announce beta** (GitHub Discussions, README)
5. ⏳ **Gather feedback** (2-4 weeks)
6. 🔄 **Iterate if needed** (v0.1.8b2, etc.)

### Final Release Workflow:
7. ✅ **Address feedback** on feature branch
8. ✅ **Update to final version** (v0.1.8)
9. ✅ **Create Pull Request** (with beta summary)
10. ✅ **Merge to main** after approval
11. ✅ **Final release** and cleanup

### ⚠️ **Key Rule**:
**NO Pull Request during beta testing period!** PR comes only after beta is complete.

This process ensures high-quality releases while maximizing community input and maintaining project stability.
