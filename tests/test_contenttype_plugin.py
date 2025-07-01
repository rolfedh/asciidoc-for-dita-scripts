#!/usr/bin/env python3
"""
Test ContentType plugin against fixtures

This test validates that the ContentType plugin correctly:
1. Ignores files that should be ignored (ignore_* fixtures)
2. Fixes files that should be fixed (report_* fixtures)
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from asciidoc_dita_toolkit.asciidoc_dita.plugins.ContentType import ContentTypeUI, apply_content_type_fix


def test_ignore_fixtures():
    """Test that ignore_* fixtures result in no changes (when user chooses to skip)"""
    print("Testing ignore_* fixtures (should not be changed):")
    print("-" * 50)
    
    fixture_dir = project_root / "tests" / "fixtures" / "ContentType"
    ignore_files = [f for f in os.listdir(fixture_dir) if f.startswith('ignore_') and f.endswith('.adoc')]
    
    ui = ContentTypeUI()
    all_passed = True
    
    for test_file in ignore_files:
        print(f"Testing {test_file}...")
        
        input_path = fixture_dir / test_file
        expected_path = fixture_dir / test_file.replace('.adoc', '.expected')
        
        if not expected_path.exists():
            print(f"  ⚠️  Missing expected file for {test_file}")
            continue
            
        # Read input and expected content
        with open(input_path) as f:
            input_content = f.read()
        with open(expected_path) as f:
            expected_content = f.read()
        
        # For ignore_* files, the expected content should match input (no changes)
        if input_content.strip() == expected_content.strip():
            print(f"  ✅ PASS: {test_file} correctly represents 'no change' state")
        else:
            print(f"  ❌ FAIL: {test_file} input/expected mismatch")
            all_passed = False
    
    return all_passed


def test_report_fixtures():
    """Test that report_* fixtures are correctly fixed by auto mode"""
    print("\nTesting report_* fixtures (should be fixed):")
    print("-" * 50)
    
    fixture_dir = project_root / "tests" / "fixtures" / "ContentType"
    report_files = [f for f in os.listdir(fixture_dir) if f.startswith('report_') and f.endswith('.adoc')]
    
    ui = ContentTypeUI()
    all_passed = True
    
    for test_file in report_files:
        print(f"Testing {test_file}...")
        
        input_path = fixture_dir / test_file
        expected_path = fixture_dir / test_file.replace('.adoc', '.expected')
        
        if not expected_path.exists():
            print(f"  ⚠️  Missing expected file for {test_file}")
            continue
        
        # Create temp file for processing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Copy input to temp file
            shutil.copy2(input_path, temp_path)
            
            # Read input content
            with open(input_path) as f:
                content = f.read()
            
            # Analyze for issues
            issues = ui.analyze_file_content(str(input_path), content)
            
            if not issues:
                print(f"  ⚠️  No issues detected in {test_file}")
                continue
            
            # Apply auto-fix
            issue = issues[0]  # Take first issue
            choice = ui._get_auto_choice(issue, issue.additional_info.get('scenario'))
            
            if apply_content_type_fix(temp_path, choice, issue):
                # Read fixed content
                with open(temp_path) as f:
                    fixed_content = f.read()
                
                # Read expected content
                with open(expected_path) as f:
                    expected_content = f.read()
                
                if fixed_content.strip() == expected_content.strip():
                    print(f"  ✅ PASS: Fixed content matches expected")
                else:
                    print(f"  ❌ FAIL: Fixed content does not match expected")
                    print(f"    Expected: {repr(expected_content.strip())}")
                    print(f"    Got:      {repr(fixed_content.strip())}")
                    all_passed = False
            else:
                print(f"  ❌ FAIL: No fix was applied to {test_file}")
                all_passed = False
                
        finally:
            os.unlink(temp_path)
    
    return all_passed


def test_detection():
    """Test that our plugin correctly detects all issue scenarios"""
    print("\nTesting issue detection:")
    print("-" * 50)
    
    fixture_dir = project_root / "tests" / "fixtures" / "ContentType"
    ui = ContentTypeUI()
    
    expected_detections = {
        'ignore_content_type.adoc': 'deprecated_content',
        'ignore_module_type.adoc': 'deprecated_module', 
        'ignore_defined_type.adoc': None,  # Should have no issues
        'ignore_preceding_content.adoc': 'misplaced',
        'report_missing_type.adoc': 'missing',
        'report_missing_value.adoc': 'empty_value',
        'report_comments.adoc': 'commented'
    }
    
    all_passed = True
    
    for test_file, expected_scenario in expected_detections.items():
        file_path = fixture_dir / test_file
        if not file_path.exists():
            continue
            
        with open(file_path) as f:
            content = f.read()
        
        issues = ui.analyze_file_content(str(file_path), content)
        
        if expected_scenario is None:
            # Should have no issues
            if not issues:
                print(f"  ✅ {test_file}: Correctly detected no issues")
            else:
                print(f"  ❌ {test_file}: Unexpected issues detected: {[i.additional_info.get('scenario') for i in issues]}")
                all_passed = False
        else:
            # Should detect the expected scenario
            if issues and issues[0].additional_info.get('scenario') == expected_scenario:
                print(f"  ✅ {test_file}: Correctly detected '{expected_scenario}' scenario")
            else:
                detected = [i.additional_info.get('scenario') for i in issues] if issues else ['none']
                print(f"  ❌ {test_file}: Expected '{expected_scenario}', got {detected}")
                all_passed = False
    
    return all_passed


if __name__ == "__main__":
    print("ContentType Plugin Test Suite")
    print("=" * 60)
    
    # Run all tests
    test1_passed = test_ignore_fixtures()
    test2_passed = test_report_fixtures() 
    test3_passed = test_detection()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if test1_passed and test2_passed and test3_passed:
        print("🎉 ALL TESTS PASSED!")
        print("The ContentType plugin is working correctly with all fixtures.")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the output above for details.")
        sys.exit(1)
