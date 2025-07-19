# Beta Test Instructions: CrossReference Plugin

These steps will help you check out the beta branch, set up a Python environment, install the toolkit in editable mode, and test the new CrossReference plugin.

## 1. Clone the Repository and Checkout the Beta Branch

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/rolfedh/asciidoc-dita-toolkit.git
cd asciidoc-dita-toolkit

# Fetch all branches and checkout the beta branch
# Replace <branch-name> with the actual branch name if different
git fetch origin
# Example branch name:
git checkout cursor/integrate-and-merge-commit-as-pr-8c77
```

## 2. Create and Activate a Python Virtual Environment

```bash
# Create a new virtual environment in the project directory
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On Linux/macOS
# .venv\Scripts\activate  # On Windows
```

## 3. Install the Toolkit in Editable Mode

```bash
pip install --upgrade pip
pip install -e .
```

## 4. Verify Plugin Installation

```bash
adt --list-plugins
# You should see 'CrossReference' in the list of available plugins
```

## 5. Test the CrossReference Plugin

### Show Help
```bash
adt CrossReference --help
```

### Run on a Sample Project
```bash
# Example: Process a master.adoc file in your docs directory
adt CrossReference --master-file path/to/your/master.adoc

# Or recursively process all master.adoc files in a directory
adt CrossReference -r -d path/to/your/docs
```

## 6. Run the Full Test Suite (Optional)

```bash
pytest -v
# or
python3 -m pytest tests/ -v
```

## 7. Report Issues

If you encounter any problems, please report them with details about your environment and the steps to reproduce.

---
**Thank you for beta testing the CrossReference plugin!**
