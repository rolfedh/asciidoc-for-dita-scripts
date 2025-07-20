#!/bin/bash
# Test that version bumping paths are correct

echo "🧪 Testing version bumping path fixes..."

echo ""
echo "✅ Testing file existence:"
if [ -f "../asciidoc_dita_toolkit/adt_core/__init__.py" ]; then
    echo "   ✓ File exists at asciidoc_dita_toolkit/adt_core/__init__.py"
else
    echo "   ✗ File not found at expected location"
    exit 1
fi

echo ""
echo "✅ Testing current version detection:"
current_version=$(grep '^__version__ = ' ../asciidoc_dita_toolkit/adt_core/__init__.py | sed 's/__version__ = "\(.*\)"/\1/')
echo "   ✓ Current version detected: $current_version"

echo ""
echo "✅ Testing bump-version target path:"
if make -n -C .. bump-version VERSION=test 2>&1 | grep -q "asciidoc_dita_toolkit/adt_core/__init__.py"; then
    echo "   ✓ bump-version target uses correct path"
else
    echo "   ✗ bump-version target path incorrect"
    exit 1
fi

echo ""
echo "✅ Testing publish target path:"
if make -n -C .. publish 2>&1 | grep -q "asciidoc_dita_toolkit/adt_core/__init__.py"; then
    echo "   ✓ publish target uses correct path"
else
    echo "   ✗ publish target path incorrect"
    exit 1
fi

echo ""
echo "✅ Testing release target path:"
if make -n -C .. release 2>&1 | grep -q "asciidoc_dita_toolkit/adt_core/__init__.py"; then
    echo "   ✓ release target uses correct path"
else
    echo "   ✗ release target path incorrect"
    exit 1
fi

echo ""
echo "🎉 All path fixes verified successfully!"
echo ""
echo "📋 Summary of fixes:"
echo "   • Updated bump-version target to use asciidoc_dita_toolkit/adt_core/__init__.py"
echo "   • Updated publish target to use asciidoc_dita_toolkit/adt_core/__init__.py"  
echo "   • Updated release target to use asciidoc_dita_toolkit/adt_core/__init__.py"
echo "   • Updated git add commands to reference correct path"
echo "   • All targets will now properly update version in both files"
