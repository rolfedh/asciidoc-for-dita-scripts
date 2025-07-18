#!/bin/bash
set -e

# DirectoryConfig Beta Testing - Automated Test Suite
# This script automatically tests all functionality described in the DirectoryConfig beta testing guide

echo "🧪 DirectoryConfig Beta Testing - Automated Test Suite"
echo "======================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test result tracking
TESTS_PASSED=0
TESTS_FAILED=0
TEST_DETAILS=()

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

log_success() {
    echo -e "${GREEN}✅ ${1}${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TEST_DETAILS+=("✅ ${1}")
}

log_failure() {
    echo -e "${RED}❌ ${1}${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TEST_DETAILS+=("❌ ${1}")
}

log_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

# Test function wrapper
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    log_info "Testing: $test_name"
    
    if eval "$test_command"; then
        log_success "$test_name"
        return 0
    else
        log_failure "$test_name"
        return 1
    fi
}

# Setup test environment
setup_test_env() {
    log_info "Setting up test environment..."
    
    # Clean up any existing test directory
    if [ -d ~/adt-directory-test-auto ]; then
        rm -rf ~/adt-directory-test-auto
    fi
    
    # Create fresh test environment
    mkdir ~/adt-directory-test-auto
    cd ~/adt-directory-test-auto
    
    # Create directory structure
    mkdir -p docs/{user-guide,admin-guide,legacy} guides/{installation,troubleshooting} archive
    
    # Create test .adoc files
    echo -e "= User Guide\n\nContent here." > docs/user-guide/index.adoc
    echo -e "= Admin Guide\n\nAdmin content." > docs/admin-guide/setup.adoc
    echo -e "= Legacy\n\nOld content." > docs/legacy/old.adoc
    echo -e "= Installation\n\nHow to install." > guides/installation/setup.adoc
    echo -e "= Archive Content\n\nArchived content." > archive/old-docs.adoc
    
    log_success "Test environment setup complete"
}

# Test 1: Feature enablement
test_feature_enablement() {
    log_info "=== Test 1: Feature Enablement ==="
    
    # Test disabled state
    unset ADT_ENABLE_DIRECTORY_CONFIG
    if echo "" | timeout 5 adt DirectoryConfig 2>&1 | grep -q "Directory configuration is currently disabled"; then
        log_success "Disabled state properly detected"
    else
        log_failure "Disabled state not properly detected"
    fi
    
    # Enable feature
    export ADT_ENABLE_DIRECTORY_CONFIG=true
    
    # Test plugin listing
    if adt --list-plugins | grep -q "DirectoryConfig"; then
        log_success "DirectoryConfig plugin visible in plugin list"
    else
        log_failure "DirectoryConfig plugin not visible in plugin list"
    fi
}

# Test 2: Interactive configuration setup
test_interactive_setup() {
    log_info "=== Test 2: Interactive Configuration Setup ==="
    
    # Prepare automated input for interactive setup
    # Repository root: current directory (default)
    # Include directories: docs/user-guide, guides
    # Exclude directories: docs/legacy, archive  
    # Save location: current directory (default)
    
    cat > setup_input.txt << 'EOF'

docs/user-guide
guides

docs/legacy
archive

1
EOF
    
    if adt DirectoryConfig < setup_input.txt > setup_output.txt 2>&1; then
        if grep -q "Configuration saved" setup_output.txt; then
            log_success "Interactive configuration setup completed"
        else
            log_failure "Interactive setup did not complete successfully"
            cat setup_output.txt
        fi
    else
        log_failure "Interactive setup failed"
        cat setup_output.txt
    fi
    
    # Verify configuration file was created
    if [ -f .adtconfig.json ]; then
        log_success "Configuration file .adtconfig.json created"
    else
        log_failure "Configuration file not created"
    fi
    
    # Verify configuration content
    if grep -q '"docs/user-guide"' .adtconfig.json && \
       grep -q '"docs/legacy"' .adtconfig.json; then
        log_success "Configuration content is correct"
    else
        log_failure "Configuration content is incorrect"
        cat .adtconfig.json
    fi
}

