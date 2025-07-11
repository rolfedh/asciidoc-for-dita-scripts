#!/bin/bash

# Pre-Demo System Check
# =====================
# Run this script before your presentation to ensure everything works

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🔍 Pre-Demo System Check${NC}"
echo "================================="

# Check Python
echo -n "Checking Python 3... "
if python3 --version >/dev/null 2>&1; then
    echo -e "${GREEN}✓ $(python3 --version)${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

# Check pip
echo -n "Checking pip... "
if python3 -m pip --version >/dev/null 2>&1; then
    echo -e "${GREEN}✓ pip available${NC}"
else
    echo -e "${RED}✗ pip not available${NC}"
    exit 1
fi

# Check if adt is already installed
echo -n "Checking if adt is installed... "
if command -v adt >/dev/null 2>&1; then
    echo -e "${GREEN}✓ adt available ($(adt --version 2>/dev/null | head -1))${NC}"
else
    echo -e "${YELLOW}⚠ adt not in PATH (will be installed during demo)${NC}"
fi

# Check PyPI connectivity
echo -n "Checking PyPI connectivity... "
if python3 -m pip search asciidoc-dita-toolkit >/dev/null 2>&1 || curl -s https://pypi.org/pypi/asciidoc-dita-toolkit/json >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PyPI accessible${NC}"
else
    echo -e "${YELLOW}⚠ PyPI connectivity issue (may affect live install demo)${NC}"
fi

# Check available disk space
echo -n "Checking disk space... "
AVAILABLE=$(df . | tail -1 | awk '{print $4}')
if [ "$AVAILABLE" -gt 100000 ]; then  # 100MB
    echo -e "${GREEN}✓ Sufficient space${NC}"
else
    echo -e "${YELLOW}⚠ Low disk space (${AVAILABLE}KB available)${NC}"
fi

# Test demo script syntax
echo -n "Checking demo script syntax... "
if bash -n scripts/demo_v2.sh 2>/dev/null; then
    echo -e "${GREEN}✓ Demo script syntax OK${NC}"
else
    echo -e "${RED}✗ Demo script has syntax errors${NC}"
    exit 1
fi

# Check demo script is executable
echo -n "Checking demo script permissions... "
if [ -x scripts/demo_v2.sh ]; then
    echo -e "${GREEN}✓ Demo script is executable${NC}"
else
    echo -e "${YELLOW}⚠ Making demo script executable...${NC}"
    chmod +x scripts/demo_v2.sh
    echo -e "${GREEN}✓ Fixed${NC}"
fi

# Quick install test (optional - only if requested)
if [ "$1" = "--test-install" ]; then
    echo ""
    echo -e "${YELLOW}🧪 Testing PyPI Installation (--test-install flag)${NC}"
    echo "=================================================="
    
    # Create temporary environment
    TEMP_ENV="temp_demo_test_$$"
    python3 -m venv "$TEMP_ENV"
    source "$TEMP_ENV/bin/activate"
    
    echo "Installing asciidoc-dita-toolkit from PyPI..."
    pip install asciidoc-dita-toolkit >/dev/null 2>&1
    
    echo -n "Testing installation... "
    if adt --version >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Installation test passed${NC}"
    else
        echo -e "${RED}✗ Installation test failed${NC}"
        deactivate
        rm -rf "$TEMP_ENV"
        exit 1
    fi
    
    deactivate
    rm -rf "$TEMP_ENV"
fi

echo ""
echo -e "${GREEN}🎉 All checks passed! Ready for demo presentation.${NC}"
echo ""
echo -e "${YELLOW}💡 Demo commands:${NC}"
echo "  ./scripts/demo_v2.sh                    # Run full interactive demo"
echo "  ./scripts/pre_demo_check.sh --test-install  # Test PyPI installation"
echo ""
echo -e "${YELLOW}📚 Reference materials:${NC}"
echo "  scripts/DEMO_PRESENTATION.md           # Presentation slides"
echo "  scripts/demo_quick_reference.md        # Quick reference card"
