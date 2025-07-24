#!/bin/bash

# Script to fix relative imports in migrated modules
cd /home/rolfedh/asciidoc-dita-toolkit

echo "Fixing relative imports in migrated modules..."

# Find all Python files in the modules directory
find asciidoc_dita_toolkit/modules -name "*.py" -type f | while read file; do
    echo "Processing $file..."

    # Fix common relative import patterns
    sed -i 's|from \.\.cli_utils|from asciidoc_dita_toolkit.asciidoc_dita.cli_utils|g' "$file"
    sed -i 's|from \.\.plugin_manager|from asciidoc_dita_toolkit.asciidoc_dita.plugin_manager|g' "$file"
    sed -i 's|from \.\.workflow_utils|from asciidoc_dita_toolkit.asciidoc_dita.workflow_utils|g' "$file"
    sed -i 's|from \.\.user_config|from asciidoc_dita_toolkit.asciidoc_dita.user_config|g' "$file"
    sed -i 's|from \.\.task_interface|from asciidoc_dita_toolkit.asciidoc_dita.task_interface|g' "$file"
    sed -i 's|from \.\.fixtures_utils|from asciidoc_dita_toolkit.asciidoc_dita.fixtures_utils|g' "$file"

    # Fix other patterns that might exist
    sed -i 's|from \.\.|from asciidoc_dita_toolkit.asciidoc_dita|g' "$file"
done

echo "Relative import fixing completed!"
