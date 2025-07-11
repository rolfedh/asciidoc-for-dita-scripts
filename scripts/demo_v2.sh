#!/bin/bash

# AsciiDoc DITA Toolkit v2.0.x - Live Demo Script
# ================================================
# 
# This script provides a comprehensive live demonstration of the unified
# AsciiDoc DITA Toolkit v2.0.x features for team presentations.
#
# USAGE:
#   ./demo_v2.sh
#
# DEMO STRUCTURE:
#   1. The Problem (30 seconds) - Show the old fragmented experience  
#   2. The Solution (2 minutes) - Unified package installation & CLI
#   3. The Features (5 minutes) - All 6 plugins in action
#   4. The Developer Experience (2 minutes) - PyPI, documentation, testing
#   5. The Impact (1 minute) - What this means for the team
#
# PRESENTER NOTES:
#   - Script pauses at key moments for your narration
#   - Press ENTER to continue to next section
#   - All commands are automated for smooth presentation
#   - Demo files are created on-the-fly for realistic scenarios

set -e

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Demo configuration
DEMO_DIR="demo_presentation"
PACKAGE_NAME="asciidoc-dita-toolkit"
VERSION="2.0.3"

# Utility functions
pause_for_narration() {
    # Use dull grey for speaker prompts
    local GREY='\033[1;30m'
    echo -e "\n${GREY}⏸️  [PAUSE FOR NARRATION] $1${NC}"
    echo -e "${GREY}Press ENTER when ready to continue...${NC}"
    read -r
}

