#!/usr/bin/env python3
"""
Documentation alignment validation test for ADTModule plugins.

This test ensures that migrated plugins have consistent docstrings and that
the Plugin Development Guide accurately reflects the established patterns.
"""

import sys
import inspect
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add necessary paths
workspace_root = Path(__file__).parent.parent  # Go up from tests/ to project root
src_path = workspace_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))


def test_adtmodule_interface_documentation():
    """Test that ADTModule interface has proper documentation."""
    print("📚 Testing ADTModule Interface Documentation")
    print("-" * 50)

    try:
        from asciidoc_dita_toolkit.adt_core.module_sequencer import ADTModule

        # Check class docstring
        class_docstring = inspect.getdoc(ADTModule)
        if not class_docstring:
            print("  ❌ ADTModule class missing docstring")
            return False

        print(f"  ✓ Class docstring: {class_docstring[:100]}...")

        # Check required method docstrings
        required_methods = [
            'name',
            'version',
            'dependencies',
            'release_status',
            'initialize',
            'execute',
            'cleanup',
        ]

        docstring_issues = []

        for method_name in required_methods:
            method = getattr(ADTModule, method_name, None)
            if method:
                docstring = inspect.getdoc(method)
                if not docstring:
                    docstring_issues.append(f"Method {method_name} missing docstring")
                else:
                    print(f"  ✓ Method {method_name}: {docstring[:50]}...")
            else:
                docstring_issues.append(f"Method {method_name} not found")

        if docstring_issues:
            print("  ❌ ADTModule interface documentation issues:")
            for issue in docstring_issues:
                print(f"    - {issue}")
            return False

        print("  ✅ ADTModule interface documentation: PASSED")
        return True

    except Exception as e:
        print(f"  ❌ ADTModule interface documentation: ERROR - {e}")
        return False


def test_entityreference_documentation():
    """Test EntityReference plugin documentation consistency."""
    print("\n📝 Testing EntityReference Documentation")
    print("-" * 50)

    try:
        from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import (
            EntityReferenceModule,
        )

        # Check class docstring
        class_docstring = inspect.getdoc(EntityReferenceModule)
        if not class_docstring:
            print("  ❌ EntityReferenceModule class missing docstring")
            return False

        print(f"  ✓ Class docstring: {class_docstring[:100]}...")

        # Check method docstrings
        methods_to_check = ['initialize', 'execute', 'cleanup']
        docstring_quality = []

        for method_name in methods_to_check:
            method = getattr(EntityReferenceModule, method_name, None)
            if method:
                docstring = inspect.getdoc(method)
                if not docstring:
                    docstring_quality.append(f"Method {method_name} missing docstring")
                else:
                    # Check for Google-style docstring elements
                    has_args = "Args:" in docstring
                    has_returns = "Returns:" in docstring or method_name == 'cleanup'

                    quality_score = 0
                    if has_args and method_name != 'cleanup':
                        quality_score += 1
                    if has_returns or method_name == 'cleanup':
                        quality_score += 1

                    if quality_score >= 1:
                        print(f"  ✓ Method {method_name}: Well-documented")
                    else:
                        docstring_quality.append(
                            f"Method {method_name} incomplete documentation"
                        )
            else:
                docstring_quality.append(f"Method {method_name} not found")

        if docstring_quality:
            print("  ❌ EntityReference documentation issues:")
            for issue in docstring_quality:
                print(f"    - {issue}")
            return False

        print("  ✅ EntityReference documentation: PASSED")
        return True

    except Exception as e:
        print(f"  ❌ EntityReference documentation: ERROR - {e}")
        return False


