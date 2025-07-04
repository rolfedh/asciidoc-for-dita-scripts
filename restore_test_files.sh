#!/bin/bash
# Restore test files from backup
# Usage: ./restore_test_files.sh

echo "Restoring test files from backup..."
cd "$(dirname "$0")"
rm -rf ./test_files/*
cp ./test_files_backup/* ./test_files/
echo "✅ Test files restored successfully!"
echo ""
echo "Available test files:"
ls -1 ./test_files/
