#!/bin/bash

# AsciiDoc DITA Toolkit v2.0.x Demo Setup Script
# This script sets up the complete demo environment for showcasing all features

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Unicode symbols
ROCKET="🚀"
FIRE="🔥"
LIGHTNING="⚡"
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
INFO="ℹ️"
GEAR="⚙️"
DOCUMENT="📄"
FOLDER="📁"

# Function to print colored output
print_colored() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print section headers
print_header() {
    local title=$1
    local emoji=$2
    echo
    print_colored $CYAN "╔═══════════════════════════════════════════════════════════════════════════════╗"
    print_colored $CYAN "║                                                                               ║"
    print_colored $CYAN "║  ${WHITE}${emoji} ${title}${NC}${CYAN}                                                                   ║"
    print_colored $CYAN "║                                                                               ║"
    print_colored $CYAN "╚═══════════════════════════════════════════════════════════════════════════════╝"
    echo
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        local major=$(echo $python_version | cut -d. -f1)
        local minor=$(echo $python_version | cut -d. -f2)
        
        if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

# Function to install dependencies
install_dependencies() {
    print_colored $BLUE "Installing required dependencies..."
    
    # Check if in virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        print_colored $GREEN "${CHECK} Virtual environment detected: $VIRTUAL_ENV"
    else
        print_colored $YELLOW "${WARNING} Consider using a virtual environment"
        read -p "$(echo -e ${YELLOW}Would you like to create one? [y/N]: ${NC})" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 -m venv adt-demo-env
            source adt-demo-env/bin/activate
            print_colored $GREEN "${CHECK} Virtual environment created and activated"
        fi
    fi
    
    # Install the toolkit
    print_colored $BLUE "Installing AsciiDoc DITA Toolkit..."
    pip install asciidoc-dita-toolkit
    
    # Install optional dependencies for better demo experience
    print_colored $BLUE "Installing optional dependencies..."
    pip install markdown 2>/dev/null || echo "Markdown not available (optional)"
    
    print_colored $GREEN "${CHECK} Dependencies installed successfully"
}

# Function to verify installation
verify_installation() {
    print_colored $BLUE "Verifying installation..."
    
    if command_exists adt; then
        local version=$(adt --version 2>/dev/null || echo "Unknown")
        print_colored $GREEN "${CHECK} ADT command available: $version"
    else
        print_colored $RED "${CROSS} ADT command not found in PATH"
        return 1
    fi
    
    # List available plugins
    print_colored $BLUE "Available plugins:"
    adt --list-plugins 2>/dev/null || echo "Could not list plugins"
    
    return 0
}

# Function to setup demo files
setup_demo_files() {
    print_colored $BLUE "Setting up demo files..."
    
    local demo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local sample_dir="$demo_dir/sample_files"
    local output_dir="$demo_dir/output"
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Copy sample files to output directory
    if [ -d "$sample_dir" ]; then
        cp "$sample_dir"/*.adoc "$output_dir/" 2>/dev/null || true
        print_colored $GREEN "${CHECK} Sample files copied to output directory"
    else
        print_colored $YELLOW "${WARNING} Sample files directory not found"
    fi
    
    # Create backup directory
    mkdir -p "$output_dir/backup"
    
    print_colored $GREEN "${CHECK} Demo files setup complete"
}

# Function to test plugins
test_plugins() {
    print_colored $BLUE "Testing plugins with sample files..."
    
    local demo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local output_dir="$demo_dir/output"
    
    if [ ! -d "$output_dir" ]; then
        print_colored $RED "${CROSS} Output directory not found"
        return 1
    fi
    
    cd "$output_dir"
    
    # Test EntityReference plugin
    print_colored $BLUE "Testing EntityReference plugin..."
    if adt EntityReference -f entity_examples.adoc 2>/dev/null; then
        print_colored $GREEN "${CHECK} EntityReference plugin working"
    else
        print_colored $YELLOW "${WARNING} EntityReference plugin test failed"
    fi
    
    # Test ContentType plugin
    print_colored $BLUE "Testing ContentType plugin..."
    if adt ContentType -f content_type_examples.adoc --batch 2>/dev/null; then
        print_colored $GREEN "${CHECK} ContentType plugin working"
    else
        print_colored $YELLOW "${WARNING} ContentType plugin test failed"
    fi
    
    cd - >/dev/null
    
    print_colored $GREEN "${CHECK} Plugin testing complete"
}

# Function to setup web server
setup_web_server() {
    print_colored $BLUE "Setting up web server for interactive demo..."
    
    local demo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local port=8000
    
    # Check if port is available
    if command_exists lsof && lsof -i :$port >/dev/null 2>&1; then
        print_colored $YELLOW "${WARNING} Port $port is already in use"
        port=8001
    fi
    
    print_colored $GREEN "${CHECK} Web server will be available at: http://localhost:$port"
    print_colored $CYAN "To start the web server, run:"
    print_colored $WHITE "  cd $demo_dir && python3 -m http.server $port"
    
    # Create a convenience script
    cat > "$demo_dir/start_web_demo.sh" << EOF
#!/bin/bash
cd "$(dirname "\$0")"
echo "Starting web demo server..."
echo "Open http://localhost:$port/web_demo.html in your browser"
echo "Press Ctrl+C to stop"
python3 -m http.server $port
EOF
    
    chmod +x "$demo_dir/start_web_demo.sh"
    print_colored $GREEN "${CHECK} Web server setup complete"
}

# Function to create demo launcher script
create_launcher() {
    print_colored $BLUE "Creating demo launcher script..."
    
    local demo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    cat > "$demo_dir/run_demo.sh" << 'EOF'
#!/bin/bash

# AsciiDoc DITA Toolkit v2.0.x Demo Launcher

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

print_colored() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

demo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_colored $CYAN "╔═══════════════════════════════════════════════════════════════════════════════╗"
print_colored $CYAN "║                                                                               ║"
print_colored $CYAN "║  ${WHITE}🚀 AsciiDoc DITA Toolkit v2.0.x Demo Launcher${NC}${CYAN}                              ║"
print_colored $CYAN "║                                                                               ║"
print_colored $CYAN "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo

print_colored $WHITE "Choose your demo experience:"
echo
print_colored $YELLOW "1) Enhanced Live Demo (Terminal)"
print_colored $YELLOW "2) Web Demo (Browser)"
print_colored $YELLOW "3) Static Presentation (Markdown)"
print_colored $YELLOW "4) Run Plugin Tests"
print_colored $YELLOW "5) View Sample Files"
print_colored $YELLOW "6) Exit"
echo

read -p "$(echo -e ${CYAN}Enter your choice [1-6]: ${NC})" choice

case $choice in
    1)
        print_colored $GREEN "🎬 Starting Enhanced Live Demo..."
        python3 "$demo_dir/enhanced_demo.py"
        ;;
    2)
        print_colored $GREEN "🌐 Starting Web Demo..."
        if [ -f "$demo_dir/start_web_demo.sh" ]; then
            "$demo_dir/start_web_demo.sh"
        else
            print_colored $BLUE "Starting web server..."
            cd "$demo_dir"
            python3 -m http.server 8000
        fi
        ;;
    3)
        print_colored $GREEN "📋 Displaying Static Presentation..."
        if command -v less >/dev/null 2>&1; then
            less "$demo_dir/presentation.md"
        else
            cat "$demo_dir/presentation.md"
        fi
        ;;
    4)
        print_colored $GREEN "🔧 Running Plugin Tests..."
        cd "$demo_dir/output"
        echo "Testing EntityReference plugin..."
        adt EntityReference -f entity_examples.adoc
        echo "Testing ContentType plugin..."
        adt ContentType -f content_type_examples.adoc --batch
        cd - >/dev/null
        ;;
    5)
        print_colored $GREEN "📄 Sample Files:"
        ls -la "$demo_dir/sample_files/"
        echo
        print_colored $CYAN "To view a sample file:"
        print_colored $WHITE "  cat $demo_dir/sample_files/entity_examples.adoc"
        ;;
    6)
        print_colored $GREEN "👋 Thank you for exploring AsciiDoc DITA Toolkit v2.0.x!"
        exit 0
        ;;
    *)
        print_colored $RED "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
EOF
    
    chmod +x "$demo_dir/run_demo.sh"
    print_colored $GREEN "${CHECK} Demo launcher created"
}

# Function to generate summary report
generate_summary() {
    print_colored $BLUE "Generating setup summary..."
    
    local demo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    cat > "$demo_dir/DEMO_SUMMARY.md" << EOF
# AsciiDoc DITA Toolkit v2.0.x Demo Setup Summary

## 🎯 Demo Components Ready

### 1. Enhanced Live Demo
- **File**: \`enhanced_demo.py\`
- **Usage**: \`python3 enhanced_demo.py\`
- **Features**: Colorful terminal output, progress bars, interactive demonstrations

### 2. Web Demo
- **File**: \`web_demo.html\`
- **Usage**: \`./start_web_demo.sh\` or \`python3 -m http.server 8000\`
- **Features**: Interactive browser-based demo with live examples

### 3. Static Presentation
- **File**: \`presentation.md\`
- **Usage**: \`cat presentation.md\` or convert to HTML
- **Features**: Comprehensive markdown presentation with all features

### 4. Sample Files
- **Directory**: \`sample_files/\`
- **Files**:
  - \`entity_examples.adoc\` - EntityReference plugin demonstration
  - \`content_type_examples.adoc\` - ContentType plugin demonstration
  - \`proc-install-toolkit.adoc\` - Procedure document example
  - \`complex_document.adoc\` - Multi-plugin integration example

## 🚀 Quick Start Commands

### Run Interactive Demo
\`\`\`bash
./run_demo.sh
\`\`\`

### Manual Plugin Testing
\`\`\`bash
cd output/
adt EntityReference -f entity_examples.adoc
adt ContentType -f content_type_examples.adoc --batch
adt CrossReference -f complex_document.adoc
\`\`\`

### Web Demo
\`\`\`bash
./start_web_demo.sh
# Then open http://localhost:8000/web_demo.html
\`\`\`

## 📊 System Information

- **Python Version**: $(python3 --version 2>/dev/null || echo "Not available")
- **ADT Version**: $(adt --version 2>/dev/null || echo "Not available")
- **Demo Directory**: $demo_dir
- **Setup Date**: $(date)

## 🎨 Demo Features Showcased

- ✅ Unified Package Installation
- ✅ Simple CLI Interface
- ✅ Six Powerful Plugins
- ✅ Real-time Processing
- ✅ Performance Metrics
- ✅ Container Support
- ✅ Enterprise Integration Examples

## 🤝 Support

Need help with the demo?
- 📖 Check the main README.md
- 🐛 Report issues on GitHub
- 💬 Join the discussions

---

**Ready to impress your team?** 🚀

Choose your demo style and showcase the power of v2.0.x!
EOF
    
    print_colored $GREEN "${CHECK} Setup summary generated: DEMO_SUMMARY.md"
}

# Main setup function
main() {
    print_header "AsciiDoc DITA Toolkit v2.0.x Demo Setup" "$ROCKET"
    
    print_colored $WHITE "Welcome to the comprehensive demo setup!"
    print_colored $CYAN "This script will prepare everything you need for your v2.0.x demonstration."
    echo
    
    # Check prerequisites
    print_colored $BLUE "Checking prerequisites..."
    
    if ! check_python_version; then
        print_colored $RED "${CROSS} Python 3.8+ is required"
        print_colored $YELLOW "Please install Python 3.8+ and run this script again"
        exit 1
    fi
    
    print_colored $GREEN "${CHECK} Python version compatible"
    
    # Check if toolkit is already installed
    if command_exists adt; then
        print_colored $GREEN "${CHECK} AsciiDoc DITA Toolkit already installed"
        local version=$(adt --version 2>/dev/null || echo "Unknown")
        print_colored $CYAN "Current version: $version"
        
        read -p "$(echo -e ${YELLOW}Would you like to upgrade? [y/N]: ${NC})" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pip install --upgrade asciidoc-dita-toolkit
        fi
    else
        # Install dependencies
        install_dependencies
    fi
    
    # Verify installation
    if ! verify_installation; then
        print_colored $RED "${CROSS} Installation verification failed"
        exit 1
    fi
    
    # Setup demo environment
    setup_demo_files
    
    # Test plugins
    test_plugins
    
    # Setup web server
    setup_web_server
    
    # Create launcher script
    create_launcher
    
    # Generate summary
    generate_summary
    
    # Final success message
    print_header "Demo Setup Complete!" "$CHECK"
    
    print_colored $GREEN "🎉 Your AsciiDoc DITA Toolkit v2.0.x demo is ready!"
    echo
    print_colored $WHITE "🚀 Quick Start Options:"
    echo
    print_colored $CYAN "  1. Run Interactive Demo:"
    print_colored $WHITE "     ./run_demo.sh"
    echo
    print_colored $CYAN "  2. Start Web Demo:"
    print_colored $WHITE "     ./start_web_demo.sh"
    echo
    print_colored $CYAN "  3. View Static Presentation:"
    print_colored $WHITE "     cat presentation.md"
    echo
    print_colored $CYAN "  4. Test Plugins Manually:"
    print_colored $WHITE "     cd output/ && adt EntityReference -f entity_examples.adoc"
    echo
    print_colored $YELLOW "📄 For detailed information, see: DEMO_SUMMARY.md"
    echo
    print_colored $MAGENTA "Ready to impress your team? 🌟"
}

# Run main function
main "$@"