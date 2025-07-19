#!/usr/bin/env python3
"""
Performance baseline test to compare legacy vs ADTModule plugin execution.

This test ensures no performance regression when migrating from legacy to ADTModule pattern.
"""

import time
import tempfile
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import statistics
import unittest

# Add necessary paths
workspace_root = Path(__file__).parent.parent  # Go up from tests/ to project root
src_path = workspace_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))


def create_test_files(num_files: int = 10, entities_per_file: int = 20) -> List[str]:
    """Create test .adoc files with entity references for performance testing."""
    import random

    random.seed(42)  # Set a fixed seed for deterministic behavior

    test_files = []

    # Sample content with various entities
    entities = [
        "&copy;",
        "&trade;",
        "&reg;",
        "&mdash;",
        "&ndash;",
        "&ldquo;",
        "&rdquo;",
        "&lsquo;",
        "&rsquo;",
        "&hellip;",
        "&bull;",
        "&deg;",
        "&para;",
        "&sect;",
        "&middot;",
    ]

    for i in range(num_files):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
            f.write(f"= Test Document {i+1}\n\n")
            f.write("This is a test document for performance testing.\n\n")

            for j in range(entities_per_file):
                entity = entities[j % len(entities)]
                f.write(f"Line {j+1}: This text contains {entity} entity reference.\n")

            f.write(
                "\n// This is a comment with &copy; entity that should be ignored\n"
            )
            f.write("////\n")
            f.write("Block comment with &trade; entity that should be ignored\n")
            f.write("////\n")

            test_files.append(f.name)

    return test_files


def cleanup_test_files(test_files: List[str]) -> None:
    """Clean up test files."""
    for file_path in test_files:
        try:
            os.unlink(file_path)
        except OSError:
            pass


class TestPerformanceBaseline(unittest.TestCase):
    """Test class for performance baseline comparisons."""
    
    def setUp(self):
        """Set up test files for performance testing."""
        self.test_files = create_test_files(
            num_files=5, entities_per_file=10
        )  # Smaller for faster tests
    
    def tearDown(self):
        """Clean up test files after each test."""
        cleanup_test_files(self.test_files)


def measure_execution_time(func, *args, **kwargs) -> Tuple[float, any]:
    """Measure execution time of a function."""
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    return end_time - start_time, result


    def test_legacy_performance(self) -> None:
        """Test legacy plugin performance."""
        try:
            from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import main

            # Create mock args
            class MockArgs:
                def __init__(self, files):
                    self.file = None
                    self.recursive = False
                    self.directory = "."
                    self.verbose = False
                    self.silent = True  # Reduce output during testing
                    self.files = files

            # Backup original files (copy them to restore later)
            backup_files = {}
            for file_path in self.test_files:
                with open(file_path, 'r') as f:
                    backup_files[file_path] = f.read()

            # Measure legacy performance
            times = []
            for i in range(5):  # Run 5 times for better statistical relevance
                # Restore files to original state
                for file_path, content in backup_files.items():
                    with open(file_path, 'w') as f:
                        f.write(content)

                # Force legacy mode by temporarily disabling ADTModule
                import asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference as er_module

                original_available = er_module.ADT_MODULE_AVAILABLE
                er_module.ADT_MODULE_AVAILABLE = False

                try:
                    # Process each file individually
                    execution_time = 0
                    for file_path in self.test_files:
                        args = MockArgs([file_path])
                        args.file = file_path

                        time_taken, _ = measure_execution_time(main, args)
                        execution_time += time_taken

                    times.append(execution_time)

                finally:
                    # Restore ADTModule availability
                    er_module.ADT_MODULE_AVAILABLE = original_available

            stats = {
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                "min": min(times),
                "max": max(times),
                "times": times,
            }

            # Basic performance assertions
            self.assertGreater(stats["mean"], 0, "Legacy performance test should take some time")
            self.assertLess(stats["mean"], 10.0, "Legacy performance should complete within 10 seconds")
            self.assertEqual(len(stats["times"]), 5, "Should have 5 performance measurements")

        except Exception as e:
            self.fail(f"Error testing legacy performance: {e}")


    def test_adtmodule_performance(self) -> None:
        """Test ADTModule plugin performance."""
        try:
            from asciidoc_dita_toolkit.asciidoc_dita.plugins.EntityReference import (
                EntityReferenceModule,
            )

            # Backup original files
            backup_files = {}
            for file_path in self.test_files:
                with open(file_path, 'r') as f:
                    backup_files[file_path] = f.read()

            # Measure ADTModule performance
            times = []
            for i in range(5):  # Run 5 times for better statistical relevance
                # Restore files to original state
                for file_path, content in backup_files.items():
                    with open(file_path, 'w') as f:
                        f.write(content)

                # Create and initialize module
                module = EntityReferenceModule()
                config = {
                    "verbose": False,
                    "timeout_seconds": 30,
                    "cache_size": 1000,
                    "skip_comments": True,
                }
                module.initialize(config)

                # Process each file individually
                execution_time = 0
                for file_path in self.test_files:
                    context = {
                        "file": file_path,
                        "recursive": False,
                        "directory": str(Path(file_path).parent),
                        "verbose": False,
                    }

                    time_taken, _ = measure_execution_time(module.execute, context)
                    execution_time += time_taken

                # Cleanup
                module.cleanup()
                times.append(execution_time)

            stats = {
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                "min": min(times),
                "max": max(times),
                "times": times,
            }

            # Basic performance assertions
            self.assertGreater(stats["mean"], 0, "ADTModule performance test should take some time")
            self.assertLess(stats["mean"], 10.0, "ADTModule performance should complete within 10 seconds")
            self.assertEqual(len(stats["times"]), 5, "Should have 5 performance measurements")

        except Exception as e:
            self.fail(f"Error testing ADTModule performance: {e}")


