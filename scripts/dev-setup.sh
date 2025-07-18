#!/bin/bash

# ADT development setup - creates venv and installs dependencies

set -e

echo "Starting ADT setup..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Created virtual environment"
else
    echo "Virtual environment exists"
fi

source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt

echo "Setup complete"
echo "Active environment: $VIRTUAL_ENV"
echo ""
echo "Commands:"
echo "  adt -h"
echo "  adt --list-plugins"
echo ""
echo "Quality checks:"
echo "  make format"
echo "  make lint-clean"
echo "  make test"
