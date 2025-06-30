#!/bin/bash
# fetch-fixtures.sh: Download test fixtures from asciidoctor-dita-vale
set -e
trap 'rm -rf temp-vale' EXIT

git clone --depth 1 --filter=blob:none --sparse https://github.com/jhradilek/asciidoctor-dita-vale.git temp-vale
cd temp-vale
git sparse-checkout set fixtures
cd ..

# Preserve existing .expected files if they exist
if [ -d "tests/fixtures" ]; then
    echo "Preserving existing .expected files..."
    # Create temporary backup directory
    mkdir -p temp-expected-backup
    
    # Find and copy all .expected files, preserving directory structure
    if find tests/fixtures -name "*.expected" -print0 2>/dev/null | grep -zq .; then
        find tests/fixtures -name "*.expected" -print0 | while IFS= read -r -d '' file; do
            # Get relative path from tests/fixtures
            rel_path="${file#tests/fixtures/}"
            # Create directory structure in backup
            mkdir -p "temp-expected-backup/$(dirname "$rel_path")"
            # Copy the file
            cp "$file" "temp-expected-backup/$rel_path"
        done
        echo "Backed up .expected files to temp-expected-backup/"
    else
        echo "No .expected files found to preserve."
    fi
    
    echo "Removing existing tests/fixtures directory..."
    rm -rf tests/fixtures
fi

# Move new fixtures
mv temp-vale/fixtures tests/

# Restore .expected files if they were backed up
if [ -d "temp-expected-backup" ]; then
    echo "Restoring preserved .expected files..."
    find temp-expected-backup -name "*.expected" -print0 | while IFS= read -r -d '' file; do
        # Get relative path from backup directory
        rel_path="${file#temp-expected-backup/}"
        # Ensure target directory exists
        mkdir -p "tests/fixtures/$(dirname "$rel_path")"
        # Copy file back
        cp "$file" "tests/fixtures/$rel_path"
    done
    rm -rf temp-expected-backup
    echo "Restored .expected files."
fi

rm -rf temp-vale

echo "Downloaded test fixtures from asciidoctor-dita-vale to tests/fixtures"
