#!/bin/bash
# generate-changelog.sh: Generate changelog entry for a specific version
set -e

VERSION=${1:-$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//')}
RELEASE_DATE=${2:-$(date +'%Y-%m-%d')}

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version> [release_date]"
    echo "Example: $0 0.1.7 2025-06-30"
    exit 1
fi

echo "Generating changelog entry for version $VERSION..."

# Get the previous tag
PREV_TAG=$(git describe --tags --abbrev=0 v${VERSION}^2 2>/dev/null || echo "")

if [ -z "$PREV_TAG" ]; then
    echo "Getting all commits since repository start..."
    RANGE=""  # Empty range means all commits
else
    echo "Getting commits since $PREV_TAG..."
    RANGE="${PREV_TAG}..v${VERSION}"
fi

# Generate changelog entry
echo "## [$VERSION] - $RELEASE_DATE" > changelog_entry.txt
echo "" >> changelog_entry.txt

# Look for merged PRs
CHANGES=$(git log --oneline --grep="Merge pull request" $RANGE --reverse | while read line; do
    if [[ $line =~ "Merge pull request #"([0-9]+)" from" ]]; then
        PR_NUM=${BASH_REMATCH[1]}
        # Try to get PR title from git log
        PR_TITLE=$(git log --grep="#${PR_NUM}" --format="%s" -1 2>/dev/null | head -1)
        if [ ! -z "$PR_TITLE" ] && [[ ! $PR_TITLE =~ ^Merge ]]; then
            # Clean up the title
            CLEAN_TITLE=$(echo "$PR_TITLE" | sed -E 's/^(feat|fix|refactor|docs|test|chore|style)(\([^)]*\))?:\s*//i' | sed 's/^./\U&/')
            echo "- $CLEAN_TITLE"
        fi
    fi
done)

# If no PR changes found, use commit messages
if [ -z "$CHANGES" ]; then
    CHANGES=$(git log --oneline $RANGE --reverse | while read line; do
        if [[ $line =~ ^[a-f0-9]+\ (.+)$ ]]; then
            COMMIT_MSG=${BASH_REMATCH[1]}
            if [[ ! $COMMIT_MSG =~ ^Merge ]] && [[ ! $COMMIT_MSG =~ ^docs:.*changelog ]]; then
                CLEAN_MSG=$(echo "$COMMIT_MSG" | sed -E 's/^(feat|fix|refactor|docs|test|chore|style)(\([^)]*\))?:\s*//i' | sed 's/^./\U&/')
                echo "- $CLEAN_MSG"
            fi
        fi
    done)
fi

echo "$CHANGES" >> changelog_entry.txt

echo ""
echo "Generated changelog entry:"
echo "========================="
cat changelog_entry.txt
echo "========================="
echo ""
echo "To add this to CHANGELOG.md, run:"
echo "  1. Edit CHANGELOG.md"
echo "  2. Add the content above after the [Unreleased] section"
echo "  3. Update the [Unreleased] section with new changes if needed"

# Optionally auto-update CHANGELOG.md
# Only prompt when run interactively (not from make or CI)
if [[ -t 0 && -t 1 && -z "$CI" && -z "$MAKE_LEVEL" ]]; then
    read -p "Automatically update CHANGELOG.md? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        UPDATE_CHANGELOG=true
    else
        UPDATE_CHANGELOG=false
    fi
else
    # Automatically update changelog in non-interactive contexts
    echo "Automatically updating CHANGELOG.md (running in automated context)"
    UPDATE_CHANGELOG=true
fi

if [[ "$UPDATE_CHANGELOG" == "true" ]]; then
    # Check if version already exists
    if grep -q "## \[$VERSION\]" CHANGELOG.md; then
        echo "Version $VERSION already exists in CHANGELOG.md"
        exit 1
    fi
    # Create backup
    cp CHANGELOG.md CHANGELOG.md.bak
    # Update changelog
    {
        sed '/## \[Unreleased\]/q' CHANGELOG.md
        echo
        cat changelog_entry.txt
        echo
        sed -n '/## \[Unreleased\]/,$p' CHANGELOG.md | tail -n +2
    } > CHANGELOG_new.md
    mv CHANGELOG_new.md CHANGELOG.md
    echo "CHANGELOG.md updated successfully!"
    echo "Backup saved as CHANGELOG.md.bak"
fi

rm -f changelog_entry.txt
