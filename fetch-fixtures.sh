#!/bin/bash
# fetch-fixtures.sh: Download test fixtures from asciidoctor-dita-vale
set -e

# Create a temporary directory and ensure it's cleaned up on exit
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Clone the full fixtures directory from the repository
git clone --depth 1 https://github.com/jhradilek/asciidoctor-dita-vale.git "$TEMP_DIR/repo"

# Define source and destination paths
SRC_FIXTURES="$TEMP_DIR/repo/fixtures"
DEST_FIXTURES="tests/fixtures"

# Remove the old fixtures directory if it exists
if [ -d "$DEST_FIXTURES" ]; then
    echo "Directory $DEST_FIXTURES already exists. Removing it..."
    rm -rf "$DEST_FIXTURES"
fi

# Move the new fixtures into place
mv "$SRC_FIXTURES" "tests/"

echo "Successfully downloaded test fixtures to $DEST_FIXTURES"
