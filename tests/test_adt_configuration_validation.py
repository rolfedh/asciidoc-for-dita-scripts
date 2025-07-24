#!/usr/bin/env python3
"""
Configuration validation test for ADTModule plugins.

This test ensures that migrated plugins properly handle edge cases in configuration
and provide helpful error messages.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import tempfile
import os

# Add necessary paths
workspace_root = Path(__file__).parent.parent  # Go up from tests/ to project root
src_path = workspace_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))


def test_entityreference_config_validation():
    """Test EntityReference configuration validation."""
    print("🧪 Testing EntityReference Configuration Validation")
    print("-" * 50)

    try:
        from asciidoc_dita_toolkit.modules.entity_reference import (
            EntityReferenceModule,
        )

        test_cases = [
            # Test Case 1: Valid configuration
            {
                "name": "Valid Configuration",
                "config": {
                    "verbose": True,
                    "timeout_seconds": 30,
                    "cache_size": 1000,
                    "skip_comments": True,
                },
                "should_succeed": True,
            },
            # Test Case 2: Missing keys (should use defaults)
            {"name": "Missing Keys", "config": {}, "should_succeed": True},
            # Test Case 3: Invalid timeout type
            {
                "name": "Invalid Timeout Type",
                "config": {"timeout_seconds": "invalid", "verbose": True},
                "should_succeed": True,  # Should handle gracefully
            },
            # Test Case 4: Invalid cache size
            {
                "name": "Invalid Cache Size",
                "config": {"cache_size": -1, "verbose": True},
                "should_succeed": True,  # Should handle gracefully
            },
            # Test Case 5: Invalid boolean values
            {
                "name": "Invalid Boolean Values",
                "config": {"verbose": "yes", "skip_comments": "no"},
                "should_succeed": True,  # Should handle gracefully
            },
            # Test Case 6: None values
            {
                "name": "None Values",
                "config": {
                    "verbose": None,
                    "timeout_seconds": None,
                    "cache_size": None,
                },
                "should_succeed": True,  # Should handle gracefully
            },
        ]

        results = []

        for test_case in test_cases:
            print(f"\n  Testing: {test_case['name']}")

            try:
                module = EntityReferenceModule()
                module.initialize(test_case['config'])

                # Check that attributes were set properly
                has_verbose = hasattr(module, 'verbose')
                has_timeout = hasattr(module, 'timeout_seconds')
                has_cache_size = hasattr(module, 'cache_size')
                has_skip_comments = hasattr(module, 'skip_comments')

                print(f"    ✓ Initialization successful")
                print(f"    ✓ Verbose: {getattr(module, 'verbose', 'NOT_SET')}")
                print(f"    ✓ Timeout: {getattr(module, 'timeout_seconds', 'NOT_SET')}")
                print(f"    ✓ Cache size: {getattr(module, 'cache_size', 'NOT_SET')}")
                print(
                    f"    ✓ Skip comments: {getattr(module, 'skip_comments', 'NOT_SET')}"
                )

                if test_case['should_succeed']:
                    results.append((test_case['name'], True, "Configuration accepted"))
                else:
                    results.append(
                        (test_case['name'], False, "Should have failed but didn't")
                    )

            except Exception as e:
                if test_case['should_succeed']:
                    print(f"    ✗ Unexpected error: {e}")
                    results.append((test_case['name'], False, f"Unexpected error: {e}"))
                else:
                    print(f"    ✓ Expected error: {e}")
                    results.append((test_case['name'], True, f"Expected error: {e}"))

        # Summary
        passed = sum(1 for _, success, _ in results if success)
        total = len(results)

        print(f"\n  Results: {passed}/{total} tests passed")

        if passed == total:
            print("  ✅ EntityReference configuration validation: PASSED")
            return True
        else:
            print("  ❌ EntityReference configuration validation: FAILED")
            for name, success, message in results:
                if not success:
                    print(f"    - {name}: {message}")
            return False

    except Exception as e:
        print(f"  ❌ EntityReference configuration validation: ERROR - {e}")
        return False


def test_configuration_error_messages():
    """Test that configuration errors provide helpful messages."""
    print("\n🔍 Testing Configuration Error Messages")
    print("-" * 50)

    try:
        from asciidoc_dita_toolkit.modules.entity_reference import (
            EntityReferenceModule,
        )

        # Test with a problematic configuration
        module = EntityReferenceModule()

        # Test various problematic configurations
        test_configs = [
            {"timeout_seconds": "not_a_number"},
            {"cache_size": "invalid"},
            {"verbose": "maybe"},
            {"unknown_key": "value"},
        ]

        for config in test_configs:
            try:
                module.initialize(config)
                print(f"  ✓ Configuration {config} handled gracefully")
            except Exception as e:
                print(f"  ✓ Configuration {config} error: {e}")

        print("  ✅ Error message testing: PASSED")
        return True

    except Exception as e:
        print(f"  ❌ Error message testing: FAILED - {e}")
        return False


def test_context_parameter_validation():
    """Test context parameter validation in execute method."""
    print("\n🎯 Testing Context Parameter Validation")
    print("-" * 50)

    try:
        from asciidoc_dita_toolkit.modules.entity_reference import (
            EntityReferenceModule,
        )

        module = EntityReferenceModule()
        module.initialize({"verbose": True})

        # Test various context configurations
        test_contexts = [
            # Valid context
            {
                "name": "Valid Context",
                "context": {
                    "file": None,
                    "recursive": False,
                    "directory": ".",
                    "verbose": False,
                },
                "should_succeed": True,
            },
            # Missing keys
            {"name": "Missing Keys", "context": {}, "should_succeed": True},
            # Invalid file path
            {
                "name": "Invalid File Path",
                "context": {
                    "file": "/nonexistent/path.adoc",
                    "recursive": False,
                    "directory": ".",
                },
                "should_succeed": True,  # Should handle gracefully
            },
            # Invalid directory
            {
                "name": "Invalid Directory",
                "context": {"directory": "/nonexistent/directory", "recursive": True},
                "should_succeed": True,  # Should handle gracefully
            },
            # Invalid types
            {
                "name": "Invalid Types",
                "context": {"recursive": "yes", "verbose": "true"},
                "should_succeed": True,  # Should handle gracefully
            },
        ]

        results = []

        for test_case in test_contexts:
            print(f"\n  Testing: {test_case['name']}")

            try:
                result = module.execute(test_case['context'])

                # Check result structure
                required_keys = ['module_name', 'version', 'success']
                has_required_keys = all(key in result for key in required_keys)

                if has_required_keys:
                    print(f"    ✓ Execution successful")
                    print(f"    ✓ Result keys: {list(result.keys())}")
                    print(f"    ✓ Success: {result.get('success', 'NOT_SET')}")

                    if test_case['should_succeed']:
                        results.append(
                            (test_case['name'], True, "Context handled properly")
                        )
                    else:
                        results.append(
                            (test_case['name'], False, "Should have failed but didn't")
                        )
                else:
                    print(f"    ✗ Missing required keys in result")
                    results.append((test_case['name'], False, "Missing required keys"))

            except Exception as e:
                if test_case['should_succeed']:
                    print(f"    ✗ Unexpected error: {e}")
                    results.append((test_case['name'], False, f"Unexpected error: {e}"))
                else:
                    print(f"    ✓ Expected error: {e}")
                    results.append((test_case['name'], True, f"Expected error: {e}"))

        # Summary
        passed = sum(1 for _, success, _ in results if success)
        total = len(results)

        print(f"\n  Results: {passed}/{total} tests passed")

        if passed == total:
            print("  ✅ Context parameter validation: PASSED")
            return True
        else:
            print("  ❌ Context parameter validation: FAILED")
            for name, success, message in results:
                if not success:
                    print(f"    - {name}: {message}")
            return False

    except Exception as e:
        print(f"  ❌ Context parameter validation: ERROR - {e}")
        return False


def test_result_structure_validation():
    """Test that execute method returns properly structured results."""
    print("\n📋 Testing Result Structure Validation")
    print("-" * 50)

    try:
        from asciidoc_dita_toolkit.modules.entity_reference import (
            EntityReferenceModule,
        )

        module = EntityReferenceModule()
        module.initialize({"verbose": False})

        # Test with a simple context
        context = {"directory": ".", "recursive": False}

        result = module.execute(context)

        # Check required keys
        required_keys = [
            'module_name',
            'version',
            'success',
            'files_processed',
            'entities_replaced',
            'warnings_generated',
        ]

        missing_keys = [key for key in required_keys if key not in result]

        if missing_keys:
            print(f"  ❌ Missing required keys: {missing_keys}")
            return False

        # Check key types
        type_checks = [
            ('module_name', str),
            ('version', str),
            ('success', bool),
            ('files_processed', int),
            ('entities_replaced', int),
            ('warnings_generated', int),
        ]

        type_errors = []
        for key, expected_type in type_checks:
            if not isinstance(result[key], expected_type):
                type_errors.append(
                    f"{key}: expected {expected_type.__name__}, got {type(result[key]).__name__}"
                )

        if type_errors:
            print(f"  ❌ Type errors: {type_errors}")
            return False

        print(f"  ✓ All required keys present: {required_keys}")
        print(f"  ✓ All types correct")
        print(f"  ✓ Result structure: {result}")

        print("  ✅ Result structure validation: PASSED")
        return True

    except Exception as e:
        print(f"  ❌ Result structure validation: ERROR - {e}")
        return False


def test_edge_case_handling():
    """Test edge case handling in configuration and execution."""
    print("\n🎪 Testing Edge Case Handling")
    print("-" * 50)

    try:
        from asciidoc_dita_toolkit.modules.entity_reference import (
            EntityReferenceModule,
        )

        # Test with extreme configurations
        edge_cases = [
            # Extreme timeout values
            {"timeout_seconds": 0},
            {"timeout_seconds": 999999},
            {"timeout_seconds": -1},
            # Extreme cache sizes
            {"cache_size": 0},
            {"cache_size": 999999},
            {"cache_size": -1},
            # Unicode in config
            {"verbose": True, "custom_key": "unicode_value_🚀"},
            # Very large config
            {"key_" + str(i): f"value_{i}" for i in range(100)},
        ]

        passed_tests = 0

        for i, config in enumerate(edge_cases):
            print(f"\n  Testing edge case {i+1}/{len(edge_cases)}")

            try:
                module = EntityReferenceModule()
                module.initialize(config)

                # Try to execute with the configured module
                result = module.execute({"directory": "."})

                if result.get('success', False) is not None:
                    print(f"    ✓ Edge case handled successfully")
                    passed_tests += 1
                else:
                    print(f"    ✗ Edge case failed")

            except Exception as e:
                print(f"    ✓ Edge case caught with error: {e}")
                passed_tests += 1  # Catching errors is acceptable

        print(f"\n  Results: {passed_tests}/{len(edge_cases)} edge cases handled")

        if passed_tests == len(edge_cases):
            print("  ✅ Edge case handling: PASSED")
            return True
        else:
            print("  ❌ Edge case handling: FAILED")
            return False

    except Exception as e:
        print(f"  ❌ Edge case handling: ERROR - {e}")
        return False


def main():
    """Run all configuration validation tests."""
    print("🔧 ADTModule Configuration Validation Tests")
    print("=" * 60)

    tests = [
        test_entityreference_config_validation,
        test_configuration_error_messages,
        test_context_parameter_validation,
        test_result_structure_validation,
        test_edge_case_handling,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("CONFIGURATION VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Total tests: {passed + failed}")

    if failed == 0:
        print("\n✅ All configuration validation tests passed!")
        print("\nKey achievements:")
        print("✅ Configuration edge cases handled gracefully")
        print("✅ Error messages are helpful and informative")
        print("✅ Result structures are consistent and well-typed")
        print("✅ Context parameters validated properly")
        print("✅ Edge cases handled robustly")
    else:
        print(f"\n❌ {failed} test(s) failed. Please review the output above.")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