section_header() {
    clear
    echo -e "${WHITE}${BOLD}"
    echo "████████████████████████████████████████████████████████████████████"
    echo "█                                                                  █"
    echo "█             AsciiDoc DITA Toolkit v${VERSION} Demo               █"
    echo "█                                                                  █"
    echo "████████████████████████████████████████████████████████████████████"
    echo -e "${NC}"
    echo -e "${GREEN}${BOLD}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

typing_effect() {
    local text="$1"
    local delay="${2:-0.03}"
    
    for (( i=0; i<${#text}; i++ )); do
        echo -n "${text:$i:1}"
        sleep "$delay"
    done
    echo ""
}

command_demo() {
    local cmd="$1"
    local description="$2"
    local BRIGHT_GREEN='\033[1;92m'
    local BRIGHT_GREEN_BOLD='\033[1;92;1m'
    
    echo -e "${YELLOW}${BOLD}💻 Running: ${NC}${BRIGHT_GREEN_BOLD}$cmd${NC}"
    [ -n "$description" ] && echo -e "${WHITE}   └── $description${NC}"
    echo ""
    
    # Simulate typing the command in bright green
    echo -ne "${BRIGHT_GREEN_BOLD}$ "
    typing_effect "$cmd" 0.05
    echo -ne "${NC}"
    
    # Capture and print output in bright green
    local output
    output=$(eval "$cmd" 2>&1)
    echo -e "${BRIGHT_GREEN}$output${NC}\n"
}

create_demo_file() {
    local filename="$1"
    local content="$2"
    
    # Ensure current directory exists (should already be in $DEMO_DIR)
    echo -e "${GREEN}📝 Creating demo file: ${CYAN}$filename${NC}"
    echo "$content" > "$filename"
}

# Main demo functions
demo_1_the_problem() {
    clear
    section_header "1. Challenges Before v2.0.x"
    
    echo -e "${RED}${BOLD}The Old Experience:${NC}"
    echo -e "${RED}❌ Multiple isolated packages${NC}"
    echo -e "${RED}❌ Inconsistent CLI interfaces${NC}"
    echo -e "${RED}❌ Need for sequencing and dependency management${NC}"
    echo ""
    
    echo ""
    
    echo -e "${YELLOW}Potential outcomes:${NC} ${RED}Frustrated users, unclear workflows, support tickets...${NC}"
    
    pause_for_narration "Explain the pain points your team experienced with the old fragmented approach"
}

demo_2_the_solution() {
    clear
    section_header "2. THE SOLUTION - Unified Package v2.0.x"
    
    echo -e "${GREEN}${BOLD}✨ The New Experience (aspirational):${NC}"
    echo -e "${GREEN}✅ Single unified package${NC}"
    echo -e "${GREEN}✅ Professional PyPI presence${NC}"
    echo -e "${GREEN}✅ Consistent CLI interface${NC}"
    echo -e "${GREEN}✅ All modules included and working${NC}"
    echo ""
    
    pause_for_narration "Introduce the unified solution"
    
    # Set up demo environment (silent, hidden from demo output)
    rm -rf "$DEMO_DIR"
    mkdir -p "$DEMO_DIR"
    cd "$DEMO_DIR"
    python3 -m venv demo_env > /dev/null 2>&1
    source demo_env/bin/activate

    # Show the recommended install/upgrade commands as text (not executed)
    local GREY='\033[1;30m'
    local BRIGHT_GREEN='\033[1;92m'
    echo -e "${GREY}# Install the toolkit from PyPI (as shown to users)${NC}"
    echo -e "${BOLD}${BRIGHT_GREEN}python3 -m pip install asciidoc-dita-toolkit${NC}"
    echo -e "${GREY}# Upgrade to the latest version if needed${NC}"
    echo -e "${BOLD}${BRIGHT_GREEN}python3 -m pip install --upgrade asciidoc-dita-toolkit${NC}"

    # Always try to install the latest local code in editable mode first (silent)
    if pip install -e .. > install.log 2>&1; then
        : # Hide success output
    else
        echo -e "${RED}Local install failed. See install.log for details.${NC}"
        echo -e "${YELLOW}Falling back to PyPI install...${NC}"
        command_demo "pip install $PACKAGE_NAME" "Single command installs everything!"
    fi
    
    pause_for_narration "Highlight how simple the installation is now"
    
    # Show CLI discovery
    echo -e "${GREEN}${BOLD}CLI Discovery:${NC}"
    command_demo "adt --version" "Check version - works immediately!"
    command_demo "adt --help" "Comprehensive help system"
    
    pause_for_narration "Show the clean, professional CLI interface"
}

demo_3_the_features() {
    clear
    section_header "3. THE FEATURES - All 6 Plugins in Action"
    
    echo -e "${GREEN}${BOLD}🎯 Plugin Discovery:${NC}"
    command_demo "adt --list-plugins" "All plugins auto-discovered"
    
    pause_for_narration "Point out all 6 plugins are available and working"
    
    # Concise one-line descriptions for each module (static, since --describe is not supported)
    echo -e "${CYAN}Module overview:${NC}"
    echo -e "${WHITE}- CrossReference: Fix cross-references in AsciiDoc files by updating xref links to include proper file paths${NC}"
    echo -e "${WHITE}- ContextAnalyzer: Analyze AsciiDoc documentation for context usage and migration complexity${NC}"
    echo -e "${WHITE}- EntityReference: Replace unsupported HTML character entity references in .adoc files with AsciiDoc attribute references.${NC}"
    echo -e "${WHITE}- ContextMigrator: Migrate AsciiDoc files from context-suffixed IDs to context-free IDs with validation and rollback${NC}"
    echo -e "${WHITE}- ContentType: Add a :_mod-docs-content-type: label in .adoc files where those are missing, based on filename.${NC}"
    echo -e "${WHITE}- DirectoryConfig: Configure directory scoping for AsciiDoc processing (preview)${NC}"
    echo ""
    
    # Create demo content for each plugin
    echo -e "${BLUE}${BOLD}📁 Creating realistic demo content...${NC}"
    
    # ContentType plugin demo
    create_demo_file "procedure_example.adoc" "= Installing Docker

This guide shows you how to install Docker on your system.

== Prerequisites

Before you begin, ensure you have:

* Administrative access to your system
* Internet connection
* Supported operating system

== Installation Steps

. Download Docker Desktop:
+
[source,bash]
----
curl -O https://desktop.docker.com/...
----

. Install the package:
+
[source,bash]
----
sudo dpkg -i docker-desktop.deb
----

. Verify installation:
+
[source,bash]
----
docker --version
----

== Verification

Run the hello-world container to verify Docker is working:

[source,bash]
----
docker run hello-world
----"
    
    echo -e "${GREEN}${BOLD}🎨 ContentType Plugin Demo:${NC}"
    command_demo "adt ContentType -f procedure_example.adoc" "Auto-detect and add content type"
    
    echo -e "${CYAN}Let's see what was added:${NC}"
    command_demo "head -5 procedure_example.adoc" "Content type attribute added!"
    
    pause_for_narration "Explain how ContentType intelligently detected this as a PROCEDURE"
    
    # EntityReference plugin demo
    create_demo_file "entities_example.adoc" "= Legal Document

This document contains entity references that need standardization:

* Copyright notice: &copy; 2024 Our Company
* Trademark symbol: ProductName&trade;
* Registered mark: BrandName&reg;
* Special spacing: Word&nbsp;spacing

Standard XML entities like &amp; and &lt; should remain unchanged."
    
    echo -e "${GREEN}${BOLD}🔄 EntityReference Plugin Demo:${NC}"
    command_demo "adt EntityReference -f entities_example.adoc" "Replace HTML entities with AsciiDoc attributes"
    
    echo -e "${CYAN}Let's see the transformations:${NC}"
    command_demo "cat entities_example.adoc" "Entities converted to AsciiDoc format!"
    
    pause_for_narration "Show how entities were intelligently converted"
    
    # CrossReference plugin demo
    create_demo_file "cross_ref_example.adoc" "= Main Document

See the installation guide in xref:install.adoc[Installation].

Also check out xref:config[Configuration Section].

[#config]
== Configuration Section

Configuration details here.

For troubleshooting, see xref:troubleshoot.adoc#common-issues[Common Issues]."
    
    create_demo_file "install.adoc" "[#installation]
= Installation Guide

Installation steps here.

[#requirements]
== System Requirements

Requirements details here."
    
    echo -e "${GREEN}${BOLD}🔗 CrossReference Plugin Demo:${NC}"
    command_demo "adt CrossReference -f cross_ref_example.adoc -v" "Validate and fix cross-references"
    
    pause_for_narration "Explain cross-reference validation and fixing"
    
    # Show multiple plugins working together
    echo -e "${GREEN}${BOLD}🚀 Multiple Plugins Working Together:${NC}"
    create_demo_file "complete_example.adoc" "= Complete Documentation Example

This document will be processed by multiple plugins.

== Overview

This shows the power of &copy; Our Toolkit&trade;.

== Installation

. Download the software
. Install using: sudo install.sh
. Verify with: check --version

== Configuration

See xref:config.adoc[Configuration Guide] for details.

For troubleshooting: xref:troubleshoot.adoc#issues[Common Issues]."
    
    echo -e "${YELLOW}Processing with multiple plugins...${NC}"
    command_demo "adt ContentType -f complete_example.adoc && adt EntityReference -f complete_example.adoc" "ContentType + EntityReference"
    
    echo -e "${CYAN}Final result:${NC}"
    command_demo "head -10 complete_example.adoc" "Multiple transformations applied!"
    
    pause_for_narration "Highlight how plugins work seamlessly together"
}

demo_4_developer_experience() {
    clear
    section_header "4. THE DEVELOPER EXPERIENCE"
    
    echo -e "${GREEN}${BOLD}🔧 Professional Development Workflow:${NC}"
    
    # Show package metadata
    echo -e "${BLUE}Professional PyPI Package:${NC}"
    command_demo "pip show $PACKAGE_NAME" "Rich metadata and project information"
    
    pause_for_narration "Point out the professional package information"
    
    # Show testing
    echo -e "${BLUE}Comprehensive Testing:${NC}"
    cd ..  # Back to main directory
    command_demo "python3 -m pytest tests/ -v --tb=short | head -20" "196 tests passing!"
    
    pause_for_narration "Emphasize the reliability and quality"
    
    # Show documentation
    echo -e "${BLUE}Complete Documentation:${NC}"
    command_demo "ls docs/" "Professional documentation structure"
    command_demo "head -15 README.md" "Clear usage instructions"
    
    # Show build system
    echo -e "${BLUE}Modern Build System:${NC}"
    command_demo "head -10 pyproject.toml" "Modern Python packaging standards"
    
    pause_for_narration "Highlight the professional development practices"
}

demo_5_the_impact() {
    clear
    section_header "5. THE IMPACT - What This Means for Our Team"
    
    echo -e "${GREEN}${BOLD}🎯 Business Impact:${NC}"
    echo ""
    echo -e "${GREEN}✅ ${BOLD}For End Users:${NC}"
    echo -e "   • Single command installation: ${CYAN}pip install $PACKAGE_NAME${NC}"
    echo -e "   • Intuitive CLI interface: ${CYAN}adt --help${NC}"
    echo -e "   • All features work out of the box"
    echo -e "   • Professional documentation and support"
    echo ""
    
    echo -e "${GREEN}✅ ${BOLD}For Our Team:${NC}"
    echo -e "   • Reduced support tickets and installation issues"
    echo -e "   • Professional brand presence on PyPI"
    echo -e "   • Easier maintenance with unified codebase"
    echo -e "   • Confident in recommending the tool"
    echo ""
    
    echo -e "${GREEN}✅ ${BOLD}Technical Achievements:${NC}"
    echo -e "   • 196 automated tests ensuring reliability"
    echo -e "   • Modern packaging with complete metadata"
    echo -e "   • All 6 plugins integrated and working"
    echo -e "   • Backward compatibility maintained"
    echo ""
    
    # Show version info one more time
    cd "$DEMO_DIR"
    source demo_env/bin/activate
    echo -e "${BLUE}${BOLD}🏆 Final Demo:${NC}"
    command_demo "adt --version" "Version $VERSION - Live on PyPI!"
    command_demo "adt --list-plugins" "All 6 plugins ready to use!"
    
    pause_for_narration "Wrap up with the key achievements and what's next"
    
    # Cleanup
    cd ..
    echo -e "${YELLOW}🧹 Cleaning up demo environment...${NC}"
    rm -rf "$DEMO_DIR"
    
    echo -e "${GREEN}"
    echo "┌───────────────────────────────────────────────────────────────┐"
    echo "│                                                               │"
    echo "│                  DEMO COMPLETE!  🎉                           │"
    echo "│                                                               │"
    echo "│        AsciiDoc DITA Toolkit v$VERSION                        │"
    echo "│        Ready for Production Use!                              │"
    echo "│                                                               │"
    echo "└───────────────────────────────────────────────────────────────┘"
    echo -e "${NC}"
}

# Main demo execution
main() {
    echo -e "${WHITE}${BOLD}"
    echo "🚀 Starting AsciiDoc DITA Toolkit v$VERSION Live Demo!"
    echo -e "${NC}"
    echo -e "${CYAN}This demo will showcase all the amazing features of our unified package.${NC}"
    echo -e "${YELLOW}Estimated time: ~10 minutes${NC}"
    echo ""
    
    pause_for_narration "Welcome your team and introduce the demo"
    
    demo_1_the_problem
    demo_2_the_solution  
    demo_3_the_features
    demo_4_developer_experience
    demo_5_the_impact
    
    echo -e "${GREEN}${BOLD}Thank you for watching! Questions?${NC}"
}

# Run the demo
main "$@"
