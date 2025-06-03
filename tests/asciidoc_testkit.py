"""
Reusable test utilities for AsciiDoc plugin/processing scripts.

Provides functions for fixture discovery and test running, to be imported by all plugin test scripts.
"""
import os
import difflib

def get_fixture_pairs(fixture_dir, input_ext='.adoc', expected_ext='.expected', warn_missing=True):
    """
    Yield (input_path, expected_path) pairs for all input_ext files with expected_ext counterparts.
    If warn_missing is True, print a warning for each input file missing an expected file.
    """
    if not os.path.isdir(fixture_dir):
        print(f"Warning: Fixture directory does not exist: {fixture_dir}")
        return
    for fname in os.listdir(fixture_dir):
        if fname.endswith(input_ext):
            base = fname[: -len(input_ext)]
            expected = base + expected_ext
            expected_path = os.path.join(fixture_dir, expected)
            input_path = os.path.join(fixture_dir, fname)
            if os.path.exists(expected_path):
                yield input_path, expected_path
            elif warn_missing:
                print(f"Warning: Missing {fname[:-len(input_ext)] + expected_ext} file.")

def run_linewise_test(input_path, expected_path, transform_func):
    """
    Run a linewise test: apply transform_func to each line of input_path and compare to expected_path.
    Returns True if output matches expected, False otherwise. Prints a diff on failure.
    """
    with open(input_path, encoding='utf-8') as f:
        input_lines = f.readlines()
    with open(expected_path, encoding='utf-8') as f:
        expected_lines = f.readlines()
    output_lines = [transform_func(line) for line in input_lines]
    if output_lines != expected_lines:
        print(f"Test failed for {os.path.basename(input_path)}:")
        diff = difflib.unified_diff(expected_lines, output_lines, fromfile='expected', tofile='actual')
        print(''.join(diff))
        return False
    return True