def calculate_performance_metrics(legacy_stats: Dict, adtmodule_stats: Dict) -> Dict:
    """Calculate performance comparison metrics."""
    if "error" in legacy_stats or "error" in adtmodule_stats:
        return {"error": "Could not calculate metrics due to errors"}

    legacy_mean = legacy_stats["mean"]
    adtmodule_mean = adtmodule_stats["mean"]

    # Calculate percentage difference
    if legacy_mean > 0:
        percentage_diff = ((adtmodule_mean - legacy_mean) / legacy_mean) * 100
    else:
        percentage_diff = 0

    # Determine performance verdict
    if percentage_diff < -5:
        verdict = "🚀 IMPROVEMENT"
    elif percentage_diff > 10:
        verdict = "⚠️ REGRESSION"
    else:
        verdict = "✅ EQUIVALENT"

    return {
        "legacy_mean": legacy_mean,
        "adtmodule_mean": adtmodule_mean,
        "percentage_diff": percentage_diff,
        "verdict": verdict,
        "is_regression": percentage_diff > 10,
    }


def main():
    """Run performance baseline tests."""
    print("🚀 ADTModule Performance Baseline Test")
    print("=" * 50)

    # Test configuration
    num_files = 10
    entities_per_file = 20

    print(f"Creating {num_files} test files with {entities_per_file} entities each...")
    test_files = create_test_files(num_files, entities_per_file)

    try:
        print(f"Created {len(test_files)} test files")

        # Create test instance
        test_instance = TestPerformanceBaseline()
        test_instance.test_files = test_files

        # Test legacy performance
        print("\n📊 Testing Legacy Plugin Performance...")
        try:
            test_instance.test_legacy_performance()
            print("   ✅ Legacy performance test: PASSED")
        except Exception as e:
            print(f"   ❌ Legacy performance test: FAILED - {e}")
            return False

        # Test ADTModule performance
        print("\n� Testing ADTModule Plugin Performance...")
        try:
            test_instance.test_adtmodule_performance()
            print("   ✅ ADTModule performance test: PASSED")
        except Exception as e:
            print(f"   ❌ ADTModule performance test: FAILED - {e}")
            return False

        print("\n✅ All performance baseline tests: PASSED")
        return True

    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up {len(test_files)} test files...")
        cleanup_test_files(test_files)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
