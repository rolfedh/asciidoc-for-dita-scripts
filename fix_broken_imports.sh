#!/bin/bash

# Script to fix broken imports after the migration
cd /home/rolfedh/asciidoc-dita-toolkit

echo "Fixing broken imports in migrated modules..."

# Function to fix imports in a file
fix_broken_imports() {
    local file="$1"
    echo "Fixing broken imports in $file..."

    # Fix common misnamed imports that appeared during the migration
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_ditafile_utils|asciidoc_dita_toolkit.asciidoc_dita.file_utils|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_ditaconfig_utils|asciidoc_dita_toolkit.asciidoc_dita.config_utils|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_ditasecurity_utils|asciidoc_dita_toolkit.asciidoc_dita.security_utils|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_ditatask_interface|asciidoc_dita_toolkit.asciidoc_dita.task_interface|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_ditauser_config|asciidoc_dita_toolkit.asciidoc_dita.user_config|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_ditafixtures_utils|asciidoc_dita_toolkit.asciidoc_dita.fixtures_utils|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_ditaworkflow_utils|asciidoc_dita_toolkit.asciidoc_dita.workflow_utils|g' "$file"

    # Handle any remaining double-prefixed imports that got mangled
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.asciidoc_dita\.|asciidoc_dita_toolkit.asciidoc_dita.|g' "$file"
}

# Fix all Python files in the modules directory
find asciidoc_dita_toolkit/modules -name "*.py" -type f | while read file; do
    fix_broken_imports "$file"
done

echo "Broken import fixing completed!"
