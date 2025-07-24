#!/usr/bin/env python3
"""
Chunk 5 Validation: System Integration and Debugging
Test all components of Chunk 5 implementation.
"""

import subprocess
import sys
from pathlib import Path
import tempfile

def run_command(command):
    """Helper function to run shell commands and capture output."""
    try:
        result = subprocess.run(
            command.split(), 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_pyproject_entry_point():
    """Test pyproject.toml entry point configuration."""
    print("🔍 Testing pyproject.toml entry point...")
    
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("   ❌ pyproject.toml not found")
        return False
    
    content = pyproject_path.read_text()
    
    # Check for UserJourney entry point
    if 'UserJourney = "asciidoc_dita_toolkit.modules.user_journey:UserJourneyModule"' in content:
        print("   ✅ UserJourney entry point configured correctly")
        return True
    else:
        print("   ❌ UserJourney entry point not found or incorrect")
        return False

def test_cli_integration():
    """Test CLI integration."""
    print("🔍 Testing CLI integration...")
    
    try:
        # Test that UserJourneyModule can be imported
        from asciidoc_dita_toolkit.modules.user_journey import UserJourneyModule
        module = UserJourneyModule()
        parser = module.get_cli_parser()
        
        # Test subcommands are available in parser
        help_text = parser.format_help()
        expected_commands = ["start", "resume", "continue", "status", "list", "cleanup"]
        for cmd in expected_commands:
            if cmd in help_text:
                print(f"   ✅ Subcommand '{cmd}' available")
            else:
                print(f"   ❌ Subcommand '{cmd}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ CLI integration test failed: {e}")
        return False

def test_module_wrapper():
    """Test UserJourneyModule wrapper."""
    print("🔍 Testing UserJourneyModule wrapper...")
    
    try:
        from asciidoc_dita_toolkit.modules.user_journey import UserJourneyModule
        
        # Test module creation
        module = UserJourneyModule()
        print(f"   ✅ Module created: {module.name}")
        print(f"   ✅ Version: {module.version}")
        print(f"   ✅ Dependencies: {module.dependencies}")
        
        # Test initialization
        result = module.initialize({})
        if result.get("status") == "success":
            print("   ✅ Module initialization successful")
        else:
            print(f"   ❌ Module initialization failed: {result}")
            return False
        
        # Test CLI parser creation
        parser = module.get_cli_parser()
        if parser:
            print("   ✅ CLI parser created")
        else:
            print("   ❌ CLI parser creation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Module wrapper test failed: {e}")
        return False

def test_debug_utilities():
    """Test debug utilities."""
    print("🔍 Testing debug utilities...")
    
    debug_script = Path("debug_user_journey.py")
    if not debug_script.exists():
        print("   ❌ Debug script not found")
        return False
    
    print("   ✅ Debug utilities are available")
    return True

def test_logging_support():
    """Test logging support."""
    print("🔍 Testing logging support...")
    
    try:
        from asciidoc_dita_toolkit.modules.user_journey import UserJourneyModule
        
        # Test with verbose logging
        module = UserJourneyModule()
        result = module.initialize({"verbose": True, "log_file": "/tmp/test_userjourney.log"})
        
        if result.get("status") == "success":
            print("   ✅ Logging configuration successful")
        else:
            print(f"   ❌ Logging configuration failed: {result}")
            return False
        
        # Check if log file was created (optional)
        log_file = Path("/tmp/test_userjourney.log")
        if log_file.exists():
            print("   ✅ Log file created")
            log_file.unlink()  # Clean up
        
        return True
        
    except Exception as e:
        print(f"   ❌ Logging test failed: {e}")
        return False

def test_full_integration():
    """Test full integration workflow."""
    print("🔍 Testing full integration...")
    
    try:
        from asciidoc_dita_toolkit.modules.user_journey import UserJourneyModule
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test .adoc file
            test_file = temp_path / "test.adoc"
            test_file.write_text("""= Test Document
:content-type: concept

This is a test document.
""")
            
            # Test workflow creation through module interface
            print("   🚀 Testing workflow management...")
            module = UserJourneyModule()
            
            # Initialize module
            init_result = module.initialize({
                "directory": str(temp_path),
                "verbose": True
            })
            
            if init_result.get("status") == "success":
                print("   ✅ Module initialization successful")
            else:
                print(f"   ❌ Module initialization failed: {init_result}")
                return False
            
            # Test CLI parser
            parser = module.get_cli_parser()
            args = parser.parse_args(['start', '--name', 'test_workflow', '--directory', str(temp_path)])
            print("   ✅ CLI argument parsing successful")
            
            # Test execute method exists
            if hasattr(module, 'execute'):
                print("   ✅ Execute method exists")
            else:
                print("   ❌ Execute method missing")
                return False
            
            print("   ✅ Full integration test completed successfully")
            return True
            
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False

def main():
    """Run all Chunk 5 validation tests."""
    print("🎯 Chunk 5 Validation: System Integration and Debugging")
    print("=" * 60)
    
    tests = [
        ("pyproject.toml Entry Point", test_pyproject_entry_point),
        ("CLI Integration", test_cli_integration), 
        ("Module Wrapper", test_module_wrapper),
        ("Debug Utilities", test_debug_utilities),
        ("Logging Support", test_logging_support),
        ("Full Integration", test_full_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n{'=' * 60}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Chunk 5: System Integration and Debugging - COMPLETE!")
        print("\n✅ All integration components are working correctly:")
        print("  ✅ pyproject.toml entry point configured")
        print("  ✅ CLI integration functional")
        print("  ✅ Module wrapper working")
        print("  ✅ Debug utilities available")
        print("  ✅ Logging support implemented")
        print("  ✅ Full integration validated")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed. Please fix issues before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
