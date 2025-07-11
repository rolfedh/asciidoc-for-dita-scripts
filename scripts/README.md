# Scripts Directory

This directory contains utility scripts for the AsciiDoc DITA Toolkit project.

## 🎬 Demo & Presentation Scripts

### [`demo_v2.sh`](demo_v2.sh) ⭐ **Main Demo Script**
Complete interactive demonstration of AsciiDoc DITA Toolkit v2.0.x features.

**Usage:**
```bash
./scripts/demo_v2.sh
```

**Features:**
- 5-section structured presentation (~10 minutes)
- Live CLI demonstrations with real file processing
- Color-coded output with pause points for narration
- Automatic cleanup after demo

**Sections:**
1. **The Problem** (30s) - Show old fragmented experience
2. **The Solution** (2m) - Unified package installation
3. **The Features** (5m) - All 6 plugins in action
4. **Developer Experience** (2m) - PyPI, testing, documentation
5. **The Impact** (1m) - Business and technical benefits

### [`DEMO_PRESENTATION.md`](DEMO_PRESENTATION.md) 📊 **Presentation Slides**
Comprehensive markdown presentation document with:
- Executive summary and key metrics
- Before/after comparisons
- Technical details and business impact
- Q&A preparation

### [`demo_quick_reference.md`](demo_quick_reference.md) 📝 **Quick Reference Card**
Presenter's cheat sheet with:
- Key talking points for each section
- Demo highlights to emphasize
- Prepared answers for common questions
- Emergency fallback options

### [`pre_demo_check.sh`](pre_demo_check.sh) 🔍 **Pre-Demo System Check**
Validates system requirements before presentation.

**Usage:**
```bash
./scripts/pre_demo_check.sh                # Basic checks
./scripts/pre_demo_check.sh --test-install # Include PyPI installation test
```

**Checks:**
- Python 3 and pip availability
- PyPI connectivity
- Disk space and script permissions
- Optional: Full installation test

## 🔧 Development Scripts

### [`container.sh`](container.sh) 🐳 **Container Management**
Docker container operations for development and testing.

**Usage:**
```bash
./scripts/container.sh build    # Build container
./scripts/container.sh test     # Run tests in container
./scripts/container.sh shell    # Interactive shell
```

### [`generate-changelog.sh`](generate-changelog.sh) 📰 **Changelog Generation**
Automated changelog generation from git history.

**Usage:**
```bash
./scripts/generate-changelog.sh
```

## 🧹 Maintenance Scripts

### [`delete_stale_branches.sh`](delete_stale_branches.sh) 🗑️ **Branch Cleanup**
Interactive tool for cleaning up stale GitHub branches.

**Usage:**
```bash
./scripts/delete_stale_branches.sh
```

**Features:**
- Interactive menu with safety prompts
- Delete by category (cursor/, feature/, fix-, refactor/)
- Custom regex pattern matching
- Comprehensive branch listing and statistics

**Prerequisites:**
- GitHub CLI (`gh`) installed and authenticated
- `jq` for JSON parsing

## 🚀 Quick Start for Demo Day

1. **Pre-flight check:**
   ```bash
   ./scripts/pre_demo_check.sh --test-install
   ```

2. **Run the demo:**
   ```bash
   ./scripts/demo_v2.sh
   ```

3. **Have references ready:**
   - [`DEMO_PRESENTATION.md`](DEMO_PRESENTATION.md) - Background slides
   - [`demo_quick_reference.md`](demo_quick_reference.md) - Talking points

## 📋 Script Permissions

All scripts should be executable. If not:
```bash
chmod +x scripts/*.sh
```

## 🆘 Troubleshooting

### Demo Script Issues
- **Permission denied**: Run `chmod +x scripts/demo_v2.sh`
- **Python not found**: Ensure Python 3 is installed and in PATH
- **PyPI connection**: Check internet connectivity

### Branch Cleanup Issues  
- **gh not found**: Install GitHub CLI from https://cli.github.com/
- **Not authenticated**: Run `gh auth login`
- **jq not found**: Install with `sudo apt install jq` (Ubuntu) or `brew install jq` (macOS)

### Container Issues
- **Docker not running**: Start Docker daemon
- **Permission denied**: Add user to docker group or use sudo

---

*Last updated: [Current Date]*  
*AsciiDoc DITA Toolkit v2.0.x*
