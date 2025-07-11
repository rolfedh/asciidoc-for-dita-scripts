#!/bin/bash

# GitHub Branch Cleanup Tool
# ==========================
# 
# This script helps you safely delete stale branches from your GitHub repository.
# It provides an interactive menu to delete branches by category or pattern.
#
# PREREQUISITES:
# - GitHub CLI (gh) must be installed and authenticated
# - jq must be installed for JSON parsing
# - Repository: rolfedh/asciidoc-dita-toolkit
#
# USAGE:
#   ./delete_stale_branches.sh
#
# FEATURES:
# - Interactive menu with safety prompts
# - Delete branches by category (cursor/, feature/, fix-, refactor/)
# - Delete branches by custom regex pattern
# - List all branches with numbering
# - Show branch counts by category
# - Color-coded output for better readability
#
# SAFETY FEATURES:
# - Always prompts before deletion
# - Shows which branches will be deleted
# - Protects 'main' branch from deletion
# - Individual error handling for each branch
#
# RECOMMENDED DELETION ORDER:
# 1. Start with cursor/* branches (AI-generated, usually safe to delete)
# 2. Delete fix-* branches (old bug fixes, likely merged)
# 3. Review feature/* branches individually
# 4. Use custom patterns for specific cleanup needs
#
# EXAMPLES:
# - Delete all cursor branches: Choose option 2
# - Delete branches starting with 'test-': Choose option 6, enter '^test-'
# - List all branches to review: Choose option 7
#
# NOTE: This script only deletes remote branches on GitHub.
# Local branches in your repository clone are not affected.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}GitHub Branch Cleanup Tool${NC}"
echo "================================================"

# Check if gh is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Check if jq is installed for JSON parsing
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is not installed${NC}"
    echo "Install it with: sudo apt install jq  (or brew install jq on macOS)"
    exit 1
fi

REPO="rolfedh/asciidoc-dita-toolkit"

echo -e "${YELLOW}Fetching branch list...${NC}"
BRANCHES=$(gh api repos/$REPO/branches --paginate | jq -r '.[] | select(.name != "main") | .name')

echo -e "${GREEN}Found $(echo "$BRANCHES" | wc -l) branches (excluding main)${NC}"
echo ""

# Function to delete branches by pattern
# Parameters:
#   $1 - regex pattern to match branch names
#   $2 - human-readable description of the branch type
delete_by_pattern() {
    local pattern="$1"
    local description="$2"
    
    echo -e "${YELLOW}Branches matching pattern '$pattern':${NC}"
    echo "$BRANCHES" | grep -E "$pattern" | head -10
    if [ $(echo "$BRANCHES" | grep -E "$pattern" | wc -l) -gt 10 ]; then
        echo "... (showing first 10, there are more)"
    fi
    
    local count=$(echo "$BRANCHES" | grep -E "$pattern" | wc -l)
    echo -e "${GREEN}Found $count branches matching '$pattern'${NC}"
    
    if [ $count -eq 0 ]; then
        echo "No branches found matching pattern."
        return
    fi
    
    echo -e "${YELLOW}Delete all $count $description branches? (y/N)${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Deleting $count branches..."
        local deleted=0
        local failed=0
        
        echo "$BRANCHES" | grep -E "$pattern" | while read -r branch; do
            echo -n "Deleting: $branch ... "
            if gh api -X DELETE repos/$REPO/git/refs/heads/$branch 2>/dev/null; then
                echo -e "${GREEN}✓ Deleted${NC}"
                ((deleted++))
            else
                echo -e "${RED}✗ Failed${NC}"
                ((failed++))
            fi
        done
        
        echo -e "${GREEN}Deletion complete: $deleted deleted, $failed failed${NC}"
    else
        echo "Skipped $description branches."
    fi
    echo ""
}

