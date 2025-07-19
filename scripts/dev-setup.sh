#!/bin/bash

# ADT development setup - creates venv and installs dependencies

set -e

echo "🚀 Starting ADT development environment setup..."
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
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
source .venv/bin/activate
pip install --upgrade pip
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
