#!/bin/bash
# Simple launcher script for AsciiDoc DITA Toolkit GUI
# This script can be used as a quick way to launch the GUI

echo "Starting AsciiDoc DITA Toolkit GUI..."
echo "If you encounter any issues, please ensure:"
echo "  - Python 3.7+ is installed"
echo "  - tkinter is available (python3-tk package on Linux)"
echo "  - asciidoc-dita-toolkit is installed (pip install asciidoc-dita-toolkit)"
echo ""

# Check if the toolkit is installed
if ! command -v asciidoc-dita-toolkit-gui &> /dev/null; then
    echo "Error: asciidoc-dita-toolkit-gui command not found."
    echo "Please install the toolkit first:"
    echo "  pip install asciidoc-dita-toolkit"
    exit 1
fi

# Launch the GUI
asciidoc-dita-toolkit-gui

echo "GUI closed. Thank you for using AsciiDoc DITA Toolkit!"