# Function to list branches by category
# Shows count of branches in each common category
list_branches() {
    echo -e "${GREEN}Branch Categories:${NC}"
    echo "===================="
    
    local cursor_count=$(echo "$BRANCHES" | grep -E "^cursor/" | wc -l)
    echo -e "${YELLOW}Cursor branches (AI-generated):${NC} $cursor_count"
    if [ $cursor_count -gt 0 ]; then
        echo "$BRANCHES" | grep -E "^cursor/" | head -3 | sed 's/^/  - /'
        [ $cursor_count -gt 3 ] && echo "  ... and $((cursor_count - 3)) more"
    fi
    echo
    
    local feature_count=$(echo "$BRANCHES" | grep -E "^feature/" | wc -l)
    echo -e "${YELLOW}Feature branches:${NC} $feature_count"
    if [ $feature_count -gt 0 ]; then
        echo "$BRANCHES" | grep -E "^feature/" | head -3 | sed 's/^/  - /'
        [ $feature_count -gt 3 ] && echo "  ... and $((feature_count - 3)) more"
    fi
    echo
    
    local fix_count=$(echo "$BRANCHES" | grep -E "^fix-" | wc -l)
    echo -e "${YELLOW}Fix branches (bug fixes):${NC} $fix_count"
    if [ $fix_count -gt 0 ]; then
        echo "$BRANCHES" | grep -E "^fix-" | head -3 | sed 's/^/  - /'
        [ $fix_count -gt 3 ] && echo "  ... and $((fix_count - 3)) more"
    fi
    echo
    
    local refactor_count=$(echo "$BRANCHES" | grep -E "^refactor/" | wc -l)
    echo -e "${YELLOW}Refactor branches:${NC} $refactor_count"
    if [ $refactor_count -gt 0 ]; then
        echo "$BRANCHES" | grep -E "^refactor/" | head -3 | sed 's/^/  - /'
        [ $refactor_count -gt 3 ] && echo "  ... and $((refactor_count - 3)) more"
    fi
    echo
    
    local other_count=$(echo "$BRANCHES" | grep -v -E "^(cursor/|feature/|fix-|refactor/)" | wc -l)
    echo -e "${YELLOW}Other branches:${NC} $other_count"
    if [ $other_count -gt 0 ]; then
        echo "$BRANCHES" | grep -v -E "^(cursor/|feature/|fix-|refactor/)" | head -5 | sed 's/^/  - /'
        [ $other_count -gt 5 ] && echo "  ... and $((other_count - 5)) more"
    fi
    echo
    
    echo -e "${GREEN}Total branches (excluding main): $(echo "$BRANCHES" | wc -l)${NC}"
    echo ""
}

# Main menu
while true; do
    echo -e "${GREEN}Choose an option:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1. 📊 List branch categories and counts"
    echo "2. 🤖 Delete all cursor/* branches (AI-generated, usually safe)"
    echo "3. 🚀 Delete all feature/* branches (review recommended)"
    echo "4. 🐛 Delete all fix-* branches (old bug fixes, usually safe)"
    echo "5. 🔧 Delete all refactor/* branches (code restructuring)"
    echo "6. 🎯 Delete branches by custom pattern (advanced)"
    echo "7. 📋 List all branches with numbers"
    echo "8. 🚪 Exit"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    read -p "Enter your choice (1-8): " choice
    
    case $choice in
        1)
            list_branches
            ;;
        2)
            delete_by_pattern "^cursor/" "cursor"
            ;;
        3)
            delete_by_pattern "^feature/" "feature"
            ;;
        4)
            delete_by_pattern "^fix-" "fix"
            ;;
        5)
            delete_by_pattern "^refactor/" "refactor"
            ;;
        6)
            echo ""
            echo -e "${YELLOW}Custom Pattern Deletion${NC}"
            echo "Enter a regex pattern to match branch names:"
            echo "Examples:"
            echo "  '^test-'     - branches starting with 'test-'"
            echo "  'experiment' - branches containing 'experiment'"
            echo "  '^backup'    - branches starting with 'backup'"
            echo ""
            read -p "Pattern: " pattern
            echo ""
            read -p "Description for these branches: " desc
            delete_by_pattern "$pattern" "$desc"
            ;;
        7)
            echo -e "${GREEN}All branches (excluding main):${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "$BRANCHES" | nl
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            ;;
        8)
            echo -e "${GREEN}Cleanup complete! Goodbye! 👋${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid choice. Please enter a number between 1-8.${NC}"
            echo ""
            ;;
    esac
done
