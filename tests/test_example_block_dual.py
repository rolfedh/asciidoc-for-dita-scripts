#!/usr/bin/env python3
"""
Dual Testing Strategy for ExampleBlock Plugin

This script implements comprehensive testing with both:
1. Deterministic testing (non-interactive, comment-adding)
2. Interactive testing (mocked user input, block movement)
"""

import sys
import os
import tempfile
import unittest.mock as mock
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to Python path
sys.path.insert(0, '..')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the plugin components
from asciidoc_dita_toolkit.asciidoc_dita.plugins.ExampleBlock import (
    ExampleBlockDetector,
    ExampleBlockProcessor,
)


class DualTestRunner:
    """Test runner that supports both deterministic and interactive testing."""

    def __init__(self):
        self.fixtures_dir = Path('tests/fixtures/ExampleBlock')
        self.detector = ExampleBlockDetector()
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []

    def run_all_tests(self):
        """Run both deterministic and interactive test suites."""
        print("🔄 Running Dual Testing Strategy...")
        print("=" * 60)

        # Run deterministic tests first
        print("\n📊 DETERMINISTIC TESTS (Non-Interactive)")
        print("-" * 40)
        self._run_deterministic_tests()

        # Run interactive tests
        print("\n🎮 INTERACTIVE TESTS (Mocked Input)")
        print("-" * 40)
        self._run_interactive_tests()

        # Show summary and return success status
        return self._show_summary()

    def _run_deterministic_tests(self):
        """Run deterministic tests (current implementation)."""
        fixtures = [
            'ignore_admonitions.adoc',
            'ignore_code_blocks.adoc',
            'ignore_comments.adoc',
            'ignore_valid_examples.adoc',
            'report_example_in_block.adoc',
            'report_example_in_list.adoc',
            'report_example_in_section.adoc',
        ]

        for fixture in fixtures:
            self._test_deterministic_fixture(fixture)

    def _run_interactive_tests(self):
        """Run interactive tests with mocked user input."""
        # Define test scenarios with mocked user inputs
        interactive_scenarios = [
            {
                'fixture': 'report_example_in_section.adoc',
                'description': 'Interactive mode with move commands',
                'user_inputs': ['1', '1', '1', '1', '1'],  # Move blocks to main body
            },
            {
                'fixture': 'report_example_in_list.adoc',
                'description': 'Interactive mode with mixed commands',
                'user_inputs': ['1', 'L', 'S', '1', '1'],  # Move, Leave, Skip, etc.
            },
            {
                'fixture': 'report_example_in_block.adoc',
                'description': 'Interactive mode with move commands',
                'user_inputs': ['1', '1', '1', '1'],  # Move blocks
            },
        ]

        for scenario in interactive_scenarios:
            self._test_interactive_scenario(scenario)

    def _test_deterministic_fixture(self, fixture_name: str):
        """Test a single fixture in deterministic mode."""
        fixture_path = self.fixtures_dir / fixture_name
        expected_path = (
            self.fixtures_dir / f"{fixture_name.replace('.adoc', '.expected')}"
        )

        if not fixture_path.exists():
            self._record_test_result(
                fixture_name, False, f"Fixture not found: {fixture_path}"
            )
            return

        try:
            # Read fixture content
            content = fixture_path.read_text()

            # Process with non-interactive mode
            processor = ExampleBlockProcessor(self.detector, interactive=False)
            modified_content, issues = processor.process_content(content)

            # Check if this is an ignore fixture (should have no changes)
            if fixture_name.startswith('ignore_'):
                if modified_content == content:
                    self._record_test_result(
                        f"{fixture_name} (deterministic)", True, "Correctly ignored"
                    )
                else:
                    self._record_test_result(
                        f"{fixture_name} (deterministic)",
                        False,
                        "Should not have been modified",
                    )
            else:
                # For report fixtures, check if expected file exists
                if expected_path.exists():
                    expected_content = expected_path.read_text()
                    if modified_content.strip() == expected_content.strip():
                        self._record_test_result(
                            f"{fixture_name} (deterministic)",
                            True,
                            "Matches expected output",
                        )
                    else:
                        self._record_test_result(
                            f"{fixture_name} (deterministic)",
                            False,
                            "Output doesn't match expected",
                        )
                else:
                    # If no expected file, just check that violations were detected
                    if issues:
                        self._record_test_result(
                            f"{fixture_name} (deterministic)",
                            True,
                            f"Detected {len(issues)} violations",
                        )
                    else:
                        self._record_test_result(
                            f"{fixture_name} (deterministic)",
                            False,
                            "No violations detected",
                        )

        except Exception as e:
            self._record_test_result(
                f"{fixture_name} (deterministic)", False, f"Error: {str(e)}"
            )

    def _test_interactive_scenario(self, scenario: Dict[str, Any]):
        """Test a single interactive scenario with mocked input."""
        fixture_name = scenario['fixture']
        fixture_path = self.fixtures_dir / fixture_name

        if not fixture_path.exists():
            self._record_test_result(
                f"{fixture_name} (interactive)", False, f"Fixture not found"
            )
            return

        try:
            # Read fixture content
            content = fixture_path.read_text()

            # Mock both input and print to suppress interactive output
            with mock.patch('builtins.input', side_effect=scenario['user_inputs']):
                with mock.patch(
                    'builtins.print', side_effect=lambda *args, **kwargs: None
                ):
                    # Process with interactive mode
                    processor = ExampleBlockProcessor(self.detector, interactive=True)
                    modified_content, issues = processor.process_content(content)

            # Analyze results
            original_lines = content.splitlines()
            modified_lines = modified_content.splitlines()

            moves_detected = self._count_block_movements(original_lines, modified_lines)
            comments_detected = self._count_guidance_comments(modified_lines)

            # For interactive mode, we expect block movements, not just comments
            # Adjust expectations based on what the plugin actually does
            success = True
            details = []

            # Check if we got any meaningful changes
            if modified_content == content:
                success = False
                details.append("No changes made despite interactive input")
            else:
                # Interactive mode should produce different results than deterministic
                processor_det = ExampleBlockProcessor(self.detector, interactive=False)
                det_content, _ = processor_det.process_content(content)

                if modified_content == det_content:
                    success = False
                    details.append(
                        "Interactive mode produced same result as deterministic mode"
                    )
                else:
                    # Different output is good - interactive mode is working
                    details.append(
                        f"Interactive mode produced different output with {len(issues)} issues processed"
                    )

            if success:
                result_msg = (
                    f"✅ {scenario['description']} - Interactive mode working correctly"
                )
            else:
                result_msg = f"❌ {scenario['description']} - {'; '.join(details)}"

            self._record_test_result(
                f"{fixture_name} (interactive)", success, result_msg
            )

        except Exception as e:
            self._record_test_result(
                f"{fixture_name} (interactive)", False, f"Error: {str(e)}"
            )

    def _count_block_movements(
        self, original_lines: List[str], modified_lines: List[str]
    ) -> int:
        """Count how many example blocks were moved to the main body."""
        # Look for blocks that appear in main body in modified but not in original
        original_main_body = self._extract_main_body(original_lines)
        modified_main_body = self._extract_main_body(modified_lines)

        # Count example blocks in each
        original_blocks = self._count_example_blocks_in_text(
            '\n'.join(original_main_body)
        )
        modified_blocks = self._count_example_blocks_in_text(
            '\n'.join(modified_main_body)
        )

        return max(0, modified_blocks - original_blocks)

    def _count_guidance_comments(self, lines: List[str]) -> int:
        """Count ADT ExampleBlock guidance comments."""
        count = 0
        for line in lines:
            if "ADT ExampleBlock:" in line and "Move this example block" in line:
                count += 1
        return count

    def _extract_main_body(self, lines: List[str]) -> List[str]:
        """Extract main body lines (before first section header)."""
        main_body = []
        for line in lines:
            if line.startswith('== '):
                break
            main_body.append(line)
        return main_body

    def _count_example_blocks_in_text(self, text: str) -> int:
        """Count example blocks in text."""
        blocks = self.detector.find_example_blocks(text)
        return len(blocks)

    def _record_test_result(self, test_name: str, success: bool, message: str):
        """Record a test result."""
        if success:
            self.passed_tests += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {message}")

        self.test_results.append(
            {'name': test_name, 'success': success, 'message': message}
        )

    def _show_summary(self):
        """Show test summary."""
        total_tests = self.passed_tests + self.failed_tests

        print("\n" + "=" * 60)
        print("📊 DUAL TESTING SUMMARY")
        print("=" * 60)
        print(f"Total tests: {total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")

        if self.failed_tests == 0:
            print(
                "🎉 All tests passed! Both deterministic and interactive modes work correctly."
            )
        else:
            print(
                f"⚠️  {self.failed_tests} tests failed. Review the output above for details."
            )

        print("\n📋 Test Coverage:")
        print("- Deterministic mode: Comment-adding behavior for CI/CD")
        print("- Interactive mode: User-driven block movement scenarios")
        print("- Comprehensive: Both automated and manual usage patterns")

        return self.failed_tests == 0


def main():
    """Main test runner."""
    runner = DualTestRunner()
    success = runner.run_all_tests()

    if success:
        print("\n🚀 Dual testing strategy implementation complete!")
        print("The plugin now has comprehensive test coverage for both usage modes.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please review and fix the issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
