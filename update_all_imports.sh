#!/bin/bash

# Script to update all old plugin imports to new module locations
cd /home/rolfedh/asciidoc-dita-toolkit

echo "Updating imports to use new module locations..."

# Function to update imports in a file
update_imports() {
    local file="$1"
    echo "Updating imports in $file..."

    # Update the main plugin imports
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.plugins\.EntityReference|asciidoc_dita_toolkit.modules.entity_reference|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.plugins\.ContentType|asciidoc_dita_toolkit.modules.content_type|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.plugins\.DirectoryConfig|asciidoc_dita_toolkit.modules.directory_config|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.plugins\.UserJourney|asciidoc_dita_toolkit.modules.user_journey|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.plugins\.ArchiveUnusedFiles|asciidoc_dita_toolkit.modules.archive_unused_files|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.plugins\.ExampleBlock|asciidoc_dita_toolkit.modules.example_block|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.plugins\.ContextAnalyzer|asciidoc_dita_toolkit.modules.context_analyzer|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.plugins\.ContextMigrator|asciidoc_dita_toolkit.modules.context_migrator|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.plugins\.CrossReference|asciidoc_dita_toolkit.modules.cross_reference|g' "$file"

    # Update supporting file imports
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.plugins\.content_type_detector|asciidoc_dita_toolkit.modules.content_type.content_type_detector|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.plugins\.content_type_processor|asciidoc_dita_toolkit.modules.content_type.content_type_processor|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.plugins\.ui_interface|asciidoc_dita_toolkit.modules.content_type.ui_interface|g' "$file"
    sed -i 's|asciidoc_dita_toolkit\.asciidoc_dita\.plugins\.userjourney_cli|asciidoc_dita_toolkit.modules.user_journey.userjourney_cli|g' "$file"
}

# Update all test files
find tests -name "*.py" -type f | while read file; do
    update_imports "$file"
done

# Update any other Python files that might have old imports
find docs -name "*.py" -type f | while read file; do
    update_imports "$file"
done

# Update any remaining files in the archive directory for completeness
find archive -name "*.py" -type f | while read file; do
    update_imports "$file"
done

echo "Import updates completed!"