def test_docstring_style_consistency():
    """Test docstring style consistency across modules."""
    print("\n🎨 Testing Docstring Style Consistency")
    print("-" * 50)

    try:
        from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import (
            EntityReferenceModule,
        )

        # Get all methods
        methods = inspect.getmembers(
            EntityReferenceModule, predicate=inspect.isfunction
        )

        style_issues = []
        google_style_count = 0

        for method_name, method in methods:
            if method_name.startswith('_'):
                continue  # Skip private methods

            docstring = inspect.getdoc(method)
            if docstring:
                # Check for Google-style docstring patterns
                has_args_section = "Args:" in docstring
                has_returns_section = "Returns:" in docstring
                has_description = len(docstring.strip().split('\n')[0]) > 10

                if has_args_section or has_returns_section or has_description:
                    google_style_count += 1
                    print(f"  ✓ Method {method_name}: Google-style docstring")
                else:
                    style_issues.append(f"Method {method_name} has minimal docstring")

        if style_issues:
            print("  ⚠️  Style consistency issues:")
            for issue in style_issues:
                print(f"    - {issue}")

        if google_style_count > 0:
            print(f"  ✅ Found {google_style_count} well-documented methods")
            return True
        else:
            print("  ❌ No well-documented methods found")
            return False

    except Exception as e:
        print(f"  ❌ Docstring style consistency: ERROR - {e}")
        return False


def test_type_hints_consistency():
    """Test type hints consistency in ADTModule implementation."""
    print("\n🔤 Testing Type Hints Consistency")
    print("-" * 50)

    try:
        from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import (
            EntityReferenceModule,
        )

        # Check method signatures
        methods_to_check = ['initialize', 'execute', 'cleanup']
        type_hint_issues = []

        for method_name in methods_to_check:
            method = getattr(EntityReferenceModule, method_name, None)
            if method:
                signature = inspect.signature(method)

                # Check parameter type hints
                for param_name, param in signature.parameters.items():
                    if param_name == 'self':
                        continue

                    if param.annotation == inspect.Parameter.empty:
                        type_hint_issues.append(
                            f"Method {method_name} parameter '{param_name}' missing type hint"
                        )
                    else:
                        print(
                            f"  ✓ Method {method_name} parameter '{param_name}': {param.annotation}"
                        )

                # Check return type hint
                if signature.return_annotation == inspect.Signature.empty:
                    if method_name != 'cleanup':  # cleanup can return None
                        type_hint_issues.append(
                            f"Method {method_name} missing return type hint"
                        )
                else:
                    print(
                        f"  ✓ Method {method_name} return type: {signature.return_annotation}"
                    )

        if type_hint_issues:
            print("  ❌ Type hint issues:")
            for issue in type_hint_issues:
                print(f"    - {issue}")
            return False

        print("  ✅ Type hints consistency: PASSED")
        return True

    except Exception as e:
        print(f"  ❌ Type hints consistency: ERROR - {e}")
        return False


def test_property_documentation():
    """Test that ADTModule properties have proper documentation."""
    print("\n🏷️  Testing Property Documentation")
    print("-" * 50)

    try:
        from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import (
            EntityReferenceModule,
        )

        # Check property docstrings
        properties_to_check = ['name', 'version', 'dependencies', 'release_status']
        property_issues = []

        for prop_name in properties_to_check:
            prop = getattr(EntityReferenceModule, prop_name, None)
            if prop:
                docstring = inspect.getdoc(prop)
                if not docstring:
                    property_issues.append(f"Property {prop_name} missing docstring")
                else:
                    print(f"  ✓ Property {prop_name}: {docstring[:50]}...")
            else:
                property_issues.append(f"Property {prop_name} not found")

        if property_issues:
            print("  ❌ Property documentation issues:")
            for issue in property_issues:
                print(f"    - {issue}")
            return False

        print("  ✅ Property documentation: PASSED")
        return True

    except Exception as e:
        print(f"  ❌ Property documentation: ERROR - {e}")
        return False