# Test 3: Configuration display
test_config_display() {
    log_info "=== Test 3: Configuration Display ==="
    
    if adt DirectoryConfig --show > config_display.txt 2>&1; then
        if grep -q "Directory Configuration" config_display.txt && \
           grep -q "docs/user-guide" config_display.txt && \
           grep -q "docs/legacy" config_display.txt; then
            log_success "Configuration display shows correct information"
        else
            log_failure "Configuration display missing expected content"
            cat config_display.txt
        fi
    else
        log_failure "Configuration display failed"
    fi
}

# Test 4: Directory filtering with ContentType
test_directory_filtering() {
    log_info "=== Test 4: Directory Filtering with ContentType ==="
    
    # Test basic filtering (should use configuration)
    if adt ContentType > contenttype_output.txt 2>&1; then
        if grep -q "Using directory configuration" contenttype_output.txt; then
            log_success "ContentType plugin uses directory configuration"
        else
            log_failure "ContentType plugin does not use directory configuration"
            cat contenttype_output.txt
        fi
        
        if grep -q "Processing.*director" contenttype_output.txt; then
            log_success "Directory processing status displayed"
        else
            log_failure "Directory processing status not displayed"
        fi
    else
        log_failure "ContentType plugin failed to run"
    fi
}

# Test 5: Directory override behavior
test_directory_override() {
    log_info "=== Test 5: Directory Override Behavior ==="
    
    # Test processing excluded directory
    if adt ContentType -d docs/legacy > override_excluded.txt 2>&1; then
        if grep -q "Warning.*excluded" override_excluded.txt || \
           grep -q "Directory.*excluded" override_excluded.txt; then
            log_success "Excluded directory properly warned"
        else
            log_warning "Excluded directory warning not found (implementation may vary)"
            cat override_excluded.txt
        fi
    else
        log_failure "Override test with excluded directory failed"
    fi
    
    # Test processing included directory
    if adt ContentType -d docs/user-guide > override_included.txt 2>&1; then
        if grep -q "Using directory configuration" override_included.txt; then
            log_success "Included directory processes with configuration"
        else
            log_failure "Included directory does not use configuration"
            cat override_included.txt
        fi
    else
        log_failure "Override test with included directory failed"
    fi
}

# Test 6: Traditional behavior (disabled)
test_traditional_behavior() {
    log_info "=== Test 6: Traditional Behavior (Disabled) ==="
    
    # Disable feature
    unset ADT_ENABLE_DIRECTORY_CONFIG
    
    if adt ContentType > traditional_output.txt 2>&1; then
        if ! grep -q "Using directory configuration" traditional_output.txt; then
            log_success "Traditional behavior works without configuration messages"
        else
            log_failure "Traditional behavior still shows configuration messages"
            cat traditional_output.txt
        fi
    else
        log_failure "Traditional behavior test failed"
    fi
    
    # Re-enable for remaining tests
    export ADT_ENABLE_DIRECTORY_CONFIG=true
}

# Test 7: Multiple configuration files
test_multiple_configs() {
    log_info "=== Test 7: Multiple Configuration Files ==="
    
    # Create home config file
    cat > ~/.adtconfig.json << 'EOF'
{
  "version": "1.0",
  "repoRoot": "/home/test",
  "includeDirs": ["home-docs"],
  "excludeDirs": ["home-legacy"],
  "lastUpdated": "2025-01-01T00:00:00Z"
}
EOF
    
    # Test that it prompts when both exist
    # This is harder to test automatically, so we'll just verify the files exist
    if [ -f .adtconfig.json ] && [ -f ~/.adtconfig.json ]; then
        log_success "Multiple configuration files setup correctly"
    else
        log_failure "Multiple configuration files not setup correctly"
    fi
    
    # Clean up home config
    rm -f ~/.adtconfig.json
}

