#!/bin/bash

# Complete ADT development setup script
# This script creates a virtual environment, installs dependencies, 
# runs quality checks, and activates the environment for you.

set -e  # Exit on any error

echo "🚀 Starting complete ADT development setup..."

# Run the make setup command
make setup

echo ""
echo "🔧 Activating virtual environment..."

# Check if we're already in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Virtual environment already active: $VIRTUAL_ENV"
else
    # Activate the virtual environment
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        echo "✅ Virtual environment activated: $VIRTUAL_ENV"
    else
        echo "❌ Virtual environment not found at .venv/bin/activate"
        exit 1
    fi
fi

echo ""
echo "🎉 Setup complete! You can now use:"
echo "  adt -h                    # Show help"
echo "  adt --list-plugins        # List all plugins"
echo "  adt ContentType -h        # Plugin-specific help"
echo ""
echo "💡 Your virtual environment is now active."
echo "   To deactivate later: deactivate"
echo "   To reactivate: source .venv/bin/activate"

# Test that adt is working
echo ""
echo "🧪 Testing adt installation..."
if command -v adt >/dev/null 2>&1; then
    echo "✅ adt command is available"
    adt --version 2>/dev/null || echo "ℹ️  adt installed but version info not available"
else
    echo "⚠️  adt command not found in PATH, but should work with: python -m adt_core.cli"
fi

echo ""
echo "🎯 Ready for development!"
