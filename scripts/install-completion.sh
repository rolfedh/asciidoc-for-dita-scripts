#!/usr/bin/env bash
# Install adt bash completion automatically for end users
#
# This script is designed to run automatically during package installation
# and will install completion for the current user without prompts.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPLETION_SCRIPT="$SCRIPT_DIR/adt-completion.bash"

# Automatic installation for end users (always user-level)
INSTALL_TYPE="user"

# Allow override for system installation if explicitly requested
if [[ "${1:-}" == "--system" ]]; then
    INSTALL_TYPE="system"
fi

# Check if completion script exists
if [[ ! -f "$COMPLETION_SCRIPT" ]]; then
    echo "❌ Error: Completion script not found at $COMPLETION_SCRIPT"
    exit 1
fi

# Install completion
case "$INSTALL_TYPE" in
    user)
        # User-specific installation
        COMPLETION_DIR="$HOME/.local/share/bash-completion/completions"
        TARGET_FILE="$COMPLETION_DIR/adt"
        
        echo "📦 Installing adt completion for current user..."
        mkdir -p "$COMPLETION_DIR"
        cp "$COMPLETION_SCRIPT" "$TARGET_FILE"
        chmod +x "$TARGET_FILE"
        
        echo "✅ Completion installed to: $TARGET_FILE"
        echo ""
        echo "To enable completion in your current shell:"
        echo "  source '$TARGET_FILE'"
        echo ""
        echo "For future shells, add this to your ~/.bashrc:"
        echo "  source '$TARGET_FILE'"
        echo ""
        echo "Or restart your shell to auto-load completions."
        ;;
        
    system)
        # System-wide installation
        COMPLETION_DIR="/etc/bash_completion.d"
        TARGET_FILE="$COMPLETION_DIR/adt"
        
        if [[ $EUID -ne 0 ]]; then
            echo "❌ Error: System installation requires sudo privileges"
            echo "Run: sudo $0 --system"
            exit 1
        fi
        
        echo "📦 Installing adt completion system-wide..."
        mkdir -p "$COMPLETION_DIR"
        cp "$COMPLETION_SCRIPT" "$TARGET_FILE"
        chmod +x "$TARGET_FILE"
        
        echo "✅ Completion installed to: $TARGET_FILE"
        echo ""
        echo "Completion will be available for all users after they restart their shell."
        ;;
esac

# Test if adt is available
if command -v adt >/dev/null 2>&1; then
    echo "🔧 Testing completion setup..."
    
    # Test the completion helper
    if python3 -m asciidoc_dita_toolkit.adt_core.completion modules >/dev/null 2>&1; then
        echo "✅ Dynamic module discovery working"
    else
        echo "⚠️  Dynamic module discovery failed - will use fallback module list"
    fi
    
    echo ""
    echo "🎉 Installation complete! Try tab completion:"
    echo "  adt <TAB><TAB>          # Show all available modules"
    echo "  adt User<TAB>           # Complete to UserJourney"
    echo "  adt ContentType <TAB>   # Show module options"
    echo "  adt journey <TAB>       # Show journey subcommands"
else
    echo ""
    echo "⚠️  Warning: 'adt' command not found in PATH"
    echo "   Make sure asciidoc-dita-toolkit is properly installed:"
    echo "   pip install -e ."
    echo ""
    echo "   Then restart your shell or run:"
    echo "   source '$TARGET_FILE'"
fi