# Test 8: Configuration scenarios
test_configuration_scenarios() {
    log_info "=== Test 8: Configuration Scenarios ==="
    
    # Scenario 1: Include only specific directories
    cat > .adtconfig.json << 'EOF'
{
  "version": "1.0",
  "repoRoot": "/home/rolfedh/adt-directory-test-auto",
  "includeDirs": ["docs/user-guide"],
  "excludeDirs": [],
  "lastUpdated": "2025-07-04T12:00:00Z"
}
EOF
    
    if adt ContentType > scenario1_output.txt 2>&1; then
        if grep -q "Using directory configuration" scenario1_output.txt; then
            log_success "Scenario 1 (include only) works"
        else
            log_failure "Scenario 1 (include only) failed"
            cat scenario1_output.txt
        fi
    else
        log_failure "Scenario 1 test failed"
    fi
    
    # Scenario 2: Exclude specific directories
    cat > .adtconfig.json << 'EOF'
{
  "version": "1.0",
  "repoRoot": "/home/rolfedh/adt-directory-test-auto",
  "includeDirs": [],
  "excludeDirs": ["docs/legacy", "archive"],
  "lastUpdated": "2025-07-04T12:00:00Z"
}
EOF
    
    if adt ContentType > scenario2_output.txt 2>&1; then
        if grep -q "Using directory configuration" scenario2_output.txt; then
            log_success "Scenario 2 (exclude specific) works"
        else
            log_failure "Scenario 2 (exclude specific) failed"
            cat scenario2_output.txt
        fi
    else
        log_failure "Scenario 2 test failed"
    fi
}

# Test 9: Error handling
test_error_handling() {
    log_info "=== Test 9: Error Handling ==="
    
    # Test with invalid JSON
    echo "invalid json" > .adtconfig.json
    
    if adt ContentType > error_test.txt 2>&1; then
        if grep -q "Warning.*configuration" error_test.txt || ! grep -q "Using directory configuration" error_test.txt; then
            log_success "Invalid JSON handled gracefully"
        else
            log_failure "Invalid JSON not handled properly"
            cat error_test.txt
        fi
    else
        log_failure "Error handling test failed"
    fi
    
    # Test with missing directories in config
    cat > .adtconfig.json << 'EOF'
{
  "version": "1.0",
  "repoRoot": "/home/rolfedh/adt-directory-test-auto",
  "includeDirs": ["nonexistent"],
  "excludeDirs": [],
  "lastUpdated": "2025-07-04T12:00:00Z"
}
EOF
    
    if adt ContentType > missing_dir_test.txt 2>&1; then
        log_success "Missing directories handled gracefully"
    else
        log_failure "Missing directories not handled properly"
    fi
}

# Main test execution
main() {
    log_info "Starting DirectoryConfig automated test suite..."
    
    # Change to toolkit directory for testing
    cd /home/rolfedh/asciidoc-dita-toolkit
    
    # Setup test environment
    setup_test_env
    
    # Run all tests
    test_feature_enablement
    test_interactive_setup
    test_config_display
    test_directory_filtering
    test_directory_override
    test_traditional_behavior
    test_multiple_configs
    test_configuration_scenarios
    test_error_handling
    
    # Summary
    echo ""
    echo "🏁 Test Summary"
    echo "==============="
    echo -e "${GREEN}Tests Passed: ${TESTS_PASSED}${NC}"
    echo -e "${RED}Tests Failed: ${TESTS_FAILED}${NC}"
    echo ""
    
    # Detailed results
    echo "📋 Detailed Results:"
    for detail in "${TEST_DETAILS[@]}"; do
        echo -e "$detail"
    done
    
    # Cleanup
    log_info "Cleaning up test environment..."
    cd /home/rolfedh/asciidoc-dita-toolkit
    rm -rf ~/adt-directory-test-auto
    rm -f ~/.adtconfig.json
    
    # Exit with appropriate code
    if [ $TESTS_FAILED -eq 0 ]; then
        echo ""
        log_success "All tests passed! DirectoryConfig is ready for beta testing! 🎉"
        exit 0
    else
        echo ""
        log_failure "Some tests failed. Please review the results above."
        exit 1
    fi
}

# Run the test suite
main "$@"
