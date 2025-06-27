#!/bin/bash
# fetch-fixtures.sh: Download test fixtures from asciidoctor-dita-vale
set -e
trap 'rm -rf temp-vale' EXIT

git clone --depth 1 --filter=blob:none --sparse https://github.com/jhradilek/asciidoctor-dita-vale.git temp-vale
cd temp-vale
git sparse-checkout set fixtures
cd ..
if [ -d "tests/fixtures" ]; then
    echo "Directory tests/fixtures already exists. Removing it..."
    rm -rf tests/fixtures
fi
mv temp-vale/fixtures tests/
rm -rf temp-vale

echo "Downloaded test fixtures from asciidoctor-dita-vale to tests/fixtures"
