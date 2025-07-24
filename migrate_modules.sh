#!/bin/bash

# Module migration script
cd /home/rolfedh/asciidoc-dita-toolkit

# Define the modules and their files
declare -A modules=(
    ["entity_reference"]="EntityReference.py"
    ["directory_config"]="DirectoryConfig.py"
    ["user_journey"]="UserJourney.py userjourney_cli.py"
    ["archive_unused_files"]="ArchiveUnusedFiles.py"
    ["example_block"]="ExampleBlock.py"
    ["context_analyzer"]="ContextAnalyzer.py"
    ["context_migrator"]="ContextMigrator.py"
    ["cross_reference"]="CrossReference.py"
)

# Copy modules to new locations
for module_name in "${!modules[@]}"; do
    echo "Migrating $module_name..."
    files=${modules[$module_name]}

    for file in $files; do
        if [ -f "asciidoc_dita_toolkit/asciidoc_dita/plugins/$file" ]; then
            if [ "$file" = "${module_name^}.py" ] || [ "$file" = "${module_name^}s.py" ]; then
                # Main module file becomes __init__.py
                cp "asciidoc_dita_toolkit/asciidoc_dita/plugins/$file" "asciidoc_dita_toolkit/modules/$module_name/__init__.py"
            else
                # Supporting files keep their names
                cp "asciidoc_dita_toolkit/asciidoc_dita/plugins/$file" "asciidoc_dita_toolkit/modules/$module_name/"
            fi
            echo "  Copied $file"
        else
            echo "  Warning: $file not found"
        fi
    done
done

echo "Module migration completed!"
