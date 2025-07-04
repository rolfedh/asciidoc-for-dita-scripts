@echo off
REM Simple launcher script for AsciiDoc DITA Toolkit GUI (Windows)
REM This script can be used as a quick way to launch the GUI

echo Starting AsciiDoc DITA Toolkit GUI...
echo If you encounter any issues, please ensure:
echo   - Python 3.7+ is installed
echo   - asciidoc-dita-toolkit is installed (pip install asciidoc-dita-toolkit)
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Launch the GUI
asciidoc-dita-toolkit-gui

echo GUI closed. Thank you for using AsciiDoc DITA Toolkit!
pause
