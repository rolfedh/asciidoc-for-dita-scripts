#!/bin/bash

# ADT development setup - creates venv and installs dependencies



echo "🚀 Starting ADT development environment setup..."
echo ""

# Check if we're in the right directory

if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    read -p "Press Enter to close the terminal..."
    return 1 2>/dev/null || exit 1
fi

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created at .venv"
else
    echo "📦 Virtual environment already exists at .venv"
fi

# Activate and install dependencies
echo "📥 Installing dependencies..."
echo "🔧 Setting up virtual environment..."
source .venv/bin/activate
echo "🔄 Upgrading pip..."
if ! pip install --upgrade pip; then
    echo "❌ Error: Failed to upgrade pip. Please check your network connection or pip configuration."
    deactivate
    read -p "Press Enter to close the terminal..."
    return 1 2>/dev/null || exit 1
fi
pip install -e .
pip install -r requirements-dev.txt

echo ""
echo "✅ Setup complete!"
echo "🌍 Active environment: $VIRTUAL_ENV"
echo ""
echo "Commands:"
echo "  adt -h"
echo "  adt --list-plugins"
echo ""
echo "Quality checks:"
echo "  make format"
echo "  make lint-clean"
echo "  make test"