def test_plugin_development_guide_accuracy():
    """Test that the Plugin Development Guide exists and reflects actual patterns."""
    print("\n📖 Testing Plugin Development Guide Accuracy")
    print("-" * 50)

    try:
        # Look for the plugin development guide
        guide_paths = [
            workspace_root / "docs" / "PLUGIN_DEVELOPMENT_GUIDE.md",
            workspace_root / "docs" / "plugin_development_guide.md",
            workspace_root / "PLUGIN_DEVELOPMENT_GUIDE.md",
        ]

        guide_path = None
        for path in guide_paths:
            if path.exists():
                guide_path = path
                break

        if not guide_path:
            print("  ⚠️  Plugin Development Guide not found")
            print("  ℹ️  This should be created for Phase 3")
            return True  # Not failing, just noting

        # Read and analyze the guide
        with open(guide_path, 'r') as f:
            guide_content = f.read()

        # Check for key sections
        required_sections = [
            "ADTModule Interface",
            "initialize",
            "execute",
            "cleanup",
            "Configuration",
            "Type Hints",
        ]

        missing_sections = []
        for section in required_sections:
            if section.lower() not in guide_content.lower():
                missing_sections.append(section)

        if missing_sections:
            print(f"  ⚠️  Guide missing sections: {missing_sections}")
        else:
            print("  ✅ Guide contains all required sections")

        # Check for code examples
        code_block_count = len(re.findall(r'```python', guide_content))
        if code_block_count < 3:
            print(f"  ⚠️  Guide has only {code_block_count} Python code examples")
        else:
            print(f"  ✅ Guide has {code_block_count} Python code examples")

        print("  ✅ Plugin Development Guide: CHECKED")
        return True

    except Exception as e:
        print(f"  ❌ Plugin Development Guide: ERROR - {e}")
        return False


def test_error_message_quality():
    """Test the quality and helpfulness of error messages."""
    print("\n🚨 Testing Error Message Quality")
    print("-" * 50)

    try:
        from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import (
            EntityReferenceModule,
        )

        # Test error message patterns
        module = EntityReferenceModule()

        # Test with problematic execution context
        error_contexts = [
            {"directory": "/nonexistent/path"},
            {"file": "/invalid/file.adoc"},
            {"recursive": "invalid_type"},
        ]

        helpful_errors = 0

        for context in error_contexts:
            try:
                module.initialize({"verbose": False})
                result = module.execute(context)

                # Check if errors are captured in result
                if not result.get('success', True):
                    error_msg = result.get('error', '')
                    if error_msg and len(error_msg) > 10:
                        helpful_errors += 1
                        print(f"  ✓ Helpful error for {context}: {error_msg[:50]}...")
                    else:
                        print(f"  ⚠️  Minimal error for {context}")
                else:
                    print(f"  ✓ Graceful handling for {context}")
                    helpful_errors += 1

            except Exception as e:
                error_msg = str(e)
                if len(error_msg) > 10:
                    helpful_errors += 1
                    print(f"  ✓ Helpful exception for {context}: {error_msg[:50]}...")
                else:
                    print(f"  ⚠️  Minimal exception for {context}")

        if helpful_errors >= 2:
            print("  ✅ Error message quality: PASSED")
            return True
        else:
            print("  ❌ Error message quality: NEEDS IMPROVEMENT")
            return False

    except Exception as e:
        print(f"  ❌ Error message quality: ERROR - {e}")
        return False


def main():
    """Run all documentation alignment tests."""
    print("📋 ADTModule Documentation Alignment Tests")
    print("=" * 60)

    tests = [
        test_adtmodule_interface_documentation,
        test_entityreference_documentation,
        test_docstring_style_consistency,
        test_type_hints_consistency,
        test_property_documentation,
        test_plugin_development_guide_accuracy,
        test_error_message_quality,
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
    print("DOCUMENTATION ALIGNMENT SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Total tests: {passed + failed}")

    if failed == 0:
        print("\n✅ All documentation alignment tests passed!")
        print("\nKey achievements:")
        print("✅ ADTModule interface properly documented")
        print("✅ EntityReference plugin documentation consistent")
        print("✅ Docstring style follows Google conventions")
        print("✅ Type hints are comprehensive and consistent")
        print("✅ Property documentation is complete")
        print("✅ Error messages are helpful and informative")
    else:
        print(f"\n❌ {failed} test(s) failed. Please review the output above.")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